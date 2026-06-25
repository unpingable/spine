# Spine

**The read plane of the constellation.** Spine makes a corpus of governed
material navigable, legible, and durable for readers — including strangers —
**without requiring oral tradition.**

> Continuity governs what can be relied on. Maude governs what must be decided.
> **Spine governs what can be found and read.**

See [`DOCTRINE.md`](DOCTRINE.md) for what Spine is allowed to be, and
[`NAMING.md`](NAMING.md) for the `governor.spine` / `~/git/spine` name collision
and its resolution.

## Position in the constellation

Spine **depends on Continuity** (the semantic substrate — what can be relied on);
Continuity does not depend on Spine. Spine may arrange, package, and present
governed material; it **does not originate canonical semantic state**, and it
**does not adjudicate** (that is Maude's). Maude is the upstream path for
adjudicated material destined for publication, but not the sole ingress —
imported documents, external references, generated indexes, and editions
assembled from already-governed material may enter Spine directly.

## The read-plane discipline (load-bearing)

A read plane has one temptation it must refuse:

> **Findability is not legitimacy. Indexing a thing does not make it true.**

Spine can help you *find* a governed artifact, its provenance, and its witness; it
cannot *authorize* the artifact, and a thing being well-presented, frequently
linked, or easy to reach is not a warrant. (The PageRank lesson, read backwards:
graph position confers navigability, never authority.) See
[`docs/predicate-witness-index-candidate.md`](docs/predicate-witness-index-candidate.md)
for this refusal in the cross-constellation predicate-witness chain; the canonical
note lives in `agent_gov` at `docs/cross-tool/predicate-witness-infrastructure-note.md`.

## Status

Early. The charter is fixed; the implementation is not yet started. The first
slice is the navigable index over the governed corpus — the read plane's reason
to exist. Build system and stack are TBD and chosen with that first slice.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
Provenance (human-directed, AI-assisted): [`PROVENANCE.md`](PROVENANCE.md).
