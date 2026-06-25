# CLAUDE.md — Instructions for Claude Code

Start with [`AGENTS.md`](AGENTS.md) (the agent-neutral travel guide) and
[`DOCTRINE.md`](DOCTRINE.md) (the charter). This file adds only the
Claude-specific emphasis.

## The one thing to hold

Spine is the **read plane**: *findability is not legitimacy.* The whole repo
exists to make governed material navigable **without** letting navigability
masquerade as authority. Every design instinct that wants the index to "just
also decide / certify / vouch" is the failure mode. When you feel it, stop and
name the boundary — the answer is almost always "that belongs in Continuity
(reliance) or Maude (adjudication), not here."

## Apply the constellation's own discipline

- **Don't claim a file exists without checking; don't claim tests pass without
  running them.** (No test suite yet — say so plainly rather than implying one.)
- **Cite receipts, not vibes.** When Spine eventually presents an artifact's
  witness/provenance, present the real reference, never a summary that reads as a
  warrant.
- **Read-plane refusal in the predicate-witness chain:** indexing a predicate
  does not make it true. See `docs/predicate-witness-index-candidate.md`;
  canonical note in `agent_gov` `docs/cross-tool/predicate-witness-infrastructure-note.md`.

## Where things are

- `DOCTRINE.md` — what Spine is allowed to be (the boundary).
- `NAMING.md` — the `governor.spine` / `~/git/spine` name collision + resolution.
- `docs/` — doctrine pointers and (later) design notes.

## Status

Charter fixed; implementation not started. Slice 1 is the navigable index over the
governed corpus; the build system/stack is chosen with it. Do not scaffold a stack
before that decision is made with the user.
