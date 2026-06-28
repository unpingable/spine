# Campaign — Spine Slice 2a: Declaration Source Interface v0

Status: **SHIPPED** (2026-06-28). The first move of the Continuity-as-source
arc — and deliberately **not** Continuity. We define the *throat* first, then later
let Continuity breathe through it. The phrase "Continuity integration" has cocaine
in it; it invites architecture goblins. This slice is named ugly on purpose.

## Exit ticket (2026-06-28)

All six exit criteria met. `src/spine/source.py`: `DeclarationSource` (a
`runtime_checkable` Protocol, one verb `declare()`), `DeclaredManifest`
(manifest + provenance, closed), `SourceProvenance` (source_kind / source_ref /
export_digest / declared_at — closed, no authority field), and
`ProvisionalGitManifestSource` wrapping the existing `load_manifest` (reads bytes
once, digests the exact declared bytes). 122 tests pass (10 new in
`tests/test_declaration_source.py`). The throat is transparent:
`build_index(source.declare().manifest, …)` is byte-identical to
`build_index(load_manifest(path), …)`, and the source's `export_digest` equals the
Edition's `manifest_digest` (same bytes, one truth). The load-bearing test holds: a
source declaring a witnessless `ratified` ref is refused at index-build
(`UnwitnessedGovernedClaimError`) — declaring is not conferring; standing cannot
ride in on provenance. The crawl fence still fires at `declare()`.

The forbidden list held: no latest resolver, no crawling, no current-doctrine, no
supersedes, no ranking, no witness synthesis, no authority field on provenance, no
live Continuity / fixture / `build_edition` refactor. The 2c content-build seam is
filed below, named not built.

Next: Slice 2b (Continuity-shaped static fixture) — prove Spine consumes a
Continuity-shaped declaration without needing Continuity itself.

## The one line

> **A source declares candidates for location. It does not confer standing.**

## Question

Can we name the smallest abstraction —

```
DeclarationSource -> DeclaredManifest
```

— such that *where a declaration came from* is recorded as provenance, while the
declaration confers **no** authority, recency, ratification, or standing on the refs
it names? The first implementation must just wrap the existing provisional git
manifest: dull, antiseptic, no new external dependency.

## Invariant

**A source answers only "here are refs Spine should attempt to locate, and here is
where that declaration came from."** It must NOT answer: which ref is authoritative
/ current / supersedes another / is doctrine / should be trusted. The closed field
set of `SourceProvenance` (no authority/latest/current/ratified/supersedes/witness
field) is the wall — same discipline as the Edition-diff field set in 1d.

**The deep guarantee is already free.** Every declared ref still flows through
`build_index` → `build_entry` → `check_entry_admissible`. A source that declares a
`ratified` ref without a witness is refused at index-build *regardless of what the
source claims* — so "Continuity says, therefore authority" is structurally
impossible, not merely discouraged. This slice pins that as its load-bearing test.

## Allowed

- Define `DeclarationSource` (the interface) + `DeclaredManifest` + `SourceProvenance`.
- Implement `ProvisionalGitManifestSource` — wraps the existing `load_manifest`,
  records source provenance (kind, ref, export digest).
- Prove the existing Index / Render / Edition pipeline consumes `declared.manifest`
  byte-identically to `load_manifest` (the throat changes nothing downstream).
- Test that Spine still asserts only `located` / `rendered`, and that a source
  declaring a witnessless governed claim is refused at index-build.

## Forbidden

- No "latest" resolver. No crawling. No "current doctrine". No supersedes. No
  ranking. No witness synthesis. No "Continuity says therefore authority".
- No authority/recency/ratification field on `SourceProvenance`.
- No live Continuity, no Continuity-shaped fixture (that is 2b), no real adapter
  (2c). This slice is the interface, proven against the manifest we already have.

## Known seam (named, not built — for 2c)

`build_edition` reads manifest **bytes from a path**. A real Continuity export has
no file path — it is content. Threading a content-based build (digesting the bytes
a source hands over, not a file it points at) is the forcing case that arrives with
**Slice 2c**, not now. 2a deliberately does not refactor `build_edition`: the
provisional source wraps a file, so the existing path-based Edition build is exact.
Filing the seam here so it is a handle for review, not a surprise.

## Exit (done when)

1. `DeclarationSource` / `DeclaredManifest` / `SourceProvenance` exist, frozen,
   `extra="forbid"`.
2. `ProvisionalGitManifestSource.declare()` returns a `DeclaredManifest` whose
   `manifest` equals `load_manifest(path)` and whose provenance records source kind
   + ref + a content digest over the declared bytes.
3. `build_index(source.declare().manifest, …)` is byte-identical to
   `build_index(load_manifest(path), …)` — the throat is transparent.
4. `SourceProvenance` field set is closed and carries no authority/latest/current/
   ratified/supersedes/witness field (a test pins it).
5. A source declaring a witnessless `ratified` ref is refused at index-build
   (`UnwitnessedGovernedClaimError`) — the source confers no standing.
6. No CLI, no Continuity, no fixture, no `build_edition` refactor (2b/2c hold).

## After this (do NOT pull forward)

2b (Continuity-shaped static fixture) → 2c (real Continuity adapter) → 2d (retire
the provisional manifest as *transport replacement, not authority change*) → public
Edition reader. Do not skip 2a/2b: that is where the doctrine-washing bugs hide,
wearing little "integration" badges.
