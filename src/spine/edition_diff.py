# SPDX-License-Identifier: Apache-2.0
"""The edition diff — describe package drift between two frozen Editions.

> Edition comparison describes package drift, not doctrinal movement.

Two Editions are two immutable packages. A diff between them is a factual statement
about transport: these refs appear in one and not the other; this ref's reported
status differs. That is *drift*. It is never "newer is better," "this supersedes
that," or "this is now current." Succession is a verdict, and verdicts live in
Continuity (reliance) or Maude (adjudication) — never in a read-plane diff. The
forbidden-framing wall (:func:`spine.refusal.check_no_succession_framing`) makes
that a mechanical refusal, not a style preference.

**Drift is substantive, not chronological.** Two Editions are observed at different
times by construction, and an :pyattr:`~spine.index.IndexEntry.entry_digest`
includes ``observed_at`` — so comparing digests would mark *every* entry changed and
tell you nothing. A ``changed`` entry means its *substance* moved (what the sign
says, its source, its witness), not that Spine looked at a different clock. Time
lives in the edition metadata (``base_created_at`` vs ``target_created_at``), never
as a per-entry change.

**Direction is a coordinate, not a verdict.** ``diff_editions(base, target)`` reports
the set difference *from base to target*: ``added`` = in target, not base; ``removed``
= in base, not target. Naming them base/target imposes an axis, not a value.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from . import refusal
from .edition import EDITION_FILENAME, INDEX_FILENAME, Edition
from .index import IndexEntry, SpineIndex
from .refusal import LOCATED, RENDERED, EditionLoadError


def load_edition(edition_dir: str | Path) -> tuple[Edition, SpineIndex]:
    """Load an immutable Edition directory into its :class:`Edition` metadata and
    the frozen :class:`SpineIndex` it shipped.

    Fails closed (``EditionLoadError``) on a missing directory, a missing required
    file, or an ``index_digest`` mismatch between the recorded edition and the
    index it ships (tamper). The integrity check is the point: a diff over a
    damaged package would be a confident lie about package drift.
    """
    root = Path(edition_dir)
    if not root.is_dir():
        raise EditionLoadError(f"edition directory {root} does not exist")

    edition_path = root / EDITION_FILENAME
    index_path = root / INDEX_FILENAME
    for required in (edition_path, index_path):
        if not required.is_file():
            raise EditionLoadError(
                f"edition directory {root} is missing required file {required.name}"
            )

    try:
        edition = Edition.model_validate_json(edition_path.read_text())
        index = SpineIndex.model_validate_json(index_path.read_text())
    except Exception as exc:  # pydantic / json errors → typed refusal, not a trace
        raise EditionLoadError(
            f"edition directory {root} did not parse as a frozen package: {exc}"
        ) from exc

    if index.index_digest != edition.index_digest:
        raise EditionLoadError(
            f"edition {edition.edition_id} records index_digest "
            f"{edition.index_digest} but ships an index digesting to "
            f"{index.index_digest} — refusing to diff a tampered package"
        )
    return edition, index


def _substance(entry: IndexEntry) -> tuple:
    """The substantive identity of an entry — everything EXCEPT ``observed_at``.

    Two editions observe at different times; comparing observation time would mark
    every entry changed. Drift means *this* moved: what the sign says, its source,
    its witness, the (boring) assertions, the adapter."""
    return (
        entry.reported_status,
        entry.status_source_ref,
        entry.witness_ref,
        entry.ingress_adapter,
        tuple(sorted(entry.spine_assertions)),
    )


class EntryRef(BaseModel):
    """A light projection of an entry, for the added / removed lists. Carries the
    quoted status + its source + witness (all already wall-checked when the entry
    was built) — never a Spine verdict."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_location: str
    reported_status: str
    status_source_ref: str | None = None
    witness_ref: str | None = None

    @classmethod
    def of(cls, entry: IndexEntry) -> EntryRef:
        return cls(
            canonical_location=entry.canonical_location,
            reported_status=entry.reported_status,
            status_source_ref=entry.status_source_ref,
            witness_ref=entry.witness_ref,
        )


class ChangedRef(BaseModel):
    """A ref present in both editions whose *substance* differs. Base and target
    values sit in separate columns — never joined by an arrow, because an arrow
    ("became") is a succession claim and a column ("differs") is a fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_location: str
    base_reported_status: str
    target_reported_status: str
    base_status_source_ref: str | None = None
    target_status_source_ref: str | None = None
    base_witness_ref: str | None = None
    target_witness_ref: str | None = None


class EditionDiff(BaseModel):
    """The drift between two frozen Editions, keyed on ``canonical_location``.

    There is deliberately no ranking, winner, recommendation, or "latest" field —
    the closed field set *is* the wall against turning a difference into a verdict.
    ``spine_assertions`` is the same boring pair: Spine *located* two editions and
    *rendered* their difference; it asserts nothing about which one is current."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    base_edition_id: str
    target_edition_id: str
    base_created_at: str
    target_created_at: str
    base_ingress_adapter: str
    target_ingress_adapter: str
    added: tuple[EntryRef, ...]
    removed: tuple[EntryRef, ...]
    changed: tuple[ChangedRef, ...]
    unchanged: tuple[str, ...]
    spine_assertions: tuple[str, ...] = Field(default=(LOCATED, RENDERED))

    @property
    def is_navigational_only(self) -> bool:
        return set(self.spine_assertions).issubset({LOCATED, RENDERED})


def diff_editions(
    base: tuple[Edition, SpineIndex],
    target: tuple[Edition, SpineIndex],
) -> EditionDiff:
    """Compute a pure, deterministic diff from ``base`` to ``target``.

    ``added`` = refs in target not in base; ``removed`` = refs in base not in
    target; ``changed`` = refs in both whose substance (not observation time)
    differs; ``unchanged`` = refs in both with identical substance. Every list is
    sorted by ``canonical_location`` so the same two editions always yield a
    byte-identical ``EditionDiff``.
    """
    base_edition, base_index = base
    target_edition, target_index = target

    # The package-layer wall, on the diff's own assertions: a diff carries only the
    # boring pair, never a legitimacy verb.
    refusal.check_spine_assertions((LOCATED, RENDERED))

    base_by_loc = {e.canonical_location: e for e in base_index.entries}
    target_by_loc = {e.canonical_location: e for e in target_index.entries}

    added = [
        EntryRef.of(target_by_loc[loc])
        for loc in target_by_loc.keys() - base_by_loc.keys()
    ]
    removed = [
        EntryRef.of(base_by_loc[loc])
        for loc in base_by_loc.keys() - target_by_loc.keys()
    ]

    changed: list[ChangedRef] = []
    unchanged: list[str] = []
    for loc in base_by_loc.keys() & target_by_loc.keys():
        b = base_by_loc[loc]
        t = target_by_loc[loc]
        if _substance(b) == _substance(t):
            unchanged.append(loc)
        else:
            changed.append(
                ChangedRef(
                    canonical_location=loc,
                    base_reported_status=b.reported_status,
                    target_reported_status=t.reported_status,
                    base_status_source_ref=b.status_source_ref,
                    target_status_source_ref=t.status_source_ref,
                    base_witness_ref=b.witness_ref,
                    target_witness_ref=t.witness_ref,
                )
            )

    added.sort(key=lambda r: r.canonical_location)
    removed.sort(key=lambda r: r.canonical_location)
    changed.sort(key=lambda r: r.canonical_location)
    unchanged.sort()

    return EditionDiff(
        base_edition_id=base_edition.edition_id,
        target_edition_id=target_edition.edition_id,
        base_created_at=base_edition.created_at,
        target_created_at=target_edition.created_at,
        base_ingress_adapter=base_edition.ingress_adapter,
        target_ingress_adapter=target_edition.ingress_adapter,
        added=tuple(added),
        removed=tuple(removed),
        changed=tuple(changed),
        unchanged=tuple(unchanged),
    )


# --------------------------------------------------------------------------- #
# Render. Every framing string below is Spine's own voice, so every one is run
# through the succession wall before it is emitted. The disclaimer is load-bearing.
# --------------------------------------------------------------------------- #

_DIFF_HEADER = """\
# Spine edition diff — base `{base_id}` → target `{target_id}`

> **This describes package drift, not doctrinal movement.** Spine *located* two
> immutable Editions and *rendered* their difference. It does not assert that
> either Edition is the one to rely on, that the target replaces the base, or that
> anything here is ratified. The arrow above is the order you asked in — a
> coordinate, not a verdict. Which Edition (if any) is the one to rely on is a
> question for Continuity (reliance) or Maude (adjudication), not for this diff.

- base:   `{base_id}` packaged at `{base_at}` (ingress `{base_adapter}`)
- target: `{target_id}` packaged at `{target_at}` (ingress `{target_adapter}`)
"""

_DIFF_SUMMARY = (
    "Drift: {n_added} present-only-in-target, {n_removed} present-only-in-base, "
    "{n_changed} differing, {n_unchanged} identical."
)

_PRESENT_ONLY_IN_TARGET = "## Present only in target"
_PRESENT_ONLY_IN_BASE = "## Present only in base"
_DIFFERING = "## Differing (substance moved; base and target shown side by side)"
_IDENTICAL = "## Identical in both"

_DIFF_FOOTER = (
    "_Every line above is a located/rendered fact about two frozen packages. A "
    "difference between Editions is drift in what was found, not a ruling about "
    "what is true._"
)

# The full set of Spine-authored framing constants. Checked against the succession
# wall so the diff cannot editorialize itself into a verdict; the test pins it too.
DIFF_FRAMING: tuple[str, ...] = (
    _DIFF_HEADER,
    _DIFF_SUMMARY,
    _PRESENT_ONLY_IN_TARGET,
    _PRESENT_ONLY_IN_BASE,
    _DIFFERING,
    _IDENTICAL,
    _DIFF_FOOTER,
)


def _status_quote(status: str, source: str | None) -> str:
    src = f" (`{source}`)" if source else ""
    return f"the sign says **{status}**{src}"


def render_edition_diff(diff: EditionDiff) -> str:
    """Render an :class:`EditionDiff` as markdown with the disclaimer visible and
    no succession framing. Pure. Spine's own framing is guarded before emission;
    quoted entry data (which may legitimately contain a word like ``ratified``) is
    not Spine's voice and is rendered as a quotation."""
    # Guard Spine's own voice — never the quoted entry data.
    refusal.check_no_succession_framing(*DIFF_FRAMING)

    out = [
        _DIFF_HEADER.format(
            base_id=diff.base_edition_id,
            target_id=diff.target_edition_id,
            base_at=diff.base_created_at,
            target_at=diff.target_created_at,
            base_adapter=diff.base_ingress_adapter,
            target_adapter=diff.target_ingress_adapter,
        ),
        _DIFF_SUMMARY.format(
            n_added=len(diff.added),
            n_removed=len(diff.removed),
            n_changed=len(diff.changed),
            n_unchanged=len(diff.unchanged),
        ),
        "",
        _PRESENT_ONLY_IN_TARGET,
    ]
    out += (
        [f"- `{r.canonical_location}` — {_status_quote(r.reported_status, r.status_source_ref)}"
         for r in diff.added]
        or ["- _(none)_"]
    )
    out += ["", _PRESENT_ONLY_IN_BASE]
    out += (
        [f"- `{r.canonical_location}` — {_status_quote(r.reported_status, r.status_source_ref)}"
         for r in diff.removed]
        or ["- _(none)_"]
    )
    out += ["", _DIFFERING]
    if diff.changed:
        out.append("| Artifact | base — the sign says | target — the sign says |")
        out.append("|----------|----------------------|------------------------|")
        for c in diff.changed:
            out.append(
                f"| `{c.canonical_location}` "
                f"| {_status_quote(c.base_reported_status, c.base_status_source_ref)} "
                f"| {_status_quote(c.target_reported_status, c.target_status_source_ref)} |"
            )
    else:
        out.append("- _(none)_")
    out += ["", _IDENTICAL]
    out += ([f"- `{loc}`" for loc in diff.unchanged] or ["- _(none)_"])
    out += ["", _DIFF_FOOTER]
    return "\n".join(out) + "\n"
