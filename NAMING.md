# NAMING

## Collision

The name **Spine** is used in two places in the constellation:

- **`governor.spine`** (Python module, shipped in `agent_gov`) — the locked
  project structure and proposal-verification machinery. Metaphorical:
  *spine as structural integrity of a bounded workspace.*
- **`~/git/spine`** (this repository) — the read plane over the governed
  corpus; see `DOCTRINE.md`. Architectural: *spine as the navigable
  structural layer of a corpus, in the book-spine and skeletal senses.*

Both uses grabbed the name independently for overlapping structural reasons.
The collision is emergent, not a mistake on either side.

## Resolution

This repository keeps the name **Spine**. The literal, reader-facing use has
the stronger claim on the plain noun; the `governor.spine` use is a pun on
structural support that will read more truly under a different name.

`governor.spine` is expected to rename eventually, but not on Spine's
timeline. Do not churn that module now; the collision is known, and that is
enough for today.

## Rule until `governor.spine` renames

To avoid a Python import-shadowing hazard in shared environments:

- No bare `spine` package or distribution name from this repository.
- If code ships here before `governor.spine` renames, the published package
  must be prefixed or qualified — e.g. `spine_readplane`, `spine_corpus`,
  `spine_tui`, `constellation_spine`. Public name in prose stays *Spine*;
  the Python artifact is what carries the prefix.

Once `governor.spine` renames, this constraint is lifted and the bare name
becomes available.

## Candidate replacement names for `governor.spine`

For when that side moves. These are truer to what the module actually does
(locked workspace, bounded project structure, anti-drift execution
envelope):

- `governor.workspace`
- `governor.boundary`
- `governor.lockspace`
- `governor.projectspace`
- `governor.scope`

Not endorsements — starting points, so the eventual rename has a list to
argue over rather than a blank page.
