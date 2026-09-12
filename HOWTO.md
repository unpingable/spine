# Spine session orientation

Use Spine to orient a reader around explicitly declared material. The output is
navigational: it quotes what a source says and describes package drift. It does
not decide whether an obsolete handoff should be acted on, whether one document
replaces another, whether a neighbor constraint applies, or whether a source
change warrants work. Those questions stay with their governing surfaces, human
acceptance, and AG authorization.

The current public ingress is `provisional_git_manifest_v0`. It is a declared,
concrete-file transport, not a crawler and not an actual Continuity dependency.
`ContinuityExportFixtureSource` is a static substitution fixture: lifecycle text,
including a `supersedes` field, remains visibly quoted metadata and never becomes a
Spine decision.

For a local orientation session, use only public or synthetic references and an
empty output directory:

```sh
spine build orientation-base.yaml --observed-at 2026-09-12T00:00:00Z --out tmp/base.json
spine render tmp/base.json --out tmp/base.md
spine edition create orientation-base.yaml --created-at 2026-09-12T00:00:00Z --out tmp/editions
spine edition create orientation-target.yaml --created-at 2026-09-12T00:01:00Z --out tmp/editions
spine edition compare tmp/editions/<base-id> tmp/editions/<target-id> --out tmp/drift.md
```

Declare an obsolete handoff, a source-side supersession statement, a neighboring
constraint, and a source change as separate, quoted entries. The comparison may
show entries present only on one side or differing quoted fields. That is package
drift, not a claim that either package is current, preferred, superseding, or fit
for action. Keep this documentation-only orientation path separate from any
dependable packet integration.
