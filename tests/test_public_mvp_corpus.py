# SPDX-License-Identifier: Apache-2.0
"""Packet S-B pins — the public-mvp specimen corpus is frozen and honest.

The corpus is agent_gov's real planning surface (roadmaps + campaigns),
hand-declared. These tests pin the frozen edition's identity, the lane
distribution the OQ-2 ruling produced, and the invariant that corpus
expansion increases surface area, not authority.
"""

from __future__ import annotations

from pathlib import Path

from spine import build_index, load_manifest
from spine.edition_diff import load_edition

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "specimens" / "public_mvp_roadmaps_campaigns.yaml"
CREATED_AT = "2026-07-16T00:00:00Z"  # the EDITION timestamp (OQ-3: fixed, documented)
EDITION_ID = "sha256:b9b16649841b281d8354952ed2c3a7790a1ef343e004e651ffdccd884ffd504d"
EDITION_DIR = REPO / "editions" / EDITION_ID.removeprefix("sha256:")


def _index():
    return build_index(load_manifest(MANIFEST), observed_at=CREATED_AT)


def test_specimen_manifest_loads_and_counts():
    idx = _index()
    assert len(idx.entries) == 41


def test_lane_distribution_is_the_ruled_policy():
    """6 governed claims (each witnessed), 13 candidates, 22 unknown — and
    every quotable status carries its verbatim wording beside the
    normalization."""
    idx = _index()
    by = {}
    for e in idx.entries:
        by.setdefault(e.reported_status, []).append(e)
    assert len(by["ratified"]) == 6
    assert len(by["candidate"]) == 13
    assert len(by["unknown"]) == 22
    # a governed claim is never unwitnessed in this corpus
    assert all(e.witness_ref for e in by["ratified"])
    # normalized-from-quotation entries keep the quotation
    assert all(e.status_quote for e in by["ratified"])
    assert all(e.status_quote for e in by["candidate"])
    # the honest middle lane exists: quotable but not normalizable
    quoted_unknown = [e for e in by["unknown"] if e.status_quote]
    assert len(quoted_unknown) == 9
    assert all(e.status_source_ref for e in quoted_unknown)


def test_corpus_expansion_is_not_authority():
    """Every entry asserts only located/rendered — indexing agent_gov's whole
    planning surface mints nothing."""
    idx = _index()
    assert all(e.is_navigational_only for e in idx.entries)


def test_frozen_edition_is_reproducible_from_the_committed_manifest():
    """A stranger rebuilding the index from the committed manifest at the
    documented edition timestamp gets byte-identical identity."""
    edition, files = load_edition(EDITION_DIR)
    assert edition.edition_id == EDITION_ID
    assert edition.created_at == CREATED_AT
    assert _index().index_digest == edition.index_digest


def test_ratified_lane_quotes_survive_the_freeze():
    """The verbatim RATIFIED wording is in the frozen render — quotation
    visible, normalization checkable, warning mark present."""
    render = (EDITION_DIR / "index.md").read_text()
    assert "the sign says **ratified** ⚠ governed-claim" in render
    assert "RATIFIED (2026-07-02, A8" in render
    assert "_(not normalized)_ — the sign says verbatim:" in render
