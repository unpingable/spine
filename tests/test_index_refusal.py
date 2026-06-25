# SPDX-License-Identifier: Apache-2.0
"""The refusals that mean — the wall is the whole repo.

> Spine indexes status-bearing objects; it does not bear status.
"""

from __future__ import annotations

import pytest

from spine import build_entry
from spine.refusal import (
    LOCATED,
    RENDERED,
    SpineBearsStatusError,
    UnknownStatusError,
    UnsourcedStatusError,
    UnwitnessedGovernedClaimError,
)

_OBSERVED = "2026-06-25T00:00:00Z"


def _ok(**over):
    base = dict(
        canonical_location="agent_gov:docs/x.md",
        reported_status="candidate",
        observed_at=_OBSERVED,
        status_source_ref="self:header",
    )
    base.update(over)
    return build_entry(**base)


# --- THE WALL: Spine may never assert legitimacy ---------------------------- #


def test_index_presence_does_not_imply_governed_status():
    """A default entry asserts only located/rendered; nothing about it is
    governed, valid, or ratified."""
    e = _ok()
    assert e.spine_assertions == (LOCATED, RENDERED)
    assert e.is_navigational_only is True
    assert e.reported_status == "candidate"  # quoted, not Spine's word


@pytest.mark.parametrize("verb", ["ratified", "governed", "valid", "witnessed", "certified"])
def test_spine_may_not_assert_a_legitimacy_verb(verb):
    """The whole repo in one test: a legitimacy verb in spine_assertions is the
    wall falling. It must refuse."""
    with pytest.raises(SpineBearsStatusError):
        _ok(spine_assertions=(LOCATED, verb))


# --- reported_status is a quotation; it needs a source ---------------------- #


def test_ratified_entry_requires_status_source_ref():
    with pytest.raises(UnsourcedStatusError):
        _ok(reported_status="ratified", status_source_ref=None, witness_ref="w:1")


def test_candidate_status_requires_a_source():
    """Even a candidate status is *reported* — Spine quotes a sign, so it needs
    the sign."""
    with pytest.raises(UnsourcedStatusError):
        _ok(reported_status="candidate", status_source_ref=None)


def test_unknown_status_is_the_one_honest_sourceless_entry():
    """`unknown` is Spine saying it does not know — that needs no source and is
    purely navigational."""
    e = _ok(reported_status="unknown", status_source_ref=None)
    assert e.reported_status == "unknown"


def test_unrecognized_status_refuses():
    with pytest.raises(UnknownStatusError):
        _ok(reported_status="probably-fine")


# --- a governed claim without a witness is a HARD refusal ------------------- #


def test_missing_witness_for_governed_entry_is_hard_failure():
    """A ratified claim with no witness is refused outright — never softened to a
    warning."""
    with pytest.raises(UnwitnessedGovernedClaimError):
        _ok(reported_status="ratified", status_source_ref="self:header", witness_ref=None)


def test_governed_entry_with_witness_is_admissible():
    e = _ok(reported_status="ratified", status_source_ref="maude:ruling-7", witness_ref="nq:obs-3")
    assert e.reported_status == "ratified"
    # ...but Spine STILL only asserts located/rendered. It quotes the ratification;
    # it does not perform it.
    assert e.is_navigational_only is True


def test_candidate_entry_may_be_unwitnessed_only_if_marked_non_binding():
    """A candidate/non-binding entry may carry no witness — the non-authoritative
    marker IS the admissibility story. (Contrast the governed case above.)"""
    for status in ("candidate", "non-binding"):
        e = _ok(reported_status=status, witness_ref=None, status_source_ref="self:header")
        assert e.witness_ref is None
        assert e.reported_status == status
