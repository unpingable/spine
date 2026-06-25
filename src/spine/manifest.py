# SPDX-License-Identifier: Apache-2.0
"""provisional_git_manifest_v0 — the deliberately ugly ingress bridge.

The name smells temporary on purpose. **Final architecture: Spine reads from
Continuity.** This adapter exists only because Continuity does not yet custody
the live doctrine; it reads a *declared* manifest of git-backed file references
and is **incapable of crawling** — there is no discovery code, and a manifest
that asks the adapter to discover (a glob, a directory, a recurse flag) is
refused, not executed. Retire this module when Continuity becomes the source.

Refusals propagate as typed ``SpineRefusal`` subclasses (not raw pydantic
``ValidationError``) so the read plane fails clean and loud.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from . import refusal
from .refusal import CrawlAttemptError, MalformedManifestError

# Path shapes that mean "go find things" rather than "here is one thing".
_CRAWL_MARKERS = ("*", "?", "[", "]", "{", "}")


class ManifestArtifact(BaseModel):
    """One declared artifact reference. Pure structure; the crawl fence and
    adapter check run in :func:`load_manifest` so they raise typed refusals
    un-wrapped."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    repo: str
    path: str
    reported_status: str
    status_source_ref: str | None = None
    witness_ref: str | None = None

    @property
    def canonical_location(self) -> str:
        return f"{self.repo}:{self.path}"


class Manifest(BaseModel):
    """A declared manifest. ``extra='forbid'`` refuses crawl-shaped top-level
    keys (e.g. ``recurse: true``) at parse time."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adapter: str
    artifacts: tuple[ManifestArtifact, ...]


def _check_no_crawl(path: str) -> None:
    """Refuse a path that asks the adapter to discover rather than reference."""
    if not path or not path.strip():
        raise CrawlAttemptError("artifact path is empty")
    if path.endswith("/"):
        raise CrawlAttemptError(
            f"path {path!r} is a directory; the provisional adapter indexes "
            "concrete files, it does not crawl directories"
        )
    if any(m in path for m in _CRAWL_MARKERS):
        raise CrawlAttemptError(
            f"path {path!r} contains a glob/discovery marker; the provisional "
            "adapter is incapable of crawling — declare concrete files"
        )


def load_manifest(path: str | Path) -> Manifest:
    """Load and validate a YAML manifest. No discovery, no filesystem walk.

    Every failure is a typed ``SpineRefusal``: a structurally-invalid manifest →
    ``MalformedManifestError``; an unknown adapter → ``UnknownIngressError``; a
    crawl-shaped artifact path → ``CrawlAttemptError``.
    """
    raw = yaml.safe_load(Path(path).read_text())
    if not isinstance(raw, dict):
        raise MalformedManifestError("manifest must be a mapping")
    try:
        manifest = Manifest.model_validate(raw)
    except ValidationError as exc:
        raise MalformedManifestError(str(exc)) from exc

    if manifest.adapter not in refusal.KNOWN_INGRESS_ADAPTERS:
        raise refusal.UnknownIngressError(
            f"adapter {manifest.adapter!r} not in "
            f"{sorted(refusal.KNOWN_INGRESS_ADAPTERS)}"
        )
    for art in manifest.artifacts:
        _check_no_crawl(art.path)
    return manifest
