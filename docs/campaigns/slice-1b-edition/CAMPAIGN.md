# Campaign — Spine Slice 1b: an Edition freezes navigation, not authority

Status: **carded, pre-code** (2026-06-25). A bounded follow-on to Slice 1, not
Slice 2. Still read-plane. Still no authority. Card before code.

## The one line

> **Freezing an index preserves what was found; it does not promote what was found.**

An Edition is an immutable, content-addressed snapshot of a navigational render —
a stable *citation target*. It gives the corpus a thing you can point at that
won't move. It does **not** turn the frozen package into a governance claim.

## Question

Can Spine produce an immutable, reproducible **Edition** of a navigational index
**without** turning the frozen package into a governance claim?

## Invariant

**An Edition freezes what Spine *located*; it does not ratify what Spine
*located*.** The Slice 1 wall carries through unchanged: every entry inside an
Edition still asserts only `located` / `rendered`, still quotes `reported_status`
from a source, still marks unwitnessed material loudly. Freezing adds
*immutability + citability*, never *authority*.

## The object (sketch — not a build spec)

```
Edition {
  edition_id            # content hash over the digests below (the citation target)
  created_at            # explicit, supplied (determinism)
  manifest_digest       # the declared manifest that was read
  index_digest          # the deterministic SpineIndex (Slice 1)
  render_digest         # the rendered markdown/json output
  ingress_adapter       # provisional_git_manifest_v0 (recorded, retires later)
  build_provenance      # the exact command/inputs that reproduce it
  spine_assertions      # ["located", "rendered"]  <- still only these
}
```

`spine_assertions` on the Edition is the same humiliating pair. An Edition that
ever carried a legitimacy verb (ratified / governed / canonical) would be the wall
falling at the package layer.

## Allowed

- Content-address the current manifest, generated index, and rendered output.
- Emit Edition metadata (the digests + provenance above).
- Record the build command / inputs so the Edition is reproducible from repo state.
- Write each Edition to its own immutable directory (keyed by `edition_id` /
  `created_at`), never overwriting a prior one.

## Forbidden

- No ratification; no status upgrade inside or by the Edition.
- No "current canonical doctrine" / "latest edition wins" resolution.
- No witness synthesis.
- No mutable overwrite of a prior Edition (immutability is the point).
- No edition-as-authority language anywhere in output or metadata.

## Exit (done when)

1. `spine edition create <manifest> --created-at <iso> --out <dir>` exists.
2. It writes a **deterministic** edition directory (same inputs + same
   `created_at` → byte-identical edition, stable `edition_id`).
3. The Edition records the manifest / index / render digests + build provenance.
4. Tests prove an Edition **preserves** reported status but **cannot create**
   status — and that `spine_assertions` on the Edition never holds a legitimacy
   verb.
5. A first Edition is generated for the predicate-witness specimen corpus.

## After this (do NOT pull forward)

Only after the first Edition exists: expand the declared corpus (one published
edition of the tiny corpus *first*, then expand). Continuity-as-source comes later
still — when there's a real interface to replace, not plumbing on a hunch. A public
"Stele" / rendered page is even later. First Edition. Then the rest.
