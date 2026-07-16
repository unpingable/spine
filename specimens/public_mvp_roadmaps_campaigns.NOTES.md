# public_mvp_roadmaps_campaigns — specimen notes (Packet S-B)

**What this is.** A hand-declared corpus over agent_gov's real planning
surface: the 4 roadmap hub files, all 18 per-tool roadmaps, and every
campaign `CAMPAIGN.md` / `STATUS.md` that exists (41 artifacts). Frozen as
edition `sha256:b9b16649…d504d` at the fixed edition timestamp
`2026-07-16T00:00:00Z`.

**Why it exists.** The public-mvp stranger should be able to *navigate* the
constellation's planning docs without oral tradition — and see, on every
row, exactly what Spine does and does not claim. This corpus is the first to
exercise all three status lanes at once:

| lane | count | example |
|---|---|---|
| governed claim, witnessed, quoted | 6 | `tools/nq.md` — "the sign says **ratified** ⚠ governed-claim" + verbatim wording + witness ref |
| candidate, quoted | 13 | `tools/spine.md` — DRAFT normalized downgrade-only to candidate, wording preserved |
| unknown + verbatim quote (**the honest middle**) | 9 | `ROUTING.md` — the sign says "NORMATIVE", which is not in the closed vocabulary; Spine shows the words and declines the normalization |
| unknown, bare | 13 | campaign `STATUS.md` files — a title is not a status declaration |

**The middle lane is the point.** Before the OQ-2 ruling (2026-07-16) a doc
whose sign said `NORMATIVE` or `LIVE HUB` could only appear as a bare
`unknown` — the wording was silently discarded, which is quotation laundered
into (non-)assertion by omission. With `status_quote`, normalization and
quotation sit side by side and the reader can audit the mapping themselves.

**Witness policy.** The six `ratified` entries point their `witness_ref` at
the executed-A8 / Q-A7 record
(`agent_gov:working/handoff-2026-07-02-roadmap-program.md`). Spine does not
verify witnesses — it locates them. `ROUTING.md`'s "NORMATIVE" was
deliberately **not** promoted to `ratified`: no witness was declared, and
importance is not authority.

**Cross-repo nod (OQ-2 ruling).** Every `repo:` here is `agent_gov`, indexed
from the spine repo, which vendors none of it. Navigationally legal by
ruling: location is a coordinate, never custody. The corpus references the
sibling's files by name; nothing is copied, crawled, or resolved.

**What this corpus does NOT do.** No discovery (all 41 enumerated by hand);
no "latest" or succession claims; no doctrine resolution; no witness
synthesis; no authority-from-inclusion. Being indexed here says nothing
about a doc being true, current, or governed — including the six that quote
RATIFIED signs.

**Reproduce.** `spine edition create specimens/public_mvp_roadmaps_campaigns.yaml
--created-at 2026-07-16T00:00:00Z --out editions` re-derives the same
`edition_id`; `tests/test_public_mvp_corpus.py` pins identity, counts,
lanes, and the navigational-only invariant.
