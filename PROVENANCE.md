# Provenance

This project is human-directed and AI-assisted. Final design authority,
acceptance criteria, and editorial control rest with the human author.
AI contributions were material and are categorized below by function.

## Human authorship

The author (James Beck) defined the project direction, the read-plane charter,
and the constellation boundary that Spine sits inside. AI systems contributed
proposals, drafts, and critique under author supervision; they did not
independently determine project goals or deployment decisions. The author
reviewed, revised, or rejected AI-generated output throughout.

## AI-assisted collaboration

### Charter and constellation boundary

The read-plane charter (`DOCTRINE.md`) and the name-collision resolution
(`NAMING.md`) were authored under the author's direction with AI assistance
(Claude, Anthropic; ChatGPT, OpenAI), drawing the boundary — Continuity governs
reliance, Maude governs adjudication, Spine governs read — before implementation.

### Predicate-witness doctrine pointer

The cross-constellation predicate-witness doctrine (`docs/predicate-witness-index-candidate.md`)
was distilled from a multi-model thread (Claude, ChatGPT, DeepSeek) under author
direction; the canonical capture lives in `agent_gov`
(`docs/cross-tool/predicate-witness-infrastructure-note.md`). Spine's entry
records only its read-plane refusal (findability ≠ legitimacy).

### Repository genesis

Lead collaboration: Claude (Anthropic) via Claude Code — repository
initialization, scaffolding (license/notice/agent guides), and the doctrine
pointer, under author direction.

## Provenance basis and limits

This document is a functional attribution record based on commit history,
co-author trailers, and documented working sessions. It is not a complete
forensic account. Model names/tools are recorded at the platform level; exact
versions vary across sessions. "Footguns avoided" and ideas that did not ship are
real contributions that leave no artifact and cannot be fully accounted for here.

## What this document does not claim

- No exact proportional attribution. Contributions are categorized by function,
  not quantified.
- Design and implementation are not cleanly sequential.

---

This document reflects the project state as of 2026-06-25 (repository genesis) and
will be revised as Spine is built.
