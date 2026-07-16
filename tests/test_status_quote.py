# SPDX-License-Identifier: Apache-2.0
"""The verbatim quote — normalization must never launder the quotation.

OQ-2 ruling (2026-07-16): quote where quotable, ``unknown`` otherwise; the
specimen retains the quoted text AND its locator, not merely the normalized
``reported_status``. OQ-4 rebar: an edition record must be extractable
faithfully — stable id, locator, quoted text, provenance — without the index
runtime around it. These tests pin both.
"""

from __future__ import annotations

import pytest

from spine import build_entry, build_index, load_manifest
from spine.refusal import UnattributedQuoteError

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


# --- the quote rides with its locator, verbatim ----------------------------- #


def test_quote_is_retained_verbatim():
    quote = "Status: CANDIDATE (unratified — see docket #12)"
    e = _ok(status_quote=quote)
    assert e.status_quote == quote
    assert e.reported_status == "candidate"  # normalization sits BESIDE the quote


def test_quote_without_source_ref_is_refused():
    """A quotation that cannot say where it was read is not a quotation."""
    with pytest.raises(UnattributedQuoteError):
        _ok(
            reported_status="unknown",
            status_source_ref=None,
            status_quote="Status: something",
        )


def test_no_quote_is_legal():
    """Absence of a declaration is not a declaration of absence — a doc with
    no machine-quotable status simply carries no quote."""
    e = _ok()
    assert e.status_quote is None


# --- digest discipline ------------------------------------------------------ #


def test_pre_quote_entries_keep_their_digest():
    """Backward compatibility is load-bearing: an entry with no quote hashes
    exactly as it did before the field existed, so the committed genesis
    editions stay valid."""
    e = _ok()
    fields_before_quote_existed = {
        "canonical_location": e.canonical_location,
        "reported_status": e.reported_status,
        "status_source_ref": e.status_source_ref,
        "witness_ref": e.witness_ref,
        "ingress_adapter": e.ingress_adapter,
        "observed_at": e.observed_at,
        "spine_assertions": list(e.spine_assertions),
    }
    import hashlib
    import json

    legacy = "sha256:" + hashlib.sha256(
        json.dumps(fields_before_quote_existed, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert e.entry_digest == legacy


def test_quote_changes_the_digest():
    """The quote is content, not decoration: two entries differing only in
    quoted wording are different records."""
    a = _ok(status_quote="Status: CANDIDATE")
    b = _ok(status_quote="Status: CANDIDATE (amended)")
    assert a.entry_digest != b.entry_digest
    assert a.entry_digest != _ok().entry_digest


# --- manifest -> index -> extraction (the OQ-4 rebar pass) ------------------ #

_MANIFEST = """\
adapter: provisional_git_manifest_v0
artifacts:
  - repo: agent_gov
    path: docs/roadmaps/README.md
    reported_status: candidate
    status_source_ref: "agent_gov:docs/roadmaps/README.md#status"
    status_quote: "Status: CANDIDATE — not yet ratified"
"""


def test_quote_flows_from_manifest_to_entry():
    m = load_manifest("inline.yaml", content=_MANIFEST)
    idx = build_index(m, observed_at=_OBSERVED)
    (e,) = idx.entries
    assert e.status_quote == "Status: CANDIDATE — not yet ratified"
    assert e.status_source_ref == "agent_gov:docs/roadmaps/README.md#status"


def test_one_record_extracts_faithfully_without_the_runtime():
    """The stele-accommodation falsification pass, pinned: a single record
    pulled out of an index carries stable id, locator, quoted text, and
    provenance as plain data — no index object, no repository access."""
    m = load_manifest("inline.yaml", content=_MANIFEST)
    idx = build_index(m, observed_at=_OBSERVED)
    (e,) = idx.entries

    extracted = e.model_dump()
    extracted["entry_digest"] = e.entry_digest

    # The durable record stands alone: every stele-relevant coordinate is
    # present as a plain value.
    assert extracted["entry_digest"].startswith("sha256:")
    assert extracted["canonical_location"] == "agent_gov:docs/roadmaps/README.md"
    assert extracted["status_quote"] == "Status: CANDIDATE — not yet ratified"
    assert extracted["status_source_ref"] == "agent_gov:docs/roadmaps/README.md#status"
    assert extracted["reported_status"] == "candidate"
    assert extracted["observed_at"] == _OBSERVED
    assert set(extracted["spine_assertions"]) == {"located", "rendered"}
