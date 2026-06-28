# SPDX-License-Identifier: Apache-2.0
"""Slice 1c — corpus expansion as specimen intake.

> Corpus expansion increases surface area, not authority.

A larger, heterogeneous declared corpus (canonical-feeling charter, candidate
doctrine note, process artifact, working note, openly PARKED draft) must still
produce nothing but located/rendered entries. Inclusion, renderability, and
Edition membership are navigational facts — never status claims. The load-bearing
case is the museum label: an obsolete doc carried without being laundered into
"current".
"""

from __future__ import annotations

from pathlib import Path

from spine import build_edition, build_index, load_manifest, render_markdown
from spine.edition import INDEX_FILENAME
from spine.refusal import (
    AUTHORITATIVE_STATUSES,
    LEGITIMACY_VERBS,
    LOCATED,
    RENDERED,
    STATUS_UNKNOWN,
)

_CORPUS = Path(__file__).resolve().parents[1] / "specimens" / "mixed_status_corpus.yaml"
_GENESIS = Path(__file__).resolve().parents[1] / "specimens" / "predicate_witness_manifest.yaml"
_CREATED = "2026-06-27T00:00:00Z"

# Pinned so a refactor that silently moves Edition 2's citation target fails here.
_EDITION_2_ID = "sha256:b94f04428773ced08c2bd06e17ad9e892cc8eb1f67ad7c5a7f1b1f0d61589459"
_EDITION_1_ID = "sha256:fabb36a44c45ff3737c88fcd70d132899d768c8be1d99b33c3a765d1f8be8601"


def _index():
    return build_index(load_manifest(_CORPUS), observed_at=_CREATED)


# --- the larger corpus loads and stays navigational -------------------------- #


def test_mixed_corpus_builds_and_is_only_located_rendered():
    index = _index()
    assert len(index.entries) == 5
    for e in index.entries:
        assert e.spine_assertions == (LOCATED, RENDERED)
        assert e.is_navigational_only is True
        assert e.witness_ref is None  # nothing here has earned a witness


def test_no_entry_claims_governed_authority():
    """Surface area grew; authority did not. No entry reports a governed status
    (which would require a witness none of these have)."""
    for e in _index().entries:
        assert e.reported_status not in AUTHORITATIVE_STATUSES


def test_mixed_corpus_index_is_deterministic():
    a = build_index(load_manifest(_CORPUS), observed_at=_CREATED)
    b = build_index(load_manifest(_CORPUS), observed_at=_CREATED)
    assert a.index_digest == b.index_digest
    assert a.model_dump_json() == b.model_dump_json()


# --- importance is not authority --------------------------------------------- #


def test_canonical_feeling_charter_is_reported_unknown_not_assumed():
    """DOCTRINE.md is the read plane's own charter — foundational, yet it declares
    no quotable status, so Spine reports `unknown` and quotes no source. It does
    NOT promote 'important-looking' into a status."""
    by_loc = {e.canonical_location: e for e in _index().entries}
    charter = by_loc["spine:DOCTRINE.md"]
    assert charter.reported_status == STATUS_UNKNOWN
    assert charter.status_source_ref is None


# --- the museum label: included is not current ------------------------------- #


def test_parked_doc_is_carried_without_any_current_or_authority_verb():
    """The openly PARKED draft is in the corpus and in Edition 2, but Spine reports
    it as non-binding and asserts only located/rendered — it is never laundered
    into 'current' or any legitimacy verb."""
    by_loc = {e.canonical_location: e for e in _index().entries}
    parked = by_loc["agent_gov:working/parked-p31-activation.md"]
    assert parked.reported_status == "non-binding"
    assert parked.spine_assertions == (LOCATED, RENDERED)
    # The verbatim self-declaration is preserved (faithful quotation), and the
    # word "current" is nowhere asserted by Spine.
    assert "PARKED" in (parked.status_source_ref or "")


def test_render_launders_nothing_in_the_mixed_corpus():
    md = render_markdown(_index())
    assert "Findability is not legitimacy" in md
    assert "located · rendered" in md
    # No legitimacy verb appears as a Spine assertion anywhere in the table.
    for verb in ("| governed", "| valid", "| ratified |", "asserts ratified"):
        assert verb not in md
    # The unstatused charter renders as an explicit no-status cell, not a guess.
    assert "_(no status reported)_" in md


# --- Edition 2: distinct, immutable, still authority-free -------------------- #


def test_edition_2_is_minted_distinct_from_edition_1_and_pinned():
    build = build_edition(_CORPUS, created_at=_CREATED, manifest_ref="specimens/mixed_status_corpus.yaml")
    assert build.edition.edition_id == _EDITION_2_ID
    assert build.edition.edition_id != _EDITION_1_ID
    assert build.edition.spine_assertions == (LOCATED, RENDERED)
    assert build.edition.is_navigational_only is True


def test_edition_2_freezes_five_navigational_entries():
    import json

    build = build_edition(_CORPUS, created_at=_CREATED, manifest_ref="specimens/mixed_status_corpus.yaml")
    frozen = json.loads(build.files[INDEX_FILENAME])
    assert len(frozen["entries"]) == 5
    assert all(e["spine_assertions"] == [LOCATED, RENDERED] for e in frozen["entries"])
    assert not any(LEGITIMACY_VERBS.intersection(e["spine_assertions"]) for e in frozen["entries"])


def test_genesis_corpus_and_edition_1_are_untouched():
    """Adding a second corpus did not mutate the genesis family or move Edition 1
    (a second corpus is added surface area, not a mutation of the first)."""
    genesis = build_edition(
        _GENESIS, created_at="2026-06-25T00:00:00Z", manifest_ref="specimens/predicate_witness_manifest.yaml"
    )
    assert genesis.edition.edition_id == _EDITION_1_ID
    assert len(build_index(load_manifest(_GENESIS), observed_at="2026-06-25T00:00:00Z").entries) == 7
