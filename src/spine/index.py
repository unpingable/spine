# SPDX-License-Identifier: Apache-2.0
"""The index entry and the deterministic index builder.

An ``IndexEntry`` is a **mutable navigational record** — located and rendered,
nothing more. The pydantic model gives structure + a publishable schema; the
read-plane wall (``refusal.check_entry_admissible``) is enforced by the
``build_entry`` factory so callers get clean typed refusals.
"""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, ConfigDict, Field

from . import refusal
from .refusal import LOCATED, RENDERED


class IndexEntry(BaseModel):
    """One navigable record. ``spine_assertions`` is boring on purpose — only
    ``located`` / ``rendered``. ``reported_status`` is a quotation of
    ``status_source_ref``, never Spine's own word. ``entry_digest`` is computed
    over the content, so an entry cannot lie about its own digest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_location: str
    reported_status: str
    status_source_ref: str | None = None
    witness_ref: str | None = None
    ingress_adapter: str = refusal.INGRESS_PROVISIONAL_GIT
    observed_at: str
    spine_assertions: tuple[str, ...] = Field(default=(LOCATED, RENDERED))

    @property
    def entry_digest(self) -> str:
        """Content hash over the entry's meaningful fields. Deterministic;
        excludes itself. ``observed_at`` is included so a re-observation at a
        different time is a different entry."""
        body = json.dumps(
            {
                "canonical_location": self.canonical_location,
                "reported_status": self.reported_status,
                "status_source_ref": self.status_source_ref,
                "witness_ref": self.witness_ref,
                "ingress_adapter": self.ingress_adapter,
                "observed_at": self.observed_at,
                "spine_assertions": list(self.spine_assertions),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(body).hexdigest()

    @property
    def is_navigational_only(self) -> bool:
        """True iff Spine asserts only navigation (the wall holds for this entry)."""
        return set(self.spine_assertions).issubset({LOCATED, RENDERED})


def build_entry(
    *,
    canonical_location: str,
    reported_status: str,
    observed_at: str,
    status_source_ref: str | None = None,
    witness_ref: str | None = None,
    ingress_adapter: str = refusal.INGRESS_PROVISIONAL_GIT,
    spine_assertions: tuple[str, ...] = (LOCATED, RENDERED),
) -> IndexEntry:
    """Build a wall-checked ``IndexEntry`` or raise a typed ``SpineRefusal``.

    The semantic wall runs FIRST (typed errors), then the structural model is
    constructed. This is the blessed construction path; it is the only way the
    repo mints an entry.
    """
    refusal.check_entry_admissible(
        canonical_location=canonical_location,
        reported_status=reported_status,
        status_source_ref=status_source_ref,
        witness_ref=witness_ref,
        ingress_adapter=ingress_adapter,
        spine_assertions=spine_assertions,
    )
    return IndexEntry(
        canonical_location=canonical_location,
        reported_status=reported_status,
        status_source_ref=status_source_ref,
        witness_ref=witness_ref,
        ingress_adapter=ingress_adapter,
        observed_at=observed_at,
        spine_assertions=spine_assertions,
    )


class SpineIndex(BaseModel):
    """A deterministic, navigable index built from a manifest. Order is stable
    (sorted by canonical_location), so the same manifest at the same
    ``observed_at`` yields a byte-identical index."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ingress_adapter: str
    observed_at: str
    entries: tuple[IndexEntry, ...]

    @property
    def index_digest(self) -> str:
        body = json.dumps(
            {
                "ingress_adapter": self.ingress_adapter,
                "observed_at": self.observed_at,
                "entries": [e.entry_digest for e in self.entries],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(body).hexdigest()


def build_index(manifest, *, observed_at: str) -> SpineIndex:
    """Build a deterministic ``SpineIndex`` from a loaded ``Manifest``.

    Each manifest artifact becomes a wall-checked entry; a violating artifact
    raises a typed ``SpineRefusal`` and the whole build fails closed (no partial
    index). Entries are sorted by canonical_location for determinism.
    """
    entries = [
        build_entry(
            canonical_location=art.canonical_location,
            reported_status=art.reported_status,
            status_source_ref=art.status_source_ref,
            witness_ref=art.witness_ref,
            ingress_adapter=manifest.adapter,
            observed_at=observed_at,
        )
        for art in manifest.artifacts
    ]
    entries.sort(key=lambda e: e.canonical_location)
    return SpineIndex(
        ingress_adapter=manifest.adapter,
        observed_at=observed_at,
        entries=tuple(entries),
    )
