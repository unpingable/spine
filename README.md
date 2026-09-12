# Spine

**The read plane of the constellation.** Spine makes a corpus of governed
material navigable, legible, and durable for readers — including strangers —
**without requiring oral tradition.**

> Continuity supplies the semantic substrate for reliance. Maude's approved
> PlanCore validation prepares and validates proposals; human acceptance remains
> required, and AG is the authority boundary for any governed authorization.
> **Spine governs only what can be found and read.**

> ⚠️ **PROVISIONAL INGRESS — do not script against it as a stable interface.**
> The only ingress adapter today is `provisional_git_manifest_v0` (named ugly
> on purpose). It is scaffolding: the settled architecture reads declared
> references from Continuity, and this adapter exists solely so the index,
> edition, and refusal machinery could be built and tested first. Its manifest
> schema may change or disappear without a deprecation path. The *output*
> contracts (index entries, editions, the refusal wall) are the stable part;
> the ingress is not. (OQ-5 ruling, 2026-07-16.)

See [`DOCTRINE.md`](DOCTRINE.md) for what Spine is allowed to be, and
[`NAMING.md`](NAMING.md) for the `governor.spine` / `~/git/spine` name collision
and its resolution.

## Position in the constellation

Spine's intended semantic source is **Continuity**, but the public implementation
does not yet depend on it: its only live ingress is the declared
`provisional_git_manifest_v0` transport. The committed
`ContinuityExportFixtureSource` is a static shape fixture, not a Continuity
integration. Spine may arrange, package, and present material; it does not
originate canonical semantic state, validate a PlanCore, obtain human acceptance,
or authorize work through AG. Material may be declared from public manifests,
imported documents, external references, generated indexes, or editions.

See [HOWTO.md](HOWTO.md) for a session-orientation path. It is a local, read-only
way to build and compare declared packages; it is not a service, schema, or
decision workflow.

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

## Try it now

```bash
pip install -e .[dev]       # dev checkout — see Distribution name section below

spine build specimens/predicate_witness_manifest.yaml \
    --observed-at 2026-07-05T00:00:00Z \
    --out output/index.json
# built 7 entries -> output/index.json (sha256:...)

spine render output/index.json
# prints the non-authority table — the load-bearing design is in the columns:
# "Spine asserts" is always "located · rendered"; status is a quotation, never an assertion.
# Header reads: "Findability is not legitimacy. Every entry below is located and rendered by Spine."

spine edition create specimens/predicate_witness_manifest.yaml \
    --created-at 2026-07-05T00:00:00Z \
    --out editions
# froze edition sha256:...  (An Edition freezes what Spine located; it does not ratify it.)

spine edition compare \
    editions/fabb36a44c45ff3737c88fcd70d132899d768c8be1d99b33c3a765d1f8be8601 \
    editions/b94f04428773ced08c2bd06e17ad9e892cc8eb1f67ad7c5a7f1b1f0d61589459
# describes added / removed / changed / unchanged between two committed Editions
# mechanically refuses to editorialize: no "newer", "current", or "supersedes"
```

The existing specimen corpus (`specimens/predicate_witness_manifest.yaml`, 7 declared refs
across the constellation) and two committed editions (`editions/fabb36a4…`,
`editions/b94f0442…`) are the genesis fixtures. Every command above exits 0 against them
as committed.

What you see in the `render` output is the whole point: the "Spine asserts" column is always
`located · rendered` — nothing more. Status is quoted from the artifact's governing surface
(`the sign says **candidate**`), never asserted by Spine. Unwitnessed material is flagged:
`**NONE — unwitnessed**`. There is no `status`, `endorsed`, `verdict`, or `authority` column.

## Stack

The build system is not TBD — it was chosen with Slice 1 and is in place:

- **Python ≥ 3.11**, `pyproject.toml` (setuptools ≥ 61, src-layout under `src/`).
- **Runtime deps:** `pydantic>=2`, `pyyaml>=6`. No other runtime deps — stdlib `hashlib`
  for content addressing.
- **Dev deps:** `pytest>=8`, `ruff` (line-length 100).
- **Entry point:** `spine = spine.cli:main` (four commands: `build`, `render`,
  `edition create`, `edition compare`).

Run the suite:

```bash
python -m pytest -q   # 153 passed at the current public base, exit 0
```

## Status

**v0 index engine implemented and green.** 153 tests pass at the current public base. The implementation
covers: manifest loading (crawl-fence refuses globs and trailing-slash directories),
index build (deterministic, content-addressed), non-authority render, edition packaging
(immutable, content-addressed, reproducible), edition diff (substantive drift; succession
refused), declaration-source throat (`source.py`), and a Continuity-shaped fixture. See
[`REENTRY.md`](REENTRY.md) for the slice-by-slice completion record and next valid work.

The design note for the public-MVP campaign (Packets S-A through S-D) lives at
[`docs/design/v0-navigable-index.md`](docs/design/v0-navigable-index.md).

## Distribution name (unresolved — OQ-1)

`pyproject.toml` declares `name = "spine"`, but [`NAMING.md`](NAMING.md) forbids a bare
`spine` distribution name until `governor.spine` renames. The import package name stays
`spine` (every test file uses `from spine import …`; renaming it breaks all 141 tests).
Until Packet S-D resolves this, use this repository as a dev checkout:

```bash
pip install -e .[dev]
```

Do not publish to PyPI under the bare `spine` name while the constraint is active. See
[`NAMING.md`](NAMING.md) §"Rule until `governor.spine` renames" and
[`docs/design/v0-navigable-index.md`](docs/design/v0-navigable-index.md) §8 OQ-1.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
Provenance (human-directed, AI-assisted): [`PROVENANCE.md`](PROVENANCE.md).
