# Campaign — Spine Slice 1: the doctrine index (read plane, first cut)

Status: **carded, pre-code** (2026-06-25). The first implementation slice of the
Spine read plane. Card before code, per constellation discipline.

## The one line (load-bearing — this is the whole repo)

> **Spine indexes status-bearing objects; it does not bear status.**
>
> Spine can say *"the sign says ratified."* Spine cannot say *"ratified."*

A Spine index entry is a **mutable navigational record**. It may *point to*
canonical material, *report* a status (bound to a source), and *reference* a
witness — but it never certifies, ratifies, promotes, supersedes, adjudicates, or
makes anything true by indexing it. **Index presence confers no status.**

## Question

Can Spine make a *declared* cross-repo doctrine corpus findable **without** making
index presence, reported status, or presentation order look like authority?

## Invariant

**Findability is not legitimacy.** Every entry is navigational. The wall is in the
object model: Spine asserts only `located` / `rendered`, never `ratified` /
`governed` / `valid`. Reported status exists only as a *quotation* of a named
source, never as a Spine field of its own.

## Corpus boundary (the architectural call)

- **Final architecture (doctrine):** Spine reads from **Continuity**. Continuity
  custodies governed material; Spine reads and presents it.
- **Slice 1 reality:** Continuity does not yet custody the live doctrine (it sits
  in git-backed `docs/` across the sibling repos). So Slice 1 reads a **declared
  manifest** of git-backed artifact references.
- **The bridge is named ugly on purpose:** **`provisional_git_manifest_v0`**. The
  name must *smell temporary* so future-you doesn't find a polished abstraction and
  assume it was doctrine-blessed. It is provisional, explicit, narrow, and
  **incapable of crawling**. It is retired when Continuity becomes the source.

> The manifest bridge is not a compromise. It is a specimen.

## The object model (the wall, made mechanical)

An index entry is **not**:

```json
{ "canonical_location": "...", "status": "ratified", "witness_ref": "..." }
```

It is:

```json
{
  "canonical_location": "...",
  "reported_status": "ratified | candidate | non-binding | unknown",
  "status_source_ref": "<ref to the surface that reported the status>",
  "witness_ref": "<ref to admissibility evidence, or null>",
  "ingress_adapter": "provisional_git_manifest_v0",
  "observed_at": "<iso8601>",
  "entry_digest": "<content hash of the entry>",
  "spine_assertions": ["located", "rendered"]
}
```

`spine_assertions` is boring and humiliating on purpose — only `located` /
`rendered`. If it ever contains `ratified` / `governed` / `valid`, the wall has
fallen. `reported_status` is meaningless without `status_source_ref`: Spine may
report what the governing surface says; it may not *become* the surface saying it.

## Allowed

- Read from a **declared manifest** of artifact references (checked in).
- Emit a **deterministic** navigable index of canonical locations.
- Display `reported_status` **only** when bound to a `status_source_ref` (or a
  `witness_ref`).
- Index candidate / unwitnessed material **only** with an explicit
  non-authoritative marker.
- Preserve source identity, `entry_digest`, `observed_at`, and `ingress_adapter`
  provenance on every entry.
- One narrow specimen corpus: the **predicate-witness / admissibility doctrine
  family** currently scattered across the sibling repos (AG canonical note + the
  six pointer files, 2026-06-25).

## Forbidden

- No repo crawling. (The adapter cannot discover; it only reads the manifest.)
- No "latest doctrine" inference.
- No promotion from candidate to ratified.
- No status **assignment** by Spine (only quotation of a source).
- No witness synthesis.
- No treating a broken/missing witness as a soft warning **if the entry claims
  governed status** — that is a hard refusal.
- No Continuity-shaped language unless Continuity actually backed the object.
- No fallback where "present in index" means "safe to cite as authoritative."

## Exit (done when)

1. A checked-in manifest declares a small artifact set (the predicate-witness family).
2. Spine builds a **deterministic** index from that manifest.
3. Every entry carries a canonical location **plus either** a witness/status-source
   reference **or** an explicit `candidate / unwitnessed` marker.
4. The rendered/public view makes the refusal **visible** (the sign-says framing).
5. Tests prove an entry **cannot** claim `ratified`/`governed` status without the
   required witness/status-source reference, and that `spine_assertions` never
   contains a legitimacy verb.
6. The adapter is named `provisional_git_manifest_v0` and marked provisional until
   Continuity becomes the source.

## Open (decide before code)

- **Stack.** Deferred to this slice. Default lean: **Python** (low-friction over
  the existing markdown corpus, matches `agent_gov`). Alternative: **Rust** for
  kernel-idiom coherence with `standing` / `wicket`. Pick before scaffolding.

## Specimen corpus (the first manifest)

The predicate-witness family, already assembled by hand on 2026-06-25 (the symptom
that justified the read plane):

- canonical: `agent_gov` `docs/cross-tool/predicate-witness-infrastructure-note.md`
  (reported: non-binding candidate; witness: none yet — marked unwitnessed)
- pointers (each reported candidate/non-binding, status_source = the note's own header):
  `nq` `docs/working/decisions/PREDICATE_WITNESS_POINTER_CANDIDATE.md` ·
  `wicket` `docs/predicate-admissibility-candidate.md` ·
  `standing` `docs/predicate-no-authority-from-satisfaction-candidate.md` ·
  `continuity` `docs/candidates/PREDICATE_WITNESS_POINTER.md` ·
  `linearaccountant` `docs/working/predicate-legitimacy-not-from-proof-candidate.md` ·
  `spine` `docs/predicate-witness-index-candidate.md`

Indexing this set proves the wall: not one of them is ratified, and the index must
show that — *located and rendered, candidate and unwitnessed*, never promoted by
the act of being found.
