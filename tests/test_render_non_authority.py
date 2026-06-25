# SPDX-License-Identifier: Apache-2.0
"""The rendered view must make the refusal visible — never launder a found thing
into a warranted thing."""

from __future__ import annotations

from pathlib import Path

from spine import build_index, load_manifest, render_markdown

_SPECIMEN = Path(__file__).resolve().parents[1] / "specimens" / "predicate_witness_manifest.yaml"
_OBSERVED = "2026-06-25T00:00:00Z"


def _render_specimen() -> str:
    return render_markdown(build_index(load_manifest(_SPECIMEN), observed_at=_OBSERVED))


def test_render_states_findability_is_not_legitimacy():
    md = _render_specimen()
    assert "Findability is not legitimacy" in md
    assert "located and rendered" in md


def test_render_frames_status_as_quotation_never_bare_verb():
    """The view says 'the sign says candidate', never a bare 'candidate' standing
    as Spine's own verdict."""
    md = _render_specimen()
    assert "the sign says **candidate**" in md
    # The boast Spine is forbidden from making must not appear as an assertion.
    assert "the sign says **ratified**" not in md  # nothing in the specimen is ratified


def test_render_marks_unwitnessed_loudly():
    md = _render_specimen()
    # Every specimen entry is unwitnessed; the view must say so, not hide it.
    assert "**NONE — unwitnessed**" in md


def test_render_only_ever_asserts_located_and_rendered():
    """Across the whole rendered table, Spine's own assertion column is only
    located/rendered — never a legitimacy verb."""
    md = _render_specimen()
    # The asserts column cells are 'located · rendered'.
    assert "located · rendered" in md
    for verb in ("| governed", "| valid", "| ratified |", "asserts ratified"):
        assert verb not in md


def test_render_is_deterministic():
    assert _render_specimen() == _render_specimen()
