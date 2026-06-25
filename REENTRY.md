# Spine — re-entry pointer (read this before "improving" anything)

> The rake is on the floor on purpose. In three days some agent — possibly
> wearing the maintainer's face — will try to make Spine *helpful*. **The villain
> is "helpful search." Shoot it early.**

## Current state

Slice 1 shipped at **`229a503`**.

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

1. **Slice 1b — Edition:** an immutable, content-addressed snapshot of a render
   (manifest + index + output digests + provenance). *Freezes navigation, not
   authority.*
2. **First edition** of the tiny predicate-witness specimen corpus.
3. **Expand the declared corpus** — only *after* an Edition exists (otherwise
   "richer corpus" becomes the scatter trap).
4. **Replace `provisional_git_manifest_v0` with a Continuity source** — only once
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
