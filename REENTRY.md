# Spine — re-entry pointer (read this before "improving" anything)

> The rake is on the floor on purpose. In three days some agent — possibly
> wearing the maintainer's face — will try to make Spine *helpful*. **The villain
> is "helpful search." Shoot it early.**

## Current state

**Slices 1 / 1b / 1c / 1d shipped.** Slice 1 at `229a503`; Slice 1b (Edition) at
`6647ad2`; Slice 1c (corpus expansion) at `3ccc5cd`; Slice 1d (edition compare) is
the latest commit. Two Editions of the specimen corpus are committed under
`editions/` (Edition 1 `sha256:fabb36a4…` pinned in
`tests/test_edition_packaging.py`; Edition 2 `sha256:b94f0442…` over the
heterogeneous `mixed_status_corpus`). **An Edition freezes what was *found*, not what
was *true* — it is a receipt for packaging, never a witness for legitimacy.** Now
that two Editions exist, `spine edition compare` describes the **drift** between
them — added / removed / changed / unchanged — and mechanically refuses to say which
is newer, current, or supersedes the other (`EditionSuccessionError`). **Slice 2a
defined the declaration-source throat** (`src/spine/source.py` — `DeclarationSource`
/ `DeclaredManifest` / `SourceProvenance`), wrapping the existing manifest; the
Continuity-as-source arc now breathes through that interface (2b fixture → 2c real
adapter → 2d retire the provisional manifest), instead of plugging Continuity
straight into Spine. Continuity source remains the final destination.

Spine is a **read plane** over a *declared provisional git manifest*. It:

- **may** locate and render artifact references;
- **may** quote a `reported_status` **only** when bound to a `status_source_ref`;
- **may not** assign status, synthesize witnesses, crawl repositories, or promote
  anything by the act of indexing it.

The one invariant, which is the whole repo:

> **Spine indexes status-bearing objects; it does not bear status.**
> "The sign says ratified" is not "ratified." Findability is not legitimacy.

## Current ingress adapter

```
provisional_git_manifest_v0
```

**Intentionally temporary.** It reads declared, concrete file references and is
*incapable of crawling* (globs / directories / recurse are refused, not executed).
It **retires when Continuity becomes the source** — the final architecture is
Spine-reads-from-Continuity; the git manifest is a specimen, not a destination.

## Next valid work (in order; see `docs/campaigns/`)

1. ~~**Slice 1b — Edition:**~~ **DONE.** Immutable, content-addressed snapshot of a
   render (manifest + index + render digests + provenance). Freezes navigation,
   not authority. `spine edition create … --created-at … --out …`.
2. ~~**First edition** of the predicate-witness specimen corpus.~~ **DONE** —
   committed under `editions/`.
3. ~~**Expand the declared corpus** (Slice 1c).~~ **DONE.** A second, heterogeneous
   declared corpus (`specimens/mixed_status_corpus.yaml`, 5 refs spanning
   canonical-feel / candidate / non-binding / unknown) + Edition 2
   (`sha256:b94f0442…`). Genesis family + Edition 1 left frozen. Proved: inclusion,
   renderability, and Edition membership confer no authority; an obsolete (PARKED)
   doc is carried without being laundered into "current". See
   `specimens/mixed_status_corpus.NOTES.md`.
4. ~~**Compare editions** (Slice 1d).~~ **DONE.** `spine edition compare <base> <target>`
   + `src/spine/edition_diff.py`. Reports added / removed / changed / unchanged keyed
   on `canonical_location`, compared on *substantive* fields (observation time
   excluded — two editions are observed at different times by construction, so a
   digest diff would mark everything changed and say nothing). Mechanically refuses
   succession framing (`EditionSuccessionError` + closed `SUCCESSION_FRAMING`). Loads
   only intact, untampered packages (`EditionLoadError` on `index_digest` mismatch).
   The diff has no winner/latest/current/rank field — the closed field set is the
   wall. See `docs/campaigns/slice-1d-edition-compare/CAMPAIGN.md`.
5. **Continuity-as-source arc.** The *throat is now defined* — don't plug Continuity
   straight in; let it breathe through the interface.
   - ~~**Slice 2a — Declaration Source Interface v0.**~~ **DONE.**
     `src/spine/source.py`: `DeclarationSource` (Protocol, verb `declare()`),
     `DeclaredManifest`, `SourceProvenance` (closed, no authority field),
     `ProvisionalGitManifestSource` wrapping the existing manifest. The throat is
     transparent (index byte-identical via source vs `load_manifest`) and a source
     declaring a witnessless `ratified` ref is still refused at index-build — a
     source declares candidates for location, it confers no standing.
     `docs/campaigns/slice-2a-declaration-source/CAMPAIGN.md`.
   - ~~**Slice 2b — Continuity-shaped static fixture.**~~ **DONE.**
     `tests/fixtures/continuity_export_shape_v0.json` (grounded on real Continuity's
     `continuity.receipt.v0` + `MemoryObject` shape, @ `aab46ec`) +
     `src/spine/continuity_fixture.py` (`ContinuityExportFixtureSource`). Continuity
     declares LOCATION, not STATUS: every ref lands `unknown`, the lifecycle
     (status/reliance_class/supersedes) is quarantined into `status_source_ref`
     ("NOT Spine standing"), foreign authority fields (canonical/ratified/authority/
     latest/current) are rejected. No `continuity` import, no subprocess (AST-guarded).
     `docs/campaigns/slice-2b-continuity-fixture/CAMPAIGN.md`.
   - **Slice 2c — real Continuity adapter** — **NEXT.** The forcing case for a
     content-based `build_edition` (a real export has no file path — see the 2a
     known-seam note). Still no authority/recency/ratification/witness from Continuity.
   - **Slice 2d — retire the provisional manifest** as *transport replacement, not
     authority change* (`retirement_kind: transport_replacement`).
6. **Bind real `witness_ref`s** when artifacts actually earn a witness — then, and
   only then, the index may show "the sign says ratified" *with* its witness.

## Invalid work (the do-not list — this is the load-bearing section)

- ❌ a crawler / auto-discovery / repo walk (the adapter refuses crawl directives by design)
- ❌ doctrine adjudication (that is Maude's; Spine does not decide)
- ❌ ratification inference / status upgrade by Spine
- ❌ a "latest doctrine" / "current canonical" resolver
- ❌ witness synthesis
- ❌ edition-as-authority language (an Edition freezes what was *found*, not what was *true*)
- ❌ edition-diff succession language — a diff says *added / removed / changed*, never
  *newer / current / supersedes / latest*. "Which edition is current?" is a verdict
  for Continuity or Maude; the diff is refused (`EditionSuccessionError`) if it tries.
- ❌ mutable overwrite of a prior edition

If a proposed feature would let an index entry, an edition, or a render stand in
for a witness, a verdict, or a grant — **stop. That belongs in Continuity
(reliance) or Maude (adjudication), not here.**

## The shape to keep in your head

```
Index    = mutable navigational aid
Edition  = immutable timestamped package (Slice 1b)
Witness  = authority/custody pointer that lives ELSEWHERE
```

Spine carries the first two. It never becomes the third.
