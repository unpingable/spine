# SPDX-License-Identifier: Apache-2.0
"""The declaration-source contract: declare candidates for location, confer no standing.

> A source declares candidates for location. It does not confer standing.

Slice 2a defines the *throat* — `DeclarationSource -> DeclaredManifest` — and proves
it against the manifest we already have. Two things must hold: the throat is
transparent (the Index/Edition pipeline consumes `declared.manifest` byte-identically
to `load_manifest`), and provenance can never masquerade as authority (the closed
`SourceProvenance` field set, and the wall that refuses a witnessless governed claim
no matter what the source declared).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spine import (
    DeclarationSource,
    DeclaredManifest,
    ProvisionalGitManifestSource,
    SourceProvenance,
    UnwitnessedGovernedClaimError,
    build_edition,
    build_index,
    load_manifest,
)
from spine.refusal import LOCATED, RENDERED

_SPECIMEN = Path(__file__).resolve().parents[1] / "specimens" / "predicate_witness_manifest.yaml"
_CORPUS = Path(__file__).resolve().parents[1] / "specimens" / "mixed_status_corpus.yaml"
_OBSERVED = "2026-06-28T00:00:00Z"


def test_provisional_source_satisfies_the_interface():
    src = ProvisionalGitManifestSource(_SPECIMEN)
    assert isinstance(src, DeclarationSource)  # runtime_checkable Protocol


# --- the throat is transparent: pipeline unchanged --------------------------- #


def test_declared_manifest_equals_load_manifest():
    """The source declares exactly the manifest load_manifest parses — wrapping it
    changes the refs not at all."""
    declared = ProvisionalGitManifestSource(_SPECIMEN).declare()
    assert isinstance(declared, DeclaredManifest)
    assert declared.manifest == load_manifest(_SPECIMEN)


def test_index_from_source_is_byte_identical_to_index_from_manifest():
    """build_index over the declared manifest is byte-identical to build_index over
    the directly-loaded manifest — the throat is downstream-transparent."""
    declared = ProvisionalGitManifestSource(_SPECIMEN).declare()
    via_source = build_index(declared.manifest, observed_at=_OBSERVED)
    via_load = build_index(load_manifest(_SPECIMEN), observed_at=_OBSERVED)
    assert via_source.model_dump_json() == via_load.model_dump_json()
    assert via_source.index_digest == via_load.index_digest


def test_edition_export_digest_matches_source_export_digest():
    """The source's export_digest (over declared bytes) equals the Edition's
    manifest_digest (over frozen bytes) — same bytes, one truth. The path-based
    Edition build is still exact because the provisional source wraps a file (the
    content-based build is the named 2c seam)."""
    declared = ProvisionalGitManifestSource(_SPECIMEN).declare()
    build = build_edition(_SPECIMEN, created_at=_OBSERVED, manifest_ref="specimen")
    assert declared.provenance.export_digest == build.edition.manifest_digest


def test_entries_still_assert_only_located_rendered():
    declared = ProvisionalGitManifestSource(_CORPUS).declare()
    index = build_index(declared.manifest, observed_at=_OBSERVED)
    for e in index.entries:
        assert e.spine_assertions == (LOCATED, RENDERED)


# --- provenance records origin, never authority ------------------------------ #


def test_provenance_records_kind_ref_and_digest():
    declared = ProvisionalGitManifestSource(_SPECIMEN, source_ref="specimen").declare()
    p = declared.provenance
    assert p.source_kind == "provisional_git_manifest_v0"
    assert p.source_ref == "specimen"
    assert p.export_digest.startswith("sha256:")
    assert p.declared_at is None


def test_source_provenance_field_set_is_closed_and_authority_free():
    """The closed field set IS the wall: provenance may record where a declaration
    came from, never that the refs are authoritative / current / ratified."""
    fields = set(SourceProvenance.model_fields)
    assert fields == {"source_kind", "source_ref", "export_digest", "declared_at"}
    forbidden = {
        "authority", "ratified", "current", "latest", "supersedes",
        "witness", "standing", "canonical", "recency", "trusted",
    }
    assert not (fields & forbidden)


def test_declared_manifest_carries_only_manifest_and_provenance():
    fields = set(DeclaredManifest.model_fields)
    assert fields == {"manifest", "provenance"}


# --- THE LOAD-BEARING TEST: a source confers no standing --------------------- #


def test_a_source_declaring_a_witnessless_ratified_ref_is_refused_at_index_build(tmp_path):
    """A source may DECLARE anything — including a `ratified` ref. But the entry
    wall fires at index-build regardless of what the source claimed: a governed
    claim without a witness is refused. "The source says ratified, therefore
    authoritative" is structurally impossible, not merely discouraged."""
    poisoned = {
        "adapter": "provisional_git_manifest_v0",
        "artifacts": [
            {
                "repo": "x",
                "path": "doc.md",
                "reported_status": "ratified",          # claims governed authority...
                "status_source_ref": "self:header ratified",
                "witness_ref": None,                    # ...with no witness
            }
        ],
    }
    mpath = tmp_path / "poisoned.yaml"
    mpath.write_text(yaml.safe_dump(poisoned))

    # The source declares it without complaint — declaring is not conferring.
    declared = ProvisionalGitManifestSource(mpath).declare()
    assert declared.manifest.artifacts[0].reported_status == "ratified"

    # But Spine refuses to build an index that would assert that standing.
    with pytest.raises(UnwitnessedGovernedClaimError):
        build_index(declared.manifest, observed_at=_OBSERVED)


def test_declare_reads_through_the_crawl_fence(tmp_path):
    """A source is still incapable of crawling: a glob-shaped declared path is
    refused at declare(), not executed."""
    from spine import CrawlAttemptError

    crawly = {
        "adapter": "provisional_git_manifest_v0",
        "artifacts": [{"repo": "x", "path": "docs/*.md", "reported_status": "unknown"}],
    }
    mpath = tmp_path / "crawly.yaml"
    mpath.write_text(yaml.safe_dump(crawly))
    with pytest.raises(CrawlAttemptError):
        ProvisionalGitManifestSource(mpath).declare()
