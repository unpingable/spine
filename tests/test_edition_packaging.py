# SPDX-License-Identifier: Apache-2.0
"""The Edition packaging contract: freeze what was found, promote nothing.

> Freezing an index preserves what was found; it does not promote what was found.

An Edition adds immutability + citability. It must NOT add authority: the frozen
index still asserts only ``located`` / ``rendered``, still quotes
``reported_status`` from a source, still marks unwitnessed material loudly — and
``spine_assertions`` on the Edition itself never holds a legitimacy verb.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from spine import (
    BuildProvenance,
    Edition,
    EditionExistsError,
    SpineBearsStatusError,
    SpineRefusal,
    build_edition,
    build_index,
    edition_dir_for,
    load_manifest,
    write_edition,
)
from spine.edition import (
    EDITION_FILENAME,
    INDEX_FILENAME,
    MANIFEST_FILENAME,
    RENDER_FILENAME,
)
from spine.refusal import LEGITIMACY_VERBS, LOCATED, RENDERED

_SPECIMEN = Path(__file__).resolve().parents[1] / "specimens" / "predicate_witness_manifest.yaml"
_CREATED = "2026-06-25T00:00:00Z"
# The committed first edition of the specimen corpus. Pinned so a refactor that
# silently moves the citation target fails loudly here.
_SPECIMEN_EDITION_ID = "sha256:fabb36a44c45ff3737c88fcd70d132899d768c8be1d99b33c3a765d1f8be8601"


def _provenance(**over) -> BuildProvenance:
    base = dict(
        tool="spine",
        tool_version="0.0.1",
        ingress_adapter="provisional_git_manifest_v0",
        manifest_ref="specimen",
        created_at=_CREATED,
        reproduce="spine edition create specimen --created-at x --out y",
    )
    base.update(over)
    return BuildProvenance(**base)


# --- reproducibility: same inputs + same created_at -> identical edition ----- #


def test_edition_build_is_reproducible():
    """Same manifest bytes + same created_at -> identical edition_id AND
    byte-identical files. A citation target that moved would be useless."""
    a = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    b = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    assert a.edition.edition_id == b.edition.edition_id
    assert a.files == b.files  # every frozen file, byte-for-byte
    assert a.edition.model_dump_json() == b.edition.model_dump_json()


def test_written_edition_is_byte_identical_across_runs(tmp_path):
    """Writing the same edition under two roots yields byte-identical files."""
    _, dir_a = write_edition(_SPECIMEN, created_at=_CREATED, out_root=tmp_path / "a", manifest_ref="specimen")
    _, dir_b = write_edition(_SPECIMEN, created_at=_CREATED, out_root=tmp_path / "b", manifest_ref="specimen")
    assert dir_a.name == dir_b.name  # keyed by content-addressed edition_id
    for name in (EDITION_FILENAME, MANIFEST_FILENAME, INDEX_FILENAME, RENDER_FILENAME):
        assert (dir_a / name).read_bytes() == (dir_b / name).read_bytes()


# --- the citation target is content-addressed -------------------------------- #


def test_edition_id_is_content_hash_over_created_at():
    """A different created_at is a different citation target (time is content)."""
    a = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    b = build_edition(_SPECIMEN, created_at="2026-06-26T00:00:00Z", manifest_ref="specimen")
    assert a.edition.edition_id != b.edition.edition_id


def test_edition_id_changes_when_manifest_bytes_change(tmp_path):
    """Different located content -> different edition_id. The digest does not lie
    about what was frozen."""
    altered = tmp_path / "altered.yaml"
    altered.write_bytes(_SPECIMEN.read_bytes() + b"\n# a trailing comment\n")
    a = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="m")
    b = build_edition(altered, created_at=_CREATED, manifest_ref="m")
    assert a.edition.manifest_digest != b.edition.manifest_digest
    assert a.edition.edition_id != b.edition.edition_id


def test_edition_id_excludes_build_provenance():
    """Two builds that locate identical content at the same time share a citation
    target even when *how* they were referenced differs — provenance documents
    reproduction, it does not fork identity."""
    a = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="ref-one")
    b = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="ref-two")
    assert a.edition.build_provenance.manifest_ref != b.edition.build_provenance.manifest_ref
    assert a.edition.edition_id == b.edition.edition_id


# --- THE WALL AT THE PACKAGE LAYER: preserve status, create none ------------- #


def test_edition_preserves_reported_status_but_creates_none():
    """The frozen index still reports candidate + unwitnessed for the whole
    family — exactly what Slice 1 produced. Freezing changed immutability, not
    status."""
    build = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    frozen_index = json.loads(build.files[INDEX_FILENAME])
    assert len(frozen_index["entries"]) == 7
    assert all(e["reported_status"] == "candidate" for e in frozen_index["entries"])
    assert all(e["witness_ref"] is None for e in frozen_index["entries"])
    # Every entry still asserts only located/rendered inside the Edition.
    for e in frozen_index["entries"]:
        assert e["spine_assertions"] == [LOCATED, RENDERED]


def test_edition_assertions_are_the_boring_pair():
    build = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    assert build.edition.spine_assertions == (LOCATED, RENDERED)
    assert build.edition.is_navigational_only is True


@pytest.mark.parametrize("verb", sorted(LEGITIMACY_VERBS))
def test_edition_may_not_carry_a_legitimacy_verb(verb):
    """An Edition that ever held a legitimacy verb would be the wall falling at
    the package layer. The blessed factory refuses it — typed, before any Edition
    is constructed."""
    with pytest.raises(SpineBearsStatusError):
        build_edition(_SPECIMEN, created_at=_CREATED, spine_assertions=(LOCATED, verb))


def test_edition_metadata_carries_no_legitimacy_verb_as_its_own_assertion():
    """The serialized edition.json asserts only located/rendered — it never lists
    a legitimacy verb as Spine's own word."""
    build = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    meta = json.loads(build.files[EDITION_FILENAME])
    assert meta["spine_assertions"] == [LOCATED, RENDERED]
    assert not LEGITIMACY_VERBS.intersection(meta["spine_assertions"])


# --- the metadata records the digests + reproducible provenance -------------- #


def test_edition_records_digests_and_provenance():
    build = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    meta = json.loads(build.files[EDITION_FILENAME])
    for key in ("edition_id", "manifest_digest", "index_digest", "render_digest"):
        assert meta[key].startswith("sha256:")
    # digests in the metadata bind to the frozen bytes.
    assert build.edition.index_digest == build_index(
        load_manifest(_SPECIMEN), observed_at=_CREATED
    ).index_digest
    prov = meta["build_provenance"]
    assert prov["ingress_adapter"] == "provisional_git_manifest_v0"
    assert prov["created_at"] == _CREATED
    assert prov["reproduce"].startswith("spine edition create")


# --- immutability: never overwrite a prior edition --------------------------- #


def test_edition_is_written_to_its_own_immutable_directory(tmp_path):
    edition, edition_dir = write_edition(
        _SPECIMEN, created_at=_CREATED, out_root=tmp_path, manifest_ref="specimen"
    )
    assert edition_dir == edition_dir_for(tmp_path, edition.edition_id)
    assert edition_dir.is_dir()
    assert (edition_dir / EDITION_FILENAME).exists()
    assert (edition_dir / MANIFEST_FILENAME).read_bytes() == _SPECIMEN.read_bytes()


def test_re_minting_an_edition_refuses_rather_than_overwrites(tmp_path):
    """The no-overwrite rule is the point: a second create into the same root and
    same inputs hits an occupied edition directory and refuses, loud."""
    write_edition(_SPECIMEN, created_at=_CREATED, out_root=tmp_path, manifest_ref="specimen")
    with pytest.raises(EditionExistsError):
        write_edition(_SPECIMEN, created_at=_CREATED, out_root=tmp_path, manifest_ref="specimen")


def test_round_trip_edition_json_validates():
    """The frozen edition.json deserializes back into an Edition (the metadata is
    a real, re-readable record, not a one-way print)."""
    build = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="specimen")
    reloaded = Edition.model_validate_json(build.files[EDITION_FILENAME])
    assert reloaded.edition_id == build.edition.edition_id
    assert reloaded == build.edition


def test_specimen_edition_id_is_pinned():
    """The committed first edition's citation target must not move under refactor."""
    build = build_edition(
        _SPECIMEN, created_at=_CREATED, manifest_ref="specimens/predicate_witness_manifest.yaml"
    )
    assert build.edition.edition_id == _SPECIMEN_EDITION_ID


# --- defense in depth: the wall holds even off the blessed path -------------- #


@pytest.mark.parametrize("verb", sorted(LEGITIMACY_VERBS))
def test_direct_edition_construction_cannot_carry_a_legitimacy_verb(verb):
    """Even bypassing build_edition, a model-level validator refuses a legitimacy
    verb — the package layer cannot become a priest by hand-constructing one."""
    with pytest.raises(ValidationError):
        Edition(
            edition_id="sha256:" + "0" * 64,
            created_at=_CREATED,
            ingress_adapter="provisional_git_manifest_v0",
            manifest_digest="sha256:" + "1" * 64,
            index_digest="sha256:" + "2" * 64,
            render_digest="sha256:" + "3" * 64,
            build_provenance=_provenance(),
            spine_assertions=(LOCATED, verb),
        )


# --- the citation target is representation-invariant ------------------------- #


def test_assertion_order_and_dupes_do_not_move_the_citation_target():
    """('located','rendered'), reversed, and duplicated all name the same set, so
    they must mint the same edition_id and store the same canonical pair."""
    base = build_edition(_SPECIMEN, created_at=_CREATED, manifest_ref="m")
    reordered = build_edition(
        _SPECIMEN, created_at=_CREATED, manifest_ref="m", spine_assertions=(RENDERED, LOCATED)
    )
    duped = build_edition(
        _SPECIMEN, created_at=_CREATED, manifest_ref="m",
        spine_assertions=(LOCATED, RENDERED, LOCATED),
    )
    assert reordered.edition.edition_id == base.edition.edition_id
    assert duped.edition.edition_id == base.edition.edition_id
    # ...and the stored value is the canonical boring pair regardless of input.
    assert reordered.edition.spine_assertions == (LOCATED, RENDERED)
    assert duped.edition.spine_assertions == (LOCATED, RENDERED)


# --- hostile-input discipline: the edition id never escapes out_root --------- #


@pytest.mark.parametrize(
    "bad_id",
    [
        "sha256:../escape",
        "sha256:" + "g" * 64,        # not hex
        "sha256:abc",                # too short
        "notahash:" + "0" * 64,      # wrong prefix
        "../" + "0" * 64,            # no prefix, traversal
    ],
)
def test_edition_dir_for_refuses_a_malformed_or_hostile_id(tmp_path, bad_id):
    with pytest.raises(SpineRefusal):
        edition_dir_for(tmp_path, bad_id)


def test_partial_write_does_not_leave_an_occupied_target(tmp_path, monkeypatch):
    """A crash mid-write must NOT leave a half-written edition that future runs
    refuse as 'already immutable'. The atomic temp+rename guarantees all-or-nothing."""
    import spine.edition as edmod

    real_replace = edmod.os.replace

    def boom(src, dst):  # fail exactly at publish, after staging is written
        raise OSError("simulated crash at publish")

    monkeypatch.setattr(edmod.os, "replace", boom)
    with pytest.raises(EditionExistsError):
        write_edition(_SPECIMEN, created_at=_CREATED, out_root=tmp_path, manifest_ref="m")

    # No edition target was published, and no staging litter remains.
    monkeypatch.setattr(edmod.os, "replace", real_replace)
    assert not any(p.name.startswith(".staging-") for p in tmp_path.iterdir())
    assert list(tmp_path.iterdir()) == []  # clean: the retry surface is unblocked

    # And a real retry now succeeds into the (still-empty) root.
    edition, edition_dir = write_edition(
        _SPECIMEN, created_at=_CREATED, out_root=tmp_path, manifest_ref="m"
    )
    assert edition_dir.is_dir()
