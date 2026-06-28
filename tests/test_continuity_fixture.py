# SPDX-License-Identifier: Apache-2.0
"""The Continuity-shaped fixture contract: the envelope, never the verdict.

> Continuity may shape the envelope. Continuity may not supply the verdict.

Slice 2b proves a Continuity-shaped static export can declare refs into Spine through
`DeclarationSource` without adding assertion vocabulary or succession semantics.
Continuity's lifecycle (status / reliance_class / supersedes) is quarantined as quoted
metadata; foreign authority words (canonical / ratified / authority …) are rejected;
every declared ref lands as `unknown` — Continuity declares location, not standing.

No live Continuity: no `continuity` import, no subprocess. The fixture is a static
file committed under Spine.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from spine import (
    ContinuityExportFixtureSource,
    ContinuityShapeError,
    DeclarationSource,
    DeclaredManifest,
    ForeignAuthorityFieldError,
    build_edition,
    build_index,
    render_markdown,
)
from spine.refusal import LOCATED, RENDERED

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "continuity_export_shape_v0.json"
_OBSERVED = "2026-06-28T00:00:00Z"


def _declared():
    return ContinuityExportFixtureSource(_FIXTURE).declare()


def _write_fixture(tmp_path, records):
    p = tmp_path / "export.json"
    p.write_text(json.dumps(records, indent=2))
    return p


# --- it is a real DeclarationSource over the grounded fixture ---------------- #


def test_fixture_source_satisfies_the_interface():
    assert isinstance(ContinuityExportFixtureSource(_FIXTURE), DeclarationSource)


def test_declare_emits_a_declared_manifest_with_continuity_source_kind():
    declared = _declared()
    assert isinstance(declared, DeclaredManifest)
    assert declared.provenance.source_kind == "continuity_export_fixture_v0"
    assert declared.provenance.export_digest.startswith("sha256:")
    # three records in the committed fixture -> three declared refs
    assert len(declared.manifest.artifacts) == 3
    locs = {a.canonical_location for a in declared.manifest.artifacts}
    assert "spine:DOCTRINE.md" in locs
    assert "continuity:docs/candidates/PROJECTION_RECEIPT.md" in locs


# --- the core doctrine: Continuity declares LOCATION, not STATUS ------------- #


def test_every_declared_ref_lands_as_unknown_status():
    """Continuity confers no governing status — even a `committed`, `actionable`
    memory declares an `unknown` ref. The lifecycle does not become a Spine verdict."""
    declared = _declared()
    assert all(a.reported_status == "unknown" for a in declared.manifest.artifacts)


def test_continuity_lifecycle_is_quarantined_as_quoted_metadata():
    """status / reliance_class / supersedes survive ONLY as a visibly-labelled
    quotation in status_source_ref — verbatim, never normalized into a Spine claim."""
    declared = _declared()
    by_loc = {a.canonical_location: a for a in declared.manifest.artifacts}

    committed = by_loc["spine:DOCTRINE.md"]
    assert "status=committed" in committed.status_source_ref
    assert "reliance_class=advisory" in committed.status_source_ref
    assert "NOT Spine standing" in committed.status_source_ref
    # ...but the entry itself reports unknown, not committed/advisory.
    assert committed.reported_status == "unknown"


def test_highest_reliance_class_still_confers_nothing():
    """reliance_class: actionable is the strongest Continuity reliance — it is
    quarantined, never mapped to Spine standing."""
    declared = _declared()
    actionable = next(
        a for a in declared.manifest.artifacts
        if a.canonical_location == "continuity:docs/candidates/PROJECTION_RECEIPT.md"
    )
    assert "reliance_class=actionable" in actionable.status_source_ref
    assert actionable.reported_status == "unknown"


def test_real_supersedes_field_is_quarantined_not_rejected():
    """`supersedes` IS a genuine Continuity field, so it is preserved as quoted
    metadata (not rejected as foreign), and it does NOT become Spine succession."""
    declared = _declared()
    superseding = next(
        a for a in declared.manifest.artifacts
        if a.canonical_location == "continuity:docs/candidates/PROJECTION_RECEIPT.md"
    )
    assert "supersedes=mem_00000000000000000000000000000000" in superseding.status_source_ref
    assert superseding.reported_status == "unknown"
    assert superseding.witness_ref is None


# --- the throat is transparent: full pipeline runs --------------------------- #


def test_index_render_path_runs_from_the_fixture():
    declared = _declared()
    index = build_index(declared.manifest, observed_at=_OBSERVED)
    assert len(index.entries) == 3
    for e in index.entries:
        assert e.spine_assertions == (LOCATED, RENDERED)
    md = render_markdown(index)
    assert "`spine:DOCTRINE.md`" in md
    # every entry is unwitnessed — the read plane shows that loudly
    assert "NONE — unwitnessed" in md


def test_edition_path_runs_from_a_continuity_declared_manifest(tmp_path):
    """The declared manifest mints an Edition through the untouched build_edition
    (dump the declared manifest to YAML — the 2c content-build seam stays deferred)."""
    declared = _declared()
    manifest_yaml = tmp_path / "declared.yaml"
    manifest_yaml.write_text(yaml.safe_dump(declared.manifest.model_dump(mode="json")))
    build = build_edition(manifest_yaml, created_at=_OBSERVED, manifest_ref="continuity-fixture")
    assert build.edition.spine_assertions == (LOCATED, RENDERED)
    frozen = json.loads(build.files["index.json"])
    assert all(e["reported_status"] == "unknown" for e in frozen["entries"])


# --- THE NASTY TEST: foreign authority fields are rejected ------------------- #


@pytest.mark.parametrize("field", ["canonical", "ratified", "authority", "latest", "current"])
def test_foreign_authority_field_in_content_is_rejected(tmp_path, field):
    """A field real Continuity never emits, smuggled into a record, is refused —
    not mapped, not quarantined. (supersedes is the deliberate non-member: tested
    above as quarantined.)"""
    records = json.loads(_FIXTURE.read_text())
    poisoned = copy.deepcopy(records[0])
    poisoned["payload"]["content"][field] = True
    path = _write_fixture(tmp_path, [poisoned])
    with pytest.raises(ForeignAuthorityFieldError):
        ContinuityExportFixtureSource(path).declare()


def test_foreign_authority_field_at_top_level_is_rejected(tmp_path):
    records = json.loads(_FIXTURE.read_text())
    poisoned = copy.deepcopy(records[0])
    poisoned["authoritative"] = True
    path = _write_fixture(tmp_path, [poisoned])
    with pytest.raises(ForeignAuthorityFieldError):
        ContinuityExportFixtureSource(path).declare()


def test_prose_value_naming_an_authority_word_is_not_a_hit(tmp_path):
    """The guard scans KEYS, not values — a summary that mentions 'the canonical
    doc' is prose, not a field, and must not trip the wall."""
    records = json.loads(_FIXTURE.read_text())
    ok = copy.deepcopy(records[0])
    ok["payload"]["content"]["summary"] = "widely treated as the canonical charter"
    path = _write_fixture(tmp_path, [ok])
    declared = ContinuityExportFixtureSource(path).declare()  # does not raise
    assert declared.manifest.artifacts[0].reported_status == "unknown"


# --- malformed declarations fail clean and loud ------------------------------ #


def test_record_without_locatable_ref_is_refused(tmp_path):
    records = json.loads(_FIXTURE.read_text())
    broken = copy.deepcopy(records[0])
    broken["payload"]["content"] = {"summary": "no repo or path here"}
    path = _write_fixture(tmp_path, [broken])
    with pytest.raises(ContinuityShapeError):
        ContinuityExportFixtureSource(path).declare()


def test_non_continuity_envelope_is_refused(tmp_path):
    path = _write_fixture(tmp_path, [{"envelope": "something.else.v1", "payload": {}}])
    with pytest.raises(ContinuityShapeError):
        ContinuityExportFixtureSource(path).declare()


def test_crawl_shaped_declared_path_is_refused(tmp_path):
    """Defense in depth: a Continuity-declared glob path still hits the manifest
    crawl fence downstream — the adapter is no more capable of crawling than any
    other source."""
    from spine import CrawlAttemptError

    records = json.loads(_FIXTURE.read_text())
    crawly = copy.deepcopy(records[0])
    crawly["payload"]["content"]["path"] = "docs/*.md"
    path = _write_fixture(tmp_path, [crawly])
    with pytest.raises(CrawlAttemptError):
        ContinuityExportFixtureSource(path).declare()


# --- the dog stays outside: no live Continuity dependency -------------------- #


def test_adapter_does_not_import_continuity():
    """Mechanical guard against the live-dependency regression: the module must not
    import the continuity package or shell out to it. AST-based so the module's own
    docstring (which says 'no subprocess') is not a false hit — only real imports."""
    import ast

    import spine.continuity_fixture as mod

    tree = ast.parse(Path(mod.__file__).read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "continuity" not in imported
    assert "subprocess" not in imported
