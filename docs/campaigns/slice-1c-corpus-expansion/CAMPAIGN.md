# Campaign — Spine Slice 1c: corpus expansion as specimen intake

Status: **SHIPPED** (2026-06-27). A bounded follow-on to Slice 1b. Still
read-plane. Still no authority. Specimen intake, **not architecture**.

## Exit ticket (2026-06-27)

All five exit criteria met. 5 new declared refs in `specimens/mixed_status_corpus.yaml`
(each a real file with a faithfully-quoted self-declared status); deterministic
rebuild; Edition 2 minted (`sha256:b94f0442…`), immutable and distinct from
Edition 1 (`sha256:fabb36a4…`); specimen labels in
`specimens/mixed_status_corpus.NOTES.md`. 75 tests pass (9 new in
`tests/test_corpus_expansion.py`), including the museum-label case (PARKED doc
carried as non-binding with no "current"/authority verb) and the importance-≠-authority
case (`spine:DOCTRINE.md` reported `unknown`, not assumed canonical).

The forbidden list held: the diff is **data + one manifest + notes + tests**, no
machinery — no crawler, no resolver, no automatic import, no witness synthesis, no
Continuity integration, no authority-from-inclusion. Docs self-declaring
`status: ratified` were *excluded* rather than witness-bound (the wall refusing a
witnessless governed claim is the design working; witness binding stays at
REENTRY #5). The genesis family and Edition 1 are untouched and still reproducible.

Next: REENTRY #4 (Continuity as source) — still deferred until a real interface
exists to replace.

## The one line

> **Corpus expansion increases surface area, not authority.**

Spine should be able to carry a *larger, more heterogeneous* declared corpus —
including material that looks canonical and material that is openly obsolete —
without inclusion, renderability, or edition membership becoming a status claim. A
museum carries a forgery and a masterpiece on the same wall; the *label* does the
work, not the act of hanging.

## Question

Can Spine carry a larger declared corpus without treating **inclusion**,
**renderability**, or **edition membership** as authority?

## Invariant

**Being in the corpus says nothing about being true, current, or governed.** Every
new entry still asserts only `located` / `rendered`, still quotes its
`reported_status` from a source (or honestly says `unknown`), still marks
unwitnessed material loudly. A doc that is *widely treated as canonical* but
carries no witness is reported exactly as honestly as a deprecated note: neither is
laundered by Spine into "current doctrine."

## Specimen selection (pressure the boundary, don't landfill)

A **small** set — 3–5 declared refs — chosen to test the wall, not to be
comprehensive:

- one **canonical-feeling** doctrine doc (importance ≠ authority — Spine still
  reports its self-declared status, or `unknown` if it declares none);
- one **campaign / specimen** doc (a process artifact, not a governing surface);
- one deliberately **non-authoritative** working note;
- one **deprecated / superseded** doc — the load-bearing specimen: *included ≠
  current*. Spine must carry old material without promoting it. Museum label, not
  papal seal.

Every declared ref points at a **real** file whose self-declared status is quoted
faithfully (checked, not invented). In a constellation where nothing has yet earned
a witness, that means every entry lands as `candidate` / `non-binding` / `unknown`
— and that honesty *is* the demonstration.

## Allowed

- Add a small number of declared manifest entries (new corpus manifest; the
  genesis predicate-witness manifest + Edition 1 stay frozen and reproducible).
- Rebuild index / render deterministically.
- Mint a new Edition (Edition 2) of the expanded corpus.
- Add specimen notes saying what was included and why (the labels).

## Forbidden

- No discovery / crawling (the adapter is still incapable of it).
- No "latest" / "current canonical" resolver.
- No doctrine resolver; no ratification inference from inclusion.
- No automatic corpus import.
- No Continuity integration (it stays outside the room).
- No new status vocabulary or witness synthesis to "fit" a canonical-looking doc —
  if it has no witness, it has no witness.

## Exit (done when)

1. N (3–5) new declared refs added to a corpus manifest, each pointing at a real
   file with a faithfully-quoted self-declared status.
2. Index / render regenerated deterministically (same inputs + same `created_at`
   → byte-identical).
3. One new Edition minted (Edition 2), immutable and distinct from Edition 1.
4. Tests prove all assertions remain `located` / `rendered` only, and that a
   deprecated/obsolete entry is carried **without** any "current"/authority verb.
5. No crawler, resolver, witness synthesis, or ratification inference introduced
   (the forbidden list holds; the diff adds data + one manifest + tests, not
   machinery).

## After this (do NOT pull forward)

Continuity-as-source (REENTRY #4) is still later — only when there is a real
interface to replace, not plumbing on a hunch. Binding real `witness_ref`s
(REENTRY #5) waits until an artifact actually earns a witness. Slice 1c adds
*surface area*, nothing else.
