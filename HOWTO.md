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

For a local orientation session, use only public or synthetic references. This
complete synthetic example uses the public `provisional_git_manifest_v0` shape;
the strings below are labels for local fixtures, not claims about public
documents. Start with a new output directory and create both manifests:

```sh
mkdir -p tmp/manifests tmp/editions

cat > tmp/manifests/orientation-base.yaml <<'YAML'
adapter: provisional_git_manifest_v0
artifacts:
  - repo: public-example
    path: docs/obsolete-handoff.md
    reported_status: candidate
    status_source_ref: "synthetic:Status"
    witness_ref: null
    status_quote: "Candidate; not accepted."
  - repo: public-example
    path: docs/neighbor-constraint.md
    reported_status: candidate
    status_source_ref: "synthetic:Status"
    witness_ref: null
    status_quote: "Candidate constraint; not accepted."
YAML

cat > tmp/manifests/orientation-target.yaml <<'YAML'
adapter: provisional_git_manifest_v0
artifacts:
  - repo: public-example
    path: docs/obsolete-handoff.md
    reported_status: candidate
    status_source_ref: "synthetic:Status"
    witness_ref: null
    status_quote: "Candidate; source says superseded by a later handoff."
  - repo: public-example
    path: docs/neighbor-constraint.md
    reported_status: candidate
    status_source_ref: "synthetic:Status"
    witness_ref: null
    status_quote: "Candidate constraint; not accepted."
  - repo: public-example
    path: docs/source-change.md
    reported_status: candidate
    status_source_ref: "synthetic:Status"
    witness_ref: null
    status_quote: "Candidate source change; not accepted."
YAML
```

Build and render the base manifest, then freeze and compare the two fixed
synthetic editions:

```sh
spine build tmp/manifests/orientation-base.yaml --observed-at 2026-09-12T00:00:00Z --out tmp/base.json
spine render tmp/base.json --out tmp/base.md
spine edition create tmp/manifests/orientation-base.yaml --created-at 2026-09-12T00:00:00Z --out tmp/editions
spine edition create tmp/manifests/orientation-target.yaml --created-at 2026-09-12T00:01:00Z --out tmp/editions
spine edition compare \
  tmp/editions/577ab42cad5bb439d5bb950a5d2252b304b692efe046845027c76be7392650cd \
  tmp/editions/7be89b68b38d0dd7ad92a236ce73b8bd24305969837c84b2f4f8cc173649c95d \
  --out tmp/drift.md
```

Declare an obsolete handoff, a source-side supersession statement, a neighboring
constraint, and a source change as separate, quoted entries. The comparison may
show entries present only on one side or differing quoted fields. That is package
drift, not a claim that either package is current, preferred, superseding, or fit
for action. Keep this documentation-only orientation path separate from any
dependable packet integration.
