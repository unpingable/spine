# SPDX-License-Identifier: Apache-2.0
"""Spine — the read plane of the constellation.

> Findability is not legitimacy. Spine indexes status-bearing objects; it does
> not bear status.

Public surface: build a deterministic, navigable index from a declared manifest
(``provisional_git_manifest_v0``), render it so the refusal is visible, and
freeze it into an immutable, citable :class:`~spine.edition.Edition`. The wall
lives in :mod:`spine.refusal`.
"""

from __future__ import annotations

from .edition import (
    BuildProvenance,
    Edition,
    EditionBuild,
    build_edition,
    edition_dir_for,
    write_edition,
)
from .index import IndexEntry, SpineIndex, build_entry, build_index
from .manifest import Manifest, ManifestArtifact, load_manifest
from .refusal import (
    LOCATED,
    RENDERED,
    SPINE_ASSERTIONS,
    CrawlAttemptError,
    EditionExistsError,
    SpineBearsStatusError,
    SpineRefusal,
    UnsourcedStatusError,
    UnwitnessedGovernedClaimError,
    check_entry_admissible,
    check_spine_assertions,
)
from .render import render_markdown

__all__ = [
    "IndexEntry",
    "SpineIndex",
    "build_entry",
    "build_index",
    "Manifest",
    "ManifestArtifact",
    "load_manifest",
    "render_markdown",
    "Edition",
    "EditionBuild",
    "BuildProvenance",
    "build_edition",
    "write_edition",
    "edition_dir_for",
    "check_entry_admissible",
    "check_spine_assertions",
    "SPINE_ASSERTIONS",
    "LOCATED",
    "RENDERED",
    "SpineRefusal",
    "SpineBearsStatusError",
    "UnsourcedStatusError",
    "UnwitnessedGovernedClaimError",
    "CrawlAttemptError",
    "EditionExistsError",
]
