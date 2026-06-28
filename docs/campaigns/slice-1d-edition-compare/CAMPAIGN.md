# Campaign — Spine Slice 1d: edition compare (the dumb diff)

Status: **SHIPPED** (2026-06-28). A bounded follow-on to Slice 1c. Still
read-plane. Still no authority. Now that two Editions exist, "what changed between
them?" is a real, answerable question — and *someone will want the unsafe answer*
("which one supersedes?"). This slice builds the **safe** answer before the unsafe
one grows mold.

## Exit ticket (2026-06-28)

All seven exit criteria met. `src/spine/edition_diff.py`: pure deterministic
`diff_editions(base, target)` (added / removed / changed / unchanged, keyed on
`canonical_location`, compared on **substantive** fields — observation time
excluded by design); `load_edition` reads only intact, untampered frozen packages
(fails closed on missing dir/file or `index_digest` mismatch); `render_edition_diff`
emits the disclaimer with neutral base/target column framing (no arrows). Two new
typed refusals in the wall module (`EditionLoadError`, `EditionSuccessionError`) +
a closed `SUCCESSION_FRAMING` vocabulary and `check_no_succession_framing` guard
that polices Spine's *own* voice, not quoted entry data. CLI `spine edition compare`
wired. 112 tests pass (37 new in `tests/test_edition_diff.py`), including the
load-bearing **observation-time-is-not-drift** test, the tampered-index refusal, the
closed-field-set guard (no winner/latest/current/rank field), the per-word
succession-refusal sweep, and the false-positive guard (`ratified` quotation /
`recurrent` path are not hits). Dogfood: comparing the two real committed editions
reports them as disjoint (5 target-only, 7 base-only, 0 differing) and refuses to
call either current.

The forbidden list held: the diff adds a comparison + render + two refusal types +
tests — no crawler, no resolver, no witness synthesis, no Continuity integration,
no status vocabulary, no ranking. Both real editions are untouched and still
reproducible.

Next: REENTRY #4 (Continuity as source) — still deferred until a real interface
exists to replace.

## The one line

> **Edition comparison describes package drift, not doctrinal movement.**

A diff between two immutable Editions is a factual statement about two packages:
these refs appear in one and not the other; this ref's reported status differs.
That is *transport drift*. It is **not** "newer is better," "this supersedes that,"
or "this is now current." Succession is a verdict, and verdicts live in Continuity
(reliance) or Maude (adjudication), never in a read-plane diff.

## Question

Can Spine compare two Editions and report exactly what differs **without** any of
the comparison — argument order, "added," a changed status — becoming a claim that
one Edition wins?

## Invariant

**Direction is a coordinate, not a verdict.** `compare A B` reports the set
difference *from A to B*: refs in B not in A are `added`, refs in A not in B are
`removed`, refs in both whose substance differs are `changed`. Calling them
base/target imposes an axis, not a value. Spine never says newer / older / latest /
current / canonical / supersedes / obsolete / better / recommended about either
Edition. That vocabulary is a *mechanical refusal* (`EditionSuccessionError`), not a
style guideline.

**Drift is substantive, not chronological.** Two Editions are observed at different
times by construction; an `entry_digest` includes `observed_at`, so comparing
digests would mark every entry "changed" and tell you nothing. A `changed` entry
means its *substance* moved — what the sign says, its source, its witness — not that
Spine looked at a different clock. Time lives in the edition metadata
(`base_created_at` vs `target_created_at`), never as per-entry "change."

## Allowed

- Read two existing, immutable Edition directories (their `edition.json` +
  `index.json`).
- Compute a pure, deterministic diff: added / removed / changed / unchanged, keyed
  on `canonical_location`, compared on substantive fields.
- Render the diff with a loud disclaimer and neutral (base/target, column-not-arrow)
  framing.
- Add a CLI verb: `spine edition compare <base_dir> <target_dir>`.
- Add a typed refusal that names the new laundering attempt (diff-asserts-succession)
  and a closed forbidden-framing vocabulary.

## Forbidden

- No "newer" / "older" / "latest" / "current canonical" / "supersedes" / "obsolete"
  / "deprecated" / "better" / "winner" / "recommended" in Spine's own framing of the
  diff. (Quoting an entry's already-sourced `reported_status` — e.g. the word
  `ratified` in a quotation — is not Spine's framing and is untouched.)
- No ranking, scoring, or "winner" field on the diff result.
- No mutation of either Edition (they are immutable; compare only reads).
- No new status vocabulary, no witness synthesis, no Continuity integration, no
  crawler. This slice adds a *read-over-two-frozen-packages* and nothing else.

## Exit (done when)

1. `diff_editions(base, target)` is pure and deterministic: same two Editions →
   identical `EditionDiff`.
2. added / removed / changed / unchanged are correct, keyed on `canonical_location`,
   compared on substantive fields (observation time excluded by design).
3. `diff_editions(E, E)` reports everything `unchanged`, nothing added/removed/changed.
4. The rendered diff carries the disclaimer and contains **none** of the forbidden
   succession framing; the mechanical guard (`check_no_succession_framing`) refuses
   any framing string that does.
5. The `EditionDiff` field set is closed and carries no ranking/winner/recommendation
   field.
6. CLI `spine edition compare` works against the two real editions under `editions/`.
7. No crawler, resolver, witness synthesis, Continuity integration, or status
   vocabulary introduced (the diff adds a comparison + render + one refusal type +
   tests, not machinery).

## After this (do NOT pull forward)

Continuity-as-source (REENTRY #4) is still later — only when there is a real
interface to replace. Binding real `witness_ref`s (REENTRY #5) waits until an
artifact earns a witness. A diff is the floor of succession pressure; the moment a
"which is current?" answer is wanted, that answer must come from a layer with
standing to give it — not from Spine widening this diff.
