# Spine — re-entry pointer (read this before "improving" anything)

> The rake is on the floor on purpose. In three days some agent — possibly
> wearing the maintainer's face — will try to make Spine *helpful*. **The villain
> is "helpful search." Shoot it early.**

## Current state

**`main` pushed through `6647ad2`.** Slice 1 shipped at `229a503`; Slice 1b
(Edition) at `6647ad2`. The first Edition of the predicate-witness specimen corpus
is committed under `editions/` (`sha256:fabb36a4…`, pinned in
`tests/test_edition_packaging.py`). **An Edition freezes what was *found*, not what
was *true* — it is a receipt for packaging, never a witness for legitimacy.**
Next campaign: corpus expansion (Slice 1c). Continuity source remains deferred.

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
4. **Replace `provisional_git_manifest_v0` with a Continuity source** — **NEXT**, but
   still deferred until there is a real interface to replace. Only once
   there's a real interface to replace (one manifest, one index, one edition, one
   corpus-expansion pain point) instead of plumbing on a hunch.
5. **Bind real `witness_ref`s** when artifacts actually earn a witness — then, and
   only then, the index may show "the sign says ratified" *with* its witness.

## Invalid work (the do-not list — this is the load-bearing section)

- ❌ a crawler / auto-discovery / repo walk (the adapter refuses crawl directives by design)
- ❌ doctrine adjudication (that is Maude's; Spine does not decide)
- ❌ ratification inference / status upgrade by Spine
- ❌ a "latest doctrine" / "current canonical" resolver
- ❌ witness synthesis
- ❌ edition-as-authority language (an Edition freezes what was *found*, not what was *true*)
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
