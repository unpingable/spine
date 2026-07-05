# AGENTS.md — Working in this repo

This file is a **travel guide**, not a law.
If anything here conflicts with the user's explicit instructions, the user wins.

> Instruction files shape behavior; the user determines direction.

---

## What Spine is (read this first)

Spine is the **read plane** of the constellation — it makes governed material
**findable and legible**, nothing more. Before proposing any change, read
[`DOCTRINE.md`](DOCTRINE.md). The charter is the boundary; it was drawn first on
purpose.

The non-negotiable discipline:

- **Findability is not legitimacy.** Spine helps you *find* a governed artifact;
  it never *authorizes* one. Do not build anything that lets an index entry stand
  in for a witness, a verdict, or a grant.
- **Spine does not originate canonical semantic state.** That is Continuity's.
- **Spine does not adjudicate.** That is Maude's.
- Spine reads from already-governed material and presents it. If a feature would
  make Spine *decide* or *certify* something, it belongs in another plane.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/spine build specimens/predicate_witness_manifest.yaml \
    --observed-at 2026-07-05T00:00:00Z --out output/index.json
.venv/bin/spine render output/index.json
```

## Tests

.venv/bin/python -m pytest -q   # 141 tests at v0
**Never claim tests pass without running them.**

---

## Safety and irreversibility

### Do not do these without explicit user confirmation
- Push to remote, create/close PRs or issues
- Delete or rewrite git history
- Add or change a build system / dependency lockfile
- Anything that makes Spine originate or adjudicate state (charter violation)

### Preferred workflow
- Small, reviewable steps. Run any checks locally before proposing commits.
- Keep the charter honest: if a change blurs read-plane vs. semantic/adjudication
  planes, stop and name the boundary instead of crossing it.

## Provenance

This project is human-directed and AI-assisted; see [`PROVENANCE.md`](PROVENANCE.md).
Record material AI contributions there as the repo grows.

## Constellation conventions

- Apache-2.0; SPDX headers on source once a stack exists.
- `.mcp.json` and `.claude/settings.local.json` are local — gitignored, never
  committed (they carry machine paths and principal identity).
- Cross-repo doctrine candidates follow the constellation filing idiom: the
  filing is authorized by `agent_gov` as custody root; the home repo owns the
  doctrine. See `agent_gov` `docs/cross-tool/managed-repo-candidate-filing-note.md`.
