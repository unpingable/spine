# SPDX-License-Identifier: Apache-2.0
"""The edition-diff contract: describe package drift, never doctrinal movement.

> Edition comparison describes package drift, not doctrinal movement.

A diff between two frozen Editions reports what differs — added / removed / changed
/ unchanged — and asserts nothing about which Edition is current, newer, or
supersedes the other. Two walls are exercised here: drift is *substantive* (not
chronological — observation time never makes an entry "changed"), and Spine's own
framing may never editorialize a difference into succession
(``EditionSuccessionError``).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spine import (
    EditionLoadError,
    EditionSuccessionError,
    SpineRefusal,
    check_no_succession_framing,
    diff_editions,
    load_edition,
    render_edition_diff,
)
from spine.edition import INDEX_FILENAME, write_edition
from spine.edition_diff import DIFF_FRAMING
from spine.refusal import LEGITIMACY_VERBS, LOCATED, RENDERED, SUCCESSION_FRAMING

_ROOT = Path(__file__).resolve().parents[1]
_EDITIONS = _ROOT / "editions"
# The two real committed editions (Slice 1b genesis family, Slice 1c mixed corpus).
_E1 = _EDITIONS / "fabb36a44c45ff3737c88fcd70d132899d768c8be1d99b33c3a765d1f8be8601"
_E2 = _EDITIONS / "b94f04428773ced08c2bd06e17ad9e892cc8eb1f67ad7c5a7f1b1f0d61589459"

_T0 = "2026-06-28T00:00:00Z"
_T1 = "2026-06-29T00:00:00Z"


def _art(path, *, status="candidate", source="self:header candidate", witness=None, repo="t"):
    return {
        "repo": repo,
        "path": path,
        "reported_status": status,
        "status_source_ref": source,
        "witness_ref": witness,
    }


def _edition_dir(tmp_path, name, artifacts, *, created_at=_T0):
    """Write a real immutable edition from an inline manifest and return its dir."""
    manifest = {"adapter": "provisional_git_manifest_v0", "artifacts": artifacts}
    mpath = tmp_path / f"{name}.yaml"
    mpath.write_text(yaml.safe_dump(manifest))
    _, ed_dir = write_edition(
        mpath, created_at=created_at, out_root=tmp_path / f"{name}_root", manifest_ref=name
    )
    return ed_dir


def _diff(tmp_path, base_arts, target_arts, *, base_at=_T0, target_at=_T0):
    base = load_edition(_edition_dir(tmp_path, "base", base_arts, created_at=base_at))
    target = load_edition(_edition_dir(tmp_path, "target", target_arts, created_at=target_at))
    return diff_editions(base, target)


# --- the set difference: added / removed / unchanged ------------------------- #


def test_diff_of_an_edition_with_itself_is_all_unchanged(tmp_path):
    arts = [_art("a.md"), _art("b.md")]
    ed = load_edition(_edition_dir(tmp_path, "self", arts))
    diff = diff_editions(ed, ed)
    assert diff.added == ()
    assert diff.removed == ()
    assert diff.changed == ()
    assert diff.unchanged == ("t:a.md", "t:b.md")


def test_added_and_removed_are_a_set_difference(tmp_path):
    diff = _diff(tmp_path, [_art("a.md"), _art("b.md")], [_art("b.md"), _art("c.md")])
    assert [r.canonical_location for r in diff.added] == ["t:c.md"]
    assert [r.canonical_location for r in diff.removed] == ["t:a.md"]
    assert diff.unchanged == ("t:b.md",)
    assert diff.changed == ()


# --- changed: SUBSTANTIVE drift only (the load-bearing design test) ---------- #


def test_changed_detects_a_substantive_status_move(tmp_path):
    """Same ref, different reported_status (with sources) -> changed, side-by-side."""
    diff = _diff(
        tmp_path,
        [_art("a.md", status="candidate", source="self:candidate")],
        [_art("a.md", status="non-binding", source="self:non-binding")],
    )
    assert diff.unchanged == ()
    assert len(diff.changed) == 1
    c = diff.changed[0]
    assert c.canonical_location == "t:a.md"
    assert c.base_reported_status == "candidate"
    assert c.target_reported_status == "non-binding"


def test_observation_time_never_makes_an_entry_changed(tmp_path):
    """The whole point: two editions are observed at different times by
    construction. Identical substance at different created_at is UNCHANGED, not
    changed — drift means what the sign says moved, not when Spine looked."""
    arts = [_art("a.md"), _art("b.md")]
    diff = _diff(tmp_path, arts, arts, base_at=_T0, target_at=_T1)
    assert diff.base_created_at == _T0
    assert diff.target_created_at == _T1
    assert diff.base_created_at != diff.target_created_at  # time DID move...
    assert diff.changed == ()                              # ...substance did NOT
    assert diff.unchanged == ("t:a.md", "t:b.md")


def test_witness_change_is_substantive(tmp_path):
    """A ref that gains/loses a witness has moved substantively (candidate stays
    candidate but the witness column differs)."""
    diff = _diff(
        tmp_path,
        [_art("a.md", witness=None)],
        [_art("a.md", witness="continuity:reliance/abc")],
    )
    assert len(diff.changed) == 1
    assert diff.changed[0].base_witness_ref is None
    assert diff.changed[0].target_witness_ref == "continuity:reliance/abc"


# --- determinism + closed shape --------------------------------------------- #


def test_diff_is_deterministic_and_sorted(tmp_path):
    base = load_edition(_edition_dir(tmp_path, "b", [_art("z.md"), _art("a.md")]))
    target = load_edition(_edition_dir(tmp_path, "t", [_art("a.md"), _art("m.md"), _art("z.md")]))
    d1 = diff_editions(base, target)
    d2 = diff_editions(base, target)
    assert d1.model_dump_json() == d2.model_dump_json()
    assert [r.canonical_location for r in d1.added] == ["t:m.md"]  # sorted
    assert d1.unchanged == ("t:a.md", "t:z.md")                    # sorted


def test_diff_carries_no_ranking_or_winner_field():
    """The closed field set IS the wall against a verdict: no winner, latest,
    recommended, current, or rank field may exist on the diff."""
    fields = set(__import__("spine").EditionDiff.model_fields)
    assert fields == {
        "base_edition_id", "target_edition_id",
        "base_created_at", "target_created_at",
        "base_ingress_adapter", "target_ingress_adapter",
        "added", "removed", "changed", "unchanged",
        "spine_assertions",
    }
    forbidden = {"winner", "latest", "current", "recommended", "rank", "supersedes", "newer"}
    assert not (fields & forbidden)


def test_diff_assertions_are_the_boring_pair(tmp_path):
    diff = _diff(tmp_path, [_art("a.md")], [_art("a.md")])
    assert diff.spine_assertions == (LOCATED, RENDERED)
    assert diff.is_navigational_only is True
    assert not LEGITIMACY_VERBS.intersection(diff.spine_assertions)


# --- the render shows drift, never succession -------------------------------- #


def test_render_carries_the_disclaimer(tmp_path):
    diff = _diff(tmp_path, [_art("a.md")], [_art("a.md"), _art("b.md")])
    md = render_edition_diff(diff)
    assert "package drift, not doctrinal movement" in md
    assert "coordinate, not a verdict" in md
    # the added ref appears, quoted — never as a Spine verdict
    assert "`t:b.md`" in md


def test_spine_framing_contains_no_succession_vocabulary():
    """Spine's own framing of the diff is run through the succession wall: not one
    of the forbidden words may appear in a header, label, or the disclaimer."""
    # Does not raise — the framing is clean.
    check_no_succession_framing(*DIFF_FRAMING)


@pytest.mark.parametrize("word", sorted(SUCCESSION_FRAMING))
def test_guard_refuses_each_succession_word(word):
    with pytest.raises(EditionSuccessionError):
        check_no_succession_framing(f"the target is {word} than the base")


def test_guard_does_not_false_positive_on_quoted_status_or_paths():
    """A quoted legitimacy status (``ratified``) is not succession framing, and a
    word-boundary match means ``recurrent`` is not a ``current`` hit. The guard
    polices Spine's verdict-voice, not the entry data it quotes."""
    check_no_succession_framing("the sign says ratified (witness: continuity:abc)")
    check_no_succession_framing("docs/recurrent.md is present only in target")


def test_rendered_diff_over_clean_fixtures_has_no_succession_word(tmp_path):
    """End to end: a real rendered diff (framing + clean quoted data) contains no
    succession vocabulary anywhere."""
    diff = _diff(
        tmp_path,
        [_art("a.md", status="candidate", source="self:candidate")],
        [_art("a.md", status="non-binding", source="self:non-binding"), _art("b.md")],
    )
    md = render_edition_diff(diff).lower()
    import re

    for word in SUCCESSION_FRAMING:
        assert not re.search(rf"\b{re.escape(word)}\b", md), f"succession word {word!r} leaked"


# --- load_edition: read only intact, untampered frozen packages -------------- #


def test_load_edition_round_trips_a_real_committed_edition():
    edition, index = load_edition(_E1)
    assert edition.edition_id.split(":", 1)[1] == _E1.name
    assert index.index_digest == edition.index_digest


def test_load_edition_refuses_a_missing_directory(tmp_path):
    with pytest.raises(EditionLoadError):
        load_edition(tmp_path / "nope")


def test_load_edition_refuses_a_missing_file(tmp_path):
    ed_dir = _edition_dir(tmp_path, "x", [_art("a.md")])
    (ed_dir / INDEX_FILENAME).unlink()
    with pytest.raises(EditionLoadError):
        load_edition(ed_dir)


def test_load_edition_refuses_a_tampered_index(tmp_path):
    """If index.json is swapped for a different index, its digest no longer matches
    the edition's recorded index_digest — a diff over it would be a confident lie,
    so loading fails closed."""
    ed_dir = _edition_dir(tmp_path, "x", [_art("a.md")])
    other = load_edition(_edition_dir(tmp_path, "y", [_art("a.md"), _art("b.md")]))[1]
    (ed_dir / INDEX_FILENAME).write_text(other.model_dump_json(indent=2) + "\n")
    with pytest.raises(EditionLoadError):
        load_edition(ed_dir)


# --- integration: the two real editions diff cleanly ------------------------- #


def test_two_real_committed_editions_diff_as_disjoint(tmp_path):
    """Edition 1 (predicate-witness family) and Edition 2 (mixed corpus) declare
    disjoint corpora: comparing them is all added/removed, nothing unchanged — and
    Spine still refuses to call either one current."""
    base = load_edition(_E1)
    target = load_edition(_E2)
    diff = diff_editions(base, target)
    assert diff.changed == ()
    assert diff.unchanged == ()
    assert len(diff.removed) == len(base[1].entries)   # all of E1 is base-only
    assert len(diff.added) == len(target[1].entries)   # all of E2 is target-only
    md = render_edition_diff(diff)
    assert "package drift" in md


# --- CLI smoke -------------------------------------------------------------- #


def test_cli_edition_compare_smoke(tmp_path, capsys):
    from spine.cli import main

    base = _edition_dir(tmp_path, "cb", [_art("a.md")])
    target = _edition_dir(tmp_path, "ct", [_art("a.md"), _art("b.md")])
    rc = main(["edition", "compare", str(base), str(target)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "package drift, not doctrinal movement" in out


def test_cli_edition_compare_refuses_missing_edition(tmp_path, capsys):
    from spine.cli import main

    base = _edition_dir(tmp_path, "cb", [_art("a.md")])
    rc = main(["edition", "compare", str(base), str(tmp_path / "nope")])
    assert rc == 2  # SpineRefusal -> fail closed
    assert "spine refused" in capsys.readouterr().err


def test_succession_error_is_a_spine_refusal():
    """The new refusal is part of the read-plane wall family, caught by the CLI's
    blanket SpineRefusal handler."""
    assert issubclass(EditionSuccessionError, SpineRefusal)
    assert issubclass(EditionLoadError, SpineRefusal)
