# Specimen notes — `mixed_status_corpus.yaml` (Slice 1c)

The labels for the museum. This corpus is **not** a coherent doctrine family (that
is `predicate_witness_manifest.yaml`); it is a deliberately heterogeneous set
chosen to pressure one invariant:

> **Corpus expansion increases surface area, not authority.**

Inclusion, renderability, and Edition membership are navigational facts. None of
them is a status claim. Five specimens, each picked to test a different way the
wall could be breached:

| # | Artifact | Reported | What it tests |
|---|----------|----------|---------------|
| 1 | `spine:DOCTRINE.md` | `unknown` | A **canonical-feeling** charter that declares no quotable status. Spine reports `unknown` — it does **not** promote "foundational-looking" into "governed". Importance ≠ authority. |
| 2 | `agent_gov:docs/doctrine/weak_property_strong_property.md` | `candidate` | A **doctrine-shaped** note that self-declares candidate. Doctrine-shaped ≠ doctrine-authoritative. |
| 3 | `spine:docs/campaigns/slice-1-doctrine-index/CAMPAIGN.md` | `non-binding` | A **process / campaign** artifact ("carded, pre-code"). A plan is not a governing surface. |
| 4 | `agent_gov:working/candidate-laundering-braid.md` | `candidate` | A deliberately **non-authoritative** working note. |
| 5 | `agent_gov:working/parked-p31-activation.md` | `non-binding` | **The museum label.** An openly PARKED, uncommitted draft. Spine carries obsolete material without laundering it into "current". *Included is not current.* |

## Faithful quotation, closed vocabulary

`reported_status` is Spine's closed set `{ratified, candidate, non-binding,
unknown}`. Two specimens self-declare a status outside that set:

- #3 declares **"carded, pre-code"**
- #5 declares **"PARKED 2026-06-13, uncommitted"**

Both are normalized to `non-binding` — the nearest **non-authoritative** bucket.
The normalization is **downgrade-only** (never toward authority) and the verbatim
self-declaration is preserved in `status_source_ref`, so nothing is hidden. This is
quotation under a closed vocabulary, not adjudication: Spine is not *deciding* these
docs are non-binding, it is *reporting* a non-authority self-declaration it has no
authoritative slot for.

## What is deliberately absent

- **No `ratified` entries.** Docs that self-declare `status: ratified` (e.g. the
  `agent_gov` validator decisions) are *excluded*, because a governed claim needs a
  `witness_ref` and **no artifact in the constellation has yet earned a witness**.
  Binding one would be witness synthesis — forbidden in Slice 1c, deferred to
  REENTRY #5. The wall refusing a witnessless `ratified` is the design working, not
  a gap.
- **No witnesses.** `witness_ref: null` everywhere, exactly like the genesis family.

## Editions

- Edition 1 (genesis predicate-witness family): `sha256:fabb36a4…` — frozen.
- Edition 2 (this corpus, `--created-at 2026-06-27T00:00:00Z`):
  `sha256:b94f0442…` — frozen, distinct, and asserting only `located` / `rendered`.

The genesis manifest and Edition 1 are untouched. Spine now carries two declared
corpora and two immutable Editions; its authority remains exactly zero.
