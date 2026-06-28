# SPDX-License-Identifier: Apache-2.0
"""The declaration source — the throat Spine breathes declarations through.

> A source declares candidates for location. It does not confer standing.

A :class:`DeclarationSource` answers exactly one question: *here are the refs Spine
should attempt to locate, and here is where that declaration came from.* It does
**not** answer which ref is authoritative, current, doctrine, or trustworthy —
:class:`SourceProvenance` has a closed field set with no authority/recency/
ratification field, and that closure is the wall.

This is the first move of the Continuity-as-source arc and deliberately **not**
Continuity: we define the interface here and wrap the manifest we already have
(:class:`ProvisionalGitManifestSource`). Continuity-shaped fixtures (2b) and a real
adapter (2c) breathe through this same throat later.

**The deep guarantee is structural, not promised.** A source may *declare* anything,
including a ``ratified`` ref. But every declared ref still flows through
:func:`spine.index.build_index` → :func:`spine.refusal.check_entry_admissible`, so a
witnessless governed claim is refused at index-build regardless of what the source
said. "The source declares it, therefore it is authoritative" is unrepresentable —
the source hands Spine candidates for *location*, never standing.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from .manifest import Manifest, load_manifest
from .refusal import INGRESS_PROVISIONAL_GIT


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class SourceProvenance(BaseModel):
    """Where a declaration came from — and *only* that.

    The field set is closed (``extra="forbid"``) and contains no authority, recency,
    ratification, or witness field. That closure is the wall: a source records its
    own identity and a content digest of what it declared; it can record nothing
    that would let provenance masquerade as standing.

    - ``source_kind`` — the source's own identity (e.g. the provisional adapter).
    - ``source_ref`` — how the declaration was referenced (a path, later an export id).
    - ``export_digest`` — sha256 over the exact declared bytes (tamper-evidence on
      the declaration, never a claim about the refs' truth).
    - ``declared_at`` — optional time the source says it declared this; descriptive,
      never read as recency/precedence by Spine.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_kind: str
    source_ref: str
    export_digest: str
    declared_at: str | None = None


class DeclaredManifest(BaseModel):
    """A declared manifest plus the provenance of its declaration. The ``manifest``
    is the same wall-checked :class:`~spine.manifest.Manifest` the rest of the
    pipeline already consumes — the throat changes nothing downstream."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest: Manifest
    provenance: SourceProvenance


@runtime_checkable
class DeclarationSource(Protocol):
    """The interface: something that can declare a manifest with provenance. One
    verb. A source declares candidates for location; everything about *what those
    refs mean* is decided downstream by the wall, never by the source."""

    def declare(self) -> DeclaredManifest:
        ...


class ProvisionalGitManifestSource:
    """The first, dull implementation: wrap the existing provisional git manifest.

    Reads the declared YAML once, parses it through :func:`load_manifest` (so the
    crawl fence + adapter check still apply), and records a content digest over the
    exact bytes it declared. No new external dependency, no Continuity — proof that
    the throat works against the manifest we already have."""

    source_kind = INGRESS_PROVISIONAL_GIT

    def __init__(self, manifest_path: str | Path, *, source_ref: str | None = None):
        self._path = Path(manifest_path)
        self._source_ref = source_ref if source_ref is not None else str(manifest_path)

    def declare(self) -> DeclaredManifest:
        # Read once: the digest and the parsed manifest describe the same bytes.
        raw = self._path.read_bytes()
        manifest = load_manifest(self._path, content=raw.decode("utf-8"))
        provenance = SourceProvenance(
            source_kind=self.source_kind,
            source_ref=self._source_ref,
            export_digest=_sha256(raw),
            declared_at=None,
        )
        return DeclaredManifest(manifest=manifest, provenance=provenance)
