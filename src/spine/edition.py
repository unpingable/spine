# SPDX-License-Identifier: Apache-2.0
"""The Edition — an immutable, content-addressed snapshot of a render.

> Freezing an index preserves what was found; it does not promote what was found.

An Edition freezes what Spine *located* — the declared manifest, the deterministic
:class:`~spine.index.SpineIndex`, and the rendered view — into a stable, citable
package. It adds **immutability + citability**, never authority.
``spine_assertions`` on an Edition is the same boring pair an index entry carries,
``located`` / ``rendered``: an Edition that ever held a legitimacy verb would be
the read-plane wall falling at the *package* layer.

Determinism is the whole point of a citation target: the same manifest bytes at
the same ``created_at`` produce identical digests, an identical ``edition_id``,
and a byte-identical edition directory. ``created_at`` is supplied (never read
from the clock) and is threaded through as the index's ``observed_at`` so there
is exactly one timestamp to pin.

The ``edition_id`` is a content hash over the citation-target fields only
(``created_at`` + the three digests + ingress adapter + assertions) — **not** over
the build provenance. Two builds of the same located content at the same
``created_at`` share a citation target even if *how* they were built differs;
provenance documents reproduction, it does not fork identity.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from . import refusal
from .index import build_index
from .manifest import load_manifest
from .refusal import LOCATED, RENDERED, EditionExistsError, SpineRefusal
from .render import render_markdown

# An edition_id is a sha256 content hash and nothing else — the directory key is
# derived from it, so the shape is validated before it ever touches a path.
_EDITION_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

try:  # tool identity for provenance; stable within a checkout.
    from importlib.metadata import version as _pkg_version

    _TOOL_VERSION = _pkg_version("spine")
except Exception:  # pragma: no cover - only on a broken/uninstalled checkout
    _TOOL_VERSION = "0+unknown"

# File names inside an immutable edition directory. Flat and boring on purpose.
EDITION_FILENAME = "edition.json"
MANIFEST_FILENAME = "manifest.yaml"
INDEX_FILENAME = "index.json"
RENDER_FILENAME = "index.md"


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _edition_id_over(
    *,
    created_at: str,
    ingress_adapter: str,
    manifest_digest: str,
    index_digest: str,
    render_digest: str,
    spine_assertions: tuple[str, ...],
) -> str:
    """The citation target: a content hash over the located content + time, and
    the (boring) assertions. Excludes build provenance by design.

    Assertions are canonicalized (sorted, de-duplicated) so the citation target
    is invariant to representation — ``("located","rendered")`` and
    ``("rendered","located")`` are the same set and must mint the same id."""
    body = json.dumps(
        {
            "created_at": created_at,
            "ingress_adapter": ingress_adapter,
            "manifest_digest": manifest_digest,
            "index_digest": index_digest,
            "render_digest": render_digest,
            "spine_assertions": sorted(set(spine_assertions)),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256(body)


class BuildProvenance(BaseModel):
    """How to reproduce this Edition from repo state. Recorded metadata, *not*
    part of the ``edition_id`` — see the module docstring."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool: str = "spine"
    tool_version: str
    ingress_adapter: str
    manifest_ref: str  # the manifest path as declared to the build
    created_at: str
    reproduce: str  # the exact command that rebuilds it


class Edition(BaseModel):
    """An immutable, content-addressed snapshot of a Spine render.

    The fields are the citation target plus the build provenance. ``spine_assertions``
    is the same humiliating pair as an index entry — freezing adds no authority.
    Minted only via :func:`build_edition` (the blessed path runs the assertions
    wall before construction, so a legitimacy verb is refused with a typed
    ``SpineBearsStatusError`` rather than smuggled into a package)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    edition_id: str
    created_at: str
    ingress_adapter: str
    manifest_digest: str
    index_digest: str
    render_digest: str
    build_provenance: BuildProvenance
    spine_assertions: tuple[str, ...] = Field(default=(LOCATED, RENDERED))

    @model_validator(mode="after")
    def _wall_holds_at_the_package_layer(self) -> Edition:
        """Defense in depth: the wall runs at construction too, so even a *direct*
        ``Edition(spine_assertions=("ratified", ...))`` that bypasses
        :func:`build_edition` cannot mint an object that asserts legitimacy. (The
        blessed factory checks first and raises the clean typed
        ``SpineBearsStatusError``; this is the seam that catches everything else.)
        """
        refusal.check_spine_assertions(self.spine_assertions)
        return self

    @property
    def is_navigational_only(self) -> bool:
        """True iff the Edition asserts only navigation (the wall holds at the
        package layer)."""
        return set(self.spine_assertions).issubset({LOCATED, RENDERED})


@dataclass(frozen=True)
class EditionBuild:
    """The product of :func:`build_edition`: the :class:`Edition` metadata plus
    the exact bytes of every file the immutable directory contains. Pure — no
    filesystem writes. ``files`` maps relative filename -> bytes; the same inputs
    at the same ``created_at`` yield byte-identical ``files`` and ``edition``."""

    edition: Edition
    files: dict[str, bytes]


def build_edition(
    manifest_path: str | Path,
    *,
    created_at: str,
    manifest_ref: str | None = None,
    spine_assertions: tuple[str, ...] = (LOCATED, RENDERED),
) -> EditionBuild:
    """Freeze a manifest into an immutable Edition build (pure; no IO writes).

    The Slice 1 wall carries through unchanged: every entry inside the frozen
    index still asserts only ``located`` / ``rendered``, still quotes its
    ``reported_status`` from a source, still marks unwitnessed material loudly —
    :func:`spine.index.build_index` enforces it. This adds only immutability +
    citability on top.

    ``created_at`` is the supplied packaging time and is threaded through as the
    index's ``observed_at`` (one timestamp to pin). ``manifest_ref`` records how
    the manifest was referenced for provenance; it defaults to ``manifest_path``.
    ``spine_assertions`` exists so the package-layer wall is exercisable — a
    legitimacy verb here raises a typed ``SpineBearsStatusError`` *before* any
    Edition is constructed.
    """
    # The wall, first — typed refusal escapes un-wrapped (the blessed path).
    refusal.check_spine_assertions(spine_assertions)
    # Canonicalize so the stored value and the citation target agree and are
    # invariant to ordering / duplication (the boring pair, always).
    assertions = tuple(sorted(set(spine_assertions)))

    ref = manifest_ref if manifest_ref is not None else str(manifest_path)

    # Read the manifest bytes ONCE: the digest/frozen copy and the parsed index
    # must describe the same bytes (no second read that could see a changed file).
    manifest_bytes = Path(manifest_path).read_bytes()
    manifest = load_manifest(manifest_path, content=manifest_bytes.decode("utf-8"))
    index = build_index(manifest, observed_at=created_at)
    render_md = render_markdown(index)

    manifest_digest = _sha256(manifest_bytes)
    index_bytes = (index.model_dump_json(indent=2) + "\n").encode("utf-8")
    render_bytes = render_md.encode("utf-8")
    render_digest = _sha256(render_bytes)

    provenance = BuildProvenance(
        tool="spine",
        tool_version=_TOOL_VERSION,
        ingress_adapter=manifest.adapter,
        manifest_ref=ref,
        created_at=created_at,
        reproduce=f"spine edition create {ref} --created-at {created_at} --out <editions-root>",
    )

    edition = Edition(
        edition_id=_edition_id_over(
            created_at=created_at,
            ingress_adapter=manifest.adapter,
            manifest_digest=manifest_digest,
            index_digest=index.index_digest,
            render_digest=render_digest,
            spine_assertions=assertions,
        ),
        created_at=created_at,
        ingress_adapter=manifest.adapter,
        manifest_digest=manifest_digest,
        index_digest=index.index_digest,
        render_digest=render_digest,
        build_provenance=provenance,
        spine_assertions=assertions,
    )

    files = {
        MANIFEST_FILENAME: manifest_bytes,
        INDEX_FILENAME: index_bytes,
        RENDER_FILENAME: render_bytes,
        EDITION_FILENAME: (edition.model_dump_json(indent=2) + "\n").encode("utf-8"),
    }
    return EditionBuild(edition=edition, files=files)


def edition_dir_for(out_root: str | Path, edition_id: str) -> Path:
    """The immutable directory an Edition is written to: ``<out_root>/<hex>``,
    keyed by the content-addressed ``edition_id`` (which already incorporates
    ``created_at``). Same content + same time -> same directory.

    The id shape is validated (``sha256:`` + 64 hex) before it touches a path, so
    a malformed or hostile id (e.g. ``sha256:../escape``) is refused rather than
    resolving to a directory outside ``out_root``."""
    if not _EDITION_ID_RE.match(edition_id):
        raise SpineRefusal(
            f"edition_id {edition_id!r} is not a sha256 content hash; refusing to "
            "derive a directory from a malformed id"
        )
    digest = edition_id.split(":", 1)[1]
    return Path(out_root) / digest


def write_edition(
    manifest_path: str | Path,
    *,
    created_at: str,
    out_root: str | Path,
    manifest_ref: str | None = None,
) -> tuple[Edition, Path]:
    """Build an Edition and write it to its own immutable directory under
    ``out_root``. Refuses (``EditionExistsError``) rather than overwrite an
    existing edition directory — immutability is the point.

    The write is atomic: files are staged in a temp directory and moved into
    place with a single rename, so a crash mid-write never leaves a half-written
    edition that future runs would refuse to repair as "already immutable".

    Returns the :class:`Edition` and the directory it was written to.
    """
    build = build_edition(manifest_path, created_at=created_at, manifest_ref=manifest_ref)
    root = Path(out_root)
    target = edition_dir_for(root, build.edition.edition_id)

    if target.exists():
        raise EditionExistsError(
            f"edition directory {target} already exists; an Edition is immutable "
            "and is never overwritten — delete it deliberately or pick another "
            "out-root if you really mean to re-mint it"
        )

    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".staging-edition-", dir=root))
    try:
        for name, data in build.files.items():
            (staging / name).write_bytes(data)
        # Atomic publish. os.replace onto a non-existent target is a rename; if a
        # concurrent minter won the race, the target is now a non-empty dir and
        # the rename fails — surfaced as the same immutability refusal.
        try:
            os.replace(staging, target)
        except OSError as exc:
            raise EditionExistsError(
                f"edition directory {target} appeared during write (concurrent "
                "mint); an Edition is immutable and is never overwritten"
            ) from exc
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return build.edition, target
