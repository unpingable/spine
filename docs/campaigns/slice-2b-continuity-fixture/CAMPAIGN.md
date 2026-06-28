# Campaign — Spine Slice 2b: Continuity-shaped fixture (grounded, not live)

Status: **SHIPPED** (2026-06-28). The second move of the Continuity-as-source
arc. Continuity enters as a *shape*, never as a *dependency*. The fixture is grounded
in real Continuity's export shape — because **fixture fiction is technical debt with
a fake mustache** — but Continuity stays outside the room.

## The frozen shape (grounding provenance — learned, not imported)

Inspected `~/git/continuity` @ `aab46ec`. Real Continuity has **no `export`
subcommand**; "export" is JSON serialization of pydantic models plus the receipt
envelope. The fixture is modelled on:

- **Envelope** `continuity.receipt.v0` — `src/continuity/receipts/memory_receipts.py:33-41`:
  `{envelope, receipt_id, receipt_type, hash, prev_hash, timestamp, payload}`.
- **Payload = `MemoryObject`** — `src/continuity/api/models.py:258-281`: `memory_id`,
  `scope`, `kind`, `basis`, `status`, `reliance_class`, `confidence`, `content`,
  `source_refs`, `created_at`, `updated_at`, `expires_at`, `supersedes`, `revoked_by`,
  `created_by`, `approved_by`.
- **Native status vocabulary** (`models.py` StrEnums): `MemoryStatus` =
  observed/committed/revoked; `RelianceClass` = none/retrieve_only/advisory/actionable;
  `supersedes` is a pointer field (also `LinkRelation.supersedes`,
  `ProjectStateContent.status: superseded`). **Continuity emits NO `canonical` /
  `ratified` / `authoritative` / `authority` / `latest` / `current` token** — confirmed
  absent from its vocabulary. That absence is exactly why those words are the
  *reject* set and `supersedes` is the *quarantine* set.

## Exit ticket (2026-06-28)

All five exit criteria met. `tests/fixtures/continuity_export_shape_v0.json` (3
grounded `continuity.receipt.v0` envelopes) + `src/spine/continuity_fixture.py`
(`ContinuityExportFixtureSource` — NOT `ContinuitySource`). 141 tests pass (19 new in
`tests/test_continuity_fixture.py`). Proven:

- **Continuity declares LOCATION, not STATUS.** Every declared ref lands as
  `reported_status = unknown`; the lifecycle (`status=committed`,
  `reliance_class=actionable`, `supersedes=…`) survives only as a visibly-labelled
  quotation in `status_source_ref` ("declaration metadata, NOT Spine standing"). The
  dogfood render shows "The sign says" = _(no status reported)_ for all — Continuity's
  `committed`/`actionable` never became a Spine verdict.
- **The nasty test holds.** A foreign authority *field* (`canonical` / `ratified` /
  `authority` / `latest` / `current`) anywhere in a record is rejected
  (`ForeignAuthorityFieldError`); `supersedes` (a real field) is quarantined, not
  rejected; a prose *value* naming an authority word is not a hit (keys-only scan).
- **The dog stays outside.** AST guard asserts no `continuity` import, no `subprocess`.
  Crawl fence still fires on a Continuity-declared glob path (defense in depth via the
  shared `load_manifest`).

The forbidden list held: no live Continuity, no `continuity` import, no subprocess, no
latest/canonical/current/rank/supersedes resolver, no promotion/witness synthesis, no
Continuity label mapped to Spine standing, `build_edition` untouched (the edition path
runs by dumping the declared manifest to YAML).

Next: Slice 2c — real Continuity adapter (the forcing case for a content-based
`build_edition`).

## The one line

> **Continuity may shape the envelope. Continuity may not supply the verdict.**

## The grounding rule

Glance at real Continuity (`~/git/continuity`) only to learn the export *shape*. Do
not integrate it. Do not call it live. Do not let its semantics leak into Spine. The
fixture is modelled on a real envelope so 2c is a plug-in, not a rewrite — but it is
a **static file committed under Spine**, parsed by a Spine-owned adapter.

## Question

Can a Continuity-shaped static export declare refs into Spine through
`DeclarationSource` — running the full index / render / edition path — **without
adding any new assertion vocabulary or succession semantics**?

## Invariant

Continuity-shaped fields that look like authority (`canonical`, `ratified`, `latest`,
`supersedes`, `authority`, `current`, …) must **never** map into Spine standing or
`spine_assertions`. The adapter has exactly two licensed moves for such a field:
**reject**, or **preserve it as visibly-quarantined quoted source metadata** (in
`status_source_ref`, the place Spine already keeps "what the sign said"). Never
normalize it into a Spine claim. Default bias: **reject**, unless real Continuity
actually emits the word — in which case quarantine-as-quotation, never promote.

## Allowed

- Inspect `~/git/continuity` for the existing export/record shape (learn only).
- Commit a static fixture under Spine, named obnoxiously honestly:
  `tests/fixtures/continuity_export_shape_v0.json` (a *shape*, a *v0*, a *fixture*).
- Write a Spine-owned adapter, `ContinuityExportFixtureSource` — NOT
  `ContinuitySource` (that name is too powerful; it starts wearing cologne).
- Prove it emits a `DeclaredManifest` and runs the full index/render/edition path.
- Record provenance as **source declaration provenance only** (`source_kind`
  identifies the fixture; `export_digest` over the fixture bytes; `declared_at`
  descriptive only).

## Forbidden

- No live Continuity dependency. No import from the `continuity` package. No shelling
  out to Continuity. (Tests stay environment-free — no séance rituals.)
- No "latest" / canonical / current / rank / supersedes resolver.
- No promotion, no witness synthesis, no treating a Continuity label as Spine standing.
- No `build_edition` content-refactor (still the 2c seam; the fixture path can be
  read as a file for the edition build, OR the edition step is proven via the
  declared manifest only — keep `build_edition` untouched).

## The nasty test (required)

A fixture record carrying an authority-shaped field (`canonical` / `ratified` /
`latest` / `supersedes` / `authority`) must result in **either** a typed rejection
**or** that field surviving only as quoted source metadata — and a `build_index`
over the result must still show `spine_assertions == (located, rendered)` and must
**refuse** any governed claim (`ratified`) that lacks a witness. The authority word
must not appear in any Spine assertion. (Reuses the Slice 2a guarantee: declaring is
not conferring.)

## Exit (done when)

1. A static `continuity_export_shape_v0.json` fixture exists under Spine, modelled on
   real Continuity's export shape (citation to the shape recorded in this card).
2. `ContinuityExportFixtureSource` satisfies `DeclarationSource` and emits a
   `DeclaredManifest` from the fixture, with declaration-only provenance.
3. The full index / render / edition path runs from the fixture; entries assert only
   `located` / `rendered`.
4. The nasty test passes: authority-shaped fixture fields are rejected or quarantined
   as quoted metadata, never mapped into Spine standing.
5. No live Continuity, no `continuity` import, no subprocess; no new assertion
   vocabulary; no succession semantics; `build_edition` untouched.

## After this (do NOT pull forward)

2c (real Continuity adapter — forcing case for the content-based edition build) →
2d (retire the provisional manifest as transport replacement) → public Edition
reader. The fixture proves the *shape* is consumable; the live adapter is a separate,
later admission.
