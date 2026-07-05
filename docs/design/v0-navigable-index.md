# Spine v0 — the navigable index (design note)

STATUS: DESIGN NOTE — CANDIDATE (public-mvp lane S); operator ratifies before build

---

## 0. Orientation — read this first

This note was commissioned under the belief that Spine's implementation was "not
yet started." **It is not.** A working implementation already lives in
`src/spine/` and **all 141 tests pass** (`pytest -q` green at HEAD `16ef81f`,
run in `.venv`). The README's *"implementation is not yet started"* and
*"build system TBD"* lines are **stale** — this note supersedes them.

So this is not a greenfield build plan. It is:

1. a **declaration** of what already satisfies the test pins (the contract is
   *implemented*, not merely *specified*), and
2. the **smallest delta** from "green in a dev checkout" to "a public-usable
   artifact a stranger can pick up" — which is what Sprint S actually owes.

The read-plane wall is intact in code and this note adds **no authority verb**
to Spine's vocabulary. Where charter and tests are silent or conflict, the
question is parked in §8, not decided here.

---

## 1. Stack declaration (kills "build system TBD")

The stack is **already chosen and present** — this note ratifies it, ending the
"TBD":

- **Language / runtime:** Python, `requires-python >= 3.11`.
- **Build backend:** `setuptools>=61` via `pyproject.toml` (`[build-system]`),
  src-layout (`[tool.setuptools.packages.find] where = ["src"]`).
- **Runtime deps:** `pydantic>=2` (typed models + closed-field-set walls),
  `pyyaml>=6` (manifest parse). No other runtime deps — stdlib `hashlib` for
  content addressing.
- **Dev deps:** `pytest>=8`, `ruff` (line-length 100).
- **Console entry point:** `spine = spine.cli:main` (argparse; commands `build`,
  `render`, `edition create`, `edition compare`).

There is a **naming conflict** between `pyproject.toml` (`name = "spine"`) and
`NAMING.md` (no bare `spine` distribution name until `governor.spine` renames).
It is unresolved and parked as **OQ-1** — it is a *distribution/packaging*
question, not an index-design question, and every test imports `from spine import
…`, so it cannot be changed casually.

---

## 2. Input contract — a *declared* corpus manifest (no discovery)

Spine never discovers scope. **The caller names the corpus, artifact by
artifact.** Ingress is the single provisional adapter
`provisional_git_manifest_v0` (named ugly on purpose; the final architecture
reads from Continuity).

**Manifest shape** (`spine/manifest.py`, closed schema):

```yaml
adapter: provisional_git_manifest_v0
artifacts:
  - repo: agent_gov
    path: docs/roadmaps/README.md
    reported_status: unknown          # or candidate / non-binding / ratified
    status_source_ref: null           # required unless status == unknown
    witness_ref: null                 # required iff status == ratified
```

- `canonical_location` is the derived `f"{repo}:{path}"` — the index sort key.
- **The crawl fence is the load-bearing input rule:** a `path` that is a glob
  (`*?[]{}`) or ends in `/` is **refused** (`CrawlAttemptError`) — not executed.
  A bare directory-looking ref *without* a trailing slash/glob is treated as a
  concrete (if odd) reference; the fence polices globs and trailing slashes, not
  a heuristic guess about directories.
- An unknown `adapter` → `UnknownIngressError`. Any extra top-level key (e.g.
  `recurse: true`) → `MalformedManifestError` (closed schema).

**Specimen corpus for the public MVP** (new; see Packet B): a hand-declared
manifest naming concrete files under `agent_gov` `docs/roadmaps/` and
`docs/campaigns/`. Because the adapter cannot crawl, each file is enumerated by
name — which *is* the charter ("Spine never implies scope"). The existing
committed specimens (`predicate_witness_manifest.yaml`, `mixed_status_corpus.yaml`)
stay as the test-pinned genesis corpora and are **not** replaced.

An optional **declaration-source throat** (`spine/source.py`,
`DeclarationSource -> DeclaredManifest`) wraps a manifest so a future
Continuity-shaped source can declare refs without touching the pipeline; a
committed Continuity-shaped *fixture* source already exercises it. This is
already built and is **not** in the public-MVP critical path.

---

## 3. Output contract — the index artifact + the non-authority render

### 3a. The index artifact (machine-readable)

`build_index(manifest, observed_at=…) -> SpineIndex` (deterministic; entries
sorted by `canonical_location`; `index_digest` = sha256 over the ordered entry
digests + ingress + observed_at).

`IndexEntry` field set (the *entire* status surface — note what is **absent**):

| field | meaning |
|-------|---------|
| `canonical_location` | `repo:path` — where Spine located it |
| `reported_status` | a **quotation** from a governing surface (`ratified` / `candidate` / `non-binding` / `unknown`) — never Spine's word |
| `status_source_ref` | pointer to *where* the status is declared (required unless `unknown`) |
| `witness_ref` | pointer to a witness (required iff `reported_status == ratified`) |
| `ingress_adapter` | `provisional_git_manifest_v0` |
| `observed_at` | caller-supplied observation time |
| `spine_assertions` | **closed to `("located", "rendered")`** — a legitimacy verb here is the wall falling (`SpineBearsStatusError`) |
| `entry_digest` (computed) | sha256 over content; an entry cannot lie about its own digest |
| `is_navigational_only` (computed) | `True` — always, structurally |

**There is no `status`, `endorsement`, `verdict`, `authority`, `current`, or
`rank` field.** Legitimacy is only ever *quoted* (`reported_status` + its
`status_source_ref`), never *asserted*.

### 3b. The non-authority render (human-readable) — satisfies `test_render_non_authority`

`render_markdown(index) -> str`. Deterministic. Shape (verbatim from the current
implementation, which is green against the test):

- **Header disclaimer** contains the exact strings `Findability is not
  legitimacy` and `located and rendered`.
- **Table columns:** `Artifact | Spine asserts | The sign says | Source |
  Witness`.
- **"Spine asserts" cell** is the boring pair, always: `located · rendered`.
- **"The sign says" cell** frames status as a quotation: `the sign says
  **candidate**` — never a bare `candidate` standing as Spine's verdict; a
  status Spine does not know renders as `_(no status reported)_`.
- **"Witness" cell** for a null witness is loud: `**NONE — unwitnessed**`.
- **Forbidden substrings** (the test asserts their *absence*): `| governed`,
  `| valid`, `| ratified |`, `asserts ratified`. No authority verb ever appears
  as a Spine assertion.

This render is what makes the artifact *public-usable*: a stranger reads the
table and sees, per row, exactly what Spine claims (located · rendered) versus
what the artifact claims about itself (quoted), with unwitnessed material flagged
in bold.

---

## 4. Edition / diff semantics — satisfies `test_edition_packaging` + `test_edition_diff`

### 4a. Edition (freeze what was found; promote nothing)

`build_edition` / `write_edition` freeze an index into an immutable, citable
directory named by its content-addressed `edition_id`
(`sha256:<hex>`). Each edition ships four files: `manifest.yaml`, `index.json`,
`index.md`, `edition.json`.

- **Reproducible:** same manifest bytes + same `created_at` → identical
  `edition_id` and byte-identical files. `created_at` **is** content (a
  different time is a different citation target); `build_provenance` is **not**
  (how it was referenced does not fork identity).
- **Immutable:** re-minting into an occupied dir → `EditionExistsError`; a
  crash mid-write leaves no litter and no occupied target (atomic temp+rename).
- **The wall holds at the package layer:** the frozen index still reports the
  same `reported_status` / unwitnessed state, still asserts only
  `located`/`rendered`; `spine_assertions` on the Edition itself may never hold
  a legitimacy verb — refused both in the `build_edition` factory and a
  model-level validator. Two real editions are committed and their ids are
  pinned by tests (`fabb36a4…`, `b94f0442…`).

### 4b. Diff (describe drift, never succession) — the load-bearing wall

`diff_editions(base, target) -> EditionDiff`, closed field set:
`{base_edition_id, target_edition_id, base_created_at, target_created_at,
base_ingress_adapter, target_ingress_adapter, added, removed, changed,
unchanged, spine_assertions}`. **Forbidden fields** (the closed set *is* the
wall): `winner, latest, current, recommended, rank, supersedes, newer`.

- **Drift is substantive, not chronological.** `added`/`removed` are a set
  difference on `canonical_location`; `changed` fires only on a substantive move
  (`reported_status` or `witness_ref` differs). **Two editions observed at
  different `created_at` with identical substance are `unchanged`** — "drift"
  means what the sign says moved, not when Spine looked.
- **Spine's own framing may never editorialize a difference into succession.**
  `check_no_succession_framing(*texts)` word-boundary-matches Spine-authored
  prose against a closed `SUCCESSION_FRAMING` set (`newer/older/latest/current/
  canonical/supersede(s|d)/obsolete/deprecated/…`) and raises
  `EditionSuccessionError` on a hit. It polices Spine's *verdict-voice only* — a
  quoted `reported_status` of `ratified`, or a path like `docs/recurrent.md`, is
  not a hit.
- The render (`render_edition_diff`) carries the disclaimer `package drift, not
  doctrinal movement` and `coordinate, not a verdict`; a full rendered diff
  contains no succession word anywhere.
- **Load fails closed:** a missing dir, missing file, or a tampered `index.json`
  whose digest no longer matches the edition's recorded `index_digest` →
  `EditionLoadError`. A read plane reads only intact frozen packages.

---

## 5. Non-goals (explicit)

- **N-G1. No adjudication.** Spine decides nothing; "which edition is current"
  is a verdict and verdicts live in Continuity (reliance) or Maude
  (adjudication). (`EditionSuccessionError` enforces this.)
- **N-G2. No status bearing.** `spine_assertions` is closed to
  `located`/`rendered`; a legitimacy verb is a hard refusal at every layer
  (entry, edition, model validator).
- **N-G3. No cross-repo authority claims.** Indexing a ref in another repo
  asserts only that Spine *located and rendered* it — never that it is governed,
  current, or endorsed by inclusion, arrangement, or prominence.
- **N-G4. No discovery / crawling.** The caller declares concrete refs; globs,
  directories-with-trailing-slash, and recurse flags are refused, not executed.
- **N-G5. No new witness synthesis.** Spine never manufactures a `witness_ref`;
  a governed claim without one is refused, never softened.
- **N-G6. No stele in v0** (charter C5 names *index / edition / stele*; only the
  first two are built and tested). Stele is a new surface with no forcing case
  and no test pin — parked as **OQ-4**, not built here.

---

## 6. Implementation plan (≤4 bounded packets)

The core index/render/edition/diff engine is **already built and green** — no
packet re-implements it. These packets close the delta to a public-usable
artifact. Each names the existing test pins it must keep green (regression), and
adds **no** authority vocabulary.

### Packet S-A — de-stale the front matter + ratify the stack

- **Files:** `README.md` (replace "not yet started" / "build system TBD" with
  the §1 stack declaration + "Status: v0 index engine implemented, N tests
  green"); `REENTRY.md` header touch; link this design note.
- **No code.** Pins kept green: **all 8** (unchanged; this is docs only).
- **Exit:** README truthfully describes a built read plane; no stale claim
  remains. Resolve or explicitly carry **OQ-1** (naming) — do **not** silently
  rename the `spine` import package (would break every test file).

### Packet S-B — the public-MVP specimen corpus + its Edition

- **Files:** `specimens/public_mvp_roadmaps_campaigns.yaml` (a hand-declared
  `provisional_git_manifest_v0` naming concrete files under `agent_gov`
  `docs/roadmaps/` + `docs/campaigns/`; most refs `reported_status: unknown`
  with `status_source_ref: null`, quoting a header Status only where one
  literally exists); a committed Edition under `editions/<edition_id>/`;
  optionally `specimens/public_mvp_roadmaps_campaigns.NOTES.md`.
- **Pins:** must pass `load_manifest` (crawl fence — every ref concrete),
  `build_index` (`test_manifest_contract` shape), `build_edition`
  (`test_edition_packaging` reproducibility/immutability). Add a small
  `tests/test_public_mvp_corpus.py` pinning the new edition_id + entry count +
  "all entries assert only located/rendered."
- **Exit:** a stranger can run `spine build specimens/public_mvp_roadmaps_campaigns.yaml`
  and `spine render` and get the non-authority table over real constellation
  planning docs. **Blocked on OQ-2** (per-doc status sourcing policy).

### Packet S-C — the stranger runbook (falsification C6 made operable)

- **Files:** `docs/USING-SPINE.md` (or README section): the four commands
  (`build`, `render`, `edition create`, `edition compare`), what each output
  column means, and **how to verify the digests yourself** (recompute the
  `edition_id` from the frozen bytes). This is DOCTRINE C6 — "a stranger
  recovers the corpus without oral tradition" — turned into a checklist.
- **No engine code.** Pins kept green: all existing (docs + possibly a
  `tests/test_cli_smoke.py` asserting the documented commands exit 0 and the
  disclaimer appears — mirrors the CLI smoke already in `test_edition_diff`).
- **Exit:** the runbook, executed verbatim on a clean checkout, reproduces a
  rendered index + an edition + a diff, and the digest-verification step
  succeeds.

### Packet S-D (conditional) — packaging / distribution-name resolution

- **Only if OQ-1 is ratified toward publication.** Files: `pyproject.toml`
  (distribution name → qualified per `NAMING.md`, e.g. `spine_readplane`, while
  keeping the `spine` import package so tests stay green if operator so rules),
  console-script verification, `pip install .` from a clean venv, `python -m
  build` sdist/wheel smoke.
- **Pins:** all 8 must still import `from spine import …` and pass.
- **Exit:** a buildable, installable artifact under a name that does not shadow
  `governor.spine`. **If OQ-1 is deferred, this packet does not run** — the
  dev-checkout artifact from S-A..S-C is already publicly *usable*, just not
  PyPI-published.

Order: **S-A → S-B → S-C**; **S-D** only on OQ-1 ratification.

---

## 7. What already satisfies each test pin (verification map)

| test file | what it pins | satisfied by |
|-----------|--------------|--------------|
| `test_manifest_contract.py` | specimen builds (7 entries, all candidate/unwitnessed); deterministic byte-identical index sorted by location; crawl fence (globs/dirs → `CrawlAttemptError`); unknown adapter/extra key refused | `manifest.py`, `index.py` |
| `test_render_non_authority.py` | render states "Findability is not legitimacy"/"located and rendered"; status as `the sign says **candidate**`; `**NONE — unwitnessed**`; asserts column only `located · rendered`; no legitimacy verb; deterministic | `render.py` |
| `test_index_refusal.py` | `spine_assertions` closed to located/rendered; legitimacy verb → `SpineBearsStatusError`; sourced status required (except `unknown`); ratified needs witness; unknown status refused | `refusal.py`, `index.py` |
| `test_edition_packaging.py` | reproducible + content-addressed edition_id; immutable no-overwrite + atomic write; frozen index preserves status/creates none; validator wall; pinned edition_id | `edition.py` |
| `test_edition_diff.py` | added/removed/changed/unchanged as substantive set-diff; observation time never = changed; closed field set (no winner/newer/…); succession-framing guard; fail-closed load/tamper; CLI compare smoke | `edition_diff.py`, `cli.py` |
| `test_corpus_expansion.py` | heterogeneous 5-entry corpus stays located/rendered; importance ≠ status (`unknown`); museum-label (PARKED carried, never "current"); Edition 2 pinned | `index.py`, `edition.py`, `render.py` |
| `test_declaration_source.py` | `DeclarationSource -> DeclaredManifest` throat transparent (byte-identical pipeline); closed `SourceProvenance`; a source declaring a witnessless `ratified` ref is refused at index-build | `source.py` |
| `test_continuity_fixture.py` | Continuity-shaped fixture declares refs; lifecycle quarantined as quoted metadata; every ref lands `unknown`; foreign authority *keys* rejected; no live Continuity import | `continuity_fixture.py` |

---

## 8. Open questions for operator

- **OQ-1 (distribution name conflict).** `pyproject.toml` declares
  `name = "spine"`; `NAMING.md` forbids a bare `spine` distribution name until
  `governor.spine` renames. Every test imports `from spine import …`. **Q:** for
  the public MVP, keep the `spine` *import* package (tests unchanged) and only
  qualify the *distribution* name (e.g. `spine_readplane`)? Rename the import
  package too (breaks all 8 test files — a test-pin change)? Or defer publication
  entirely and ship a dev-checkout artifact? (Gates Packet S-D.)

- **OQ-2 (specimen status-sourcing policy).** For the roadmaps/campaigns
  specimen, most docs carry no machine-quotable header Status. **Q:** blanket
  `reported_status: unknown` (honest, sourceless) for everything, or quote a
  header Status where one exists? And do these refs use `repo: agent_gov` with
  cross-repo `path`s (Spine indexing a sibling repo it does not vendor), which is
  navigationally legal but worth an explicit nod? (Gates Packet S-B.)

- **OQ-3 (`observed_at` / `created_at` for a public edition).** Both are
  caller-supplied, not wall-clock, so editions are reproducible. **Q:** is a
  fixed, documented timestamp acceptable for the public specimen edition, or does
  the public artifact want a real (and thus non-reproducible-by-a-stranger)
  build time? (Charter favors reproducibility → fixed; confirm.)

- **OQ-4 (stele in scope?).** Charter C5 lists *index / edition / **stele***;
  only index + edition are built/tested. **Q:** is a stele required for the
  public MVP, or deferred? No test pins it and there is no forcing case, so the
  default is defer — but the charter names it, so this is an operator call, not a
  worker default.

- **OQ-5 (README "final architecture" honesty).** README/REENTRY say the final
  architecture reads from Continuity, and the provisional git manifest is
  temporary. **Q:** for a public MVP, how loudly should the front matter mark the
  ingress adapter as provisional/scaffolding so a stranger does not mistake it
  for the settled interface?
