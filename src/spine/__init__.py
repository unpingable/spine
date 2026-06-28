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
from .edition_diff import (
    ChangedRef,
    EditionDiff,
    EntryRef,
    diff_editions,
    load_edition,
    render_edition_diff,
)
from .index import IndexEntry, SpineIndex, build_entry, build_index
from .manifest import Manifest, ManifestArtifact, load_manifest
from .continuity_fixture import (
    ContinuityExportFixtureSource,
    ContinuityShapeError,
    ForeignAuthorityFieldError,
)
from .source import (
    DeclarationSource,
    DeclaredManifest,
    ProvisionalGitManifestSource,
    SourceProvenance,
)
from .refusal import (
    LOCATED,
    RENDERED,
    SPINE_ASSERTIONS,
    SUCCESSION_FRAMING,
    CrawlAttemptError,
    EditionExistsError,
    EditionLoadError,
    EditionSuccessionError,
    SpineBearsStatusError,
    SpineRefusal,
    UnsourcedStatusError,
    UnwitnessedGovernedClaimError,
    check_entry_admissible,
    check_no_succession_framing,
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
    "DeclarationSource",
    "DeclaredManifest",
    "SourceProvenance",
    "ProvisionalGitManifestSource",
    "ContinuityExportFixtureSource",
    "ContinuityShapeError",
    "ForeignAuthorityFieldError",
    "render_markdown",
    "Edition",
    "EditionBuild",
    "BuildProvenance",
    "build_edition",
    "write_edition",
    "edition_dir_for",
    "EditionDiff",
    "EntryRef",
    "ChangedRef",
    "load_edition",
    "diff_editions",
    "render_edition_diff",
    "check_entry_admissible",
    "check_spine_assertions",
    "check_no_succession_framing",
    "SPINE_ASSERTIONS",
    "SUCCESSION_FRAMING",
    "LOCATED",
    "RENDERED",
    "SpineRefusal",
    "SpineBearsStatusError",
    "UnsourcedStatusError",
    "UnwitnessedGovernedClaimError",
    "CrawlAttemptError",
    "EditionExistsError",
    "EditionLoadError",
    "EditionSuccessionError",
]
