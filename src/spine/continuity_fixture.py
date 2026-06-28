# SPDX-License-Identifier: Apache-2.0
"""Continuity-shaped fixture source — the envelope, never the verdict.

> Continuity may shape the envelope. Continuity may not supply the verdict.

This adapter consumes a **static fixture** modelled on real Continuity's export shape
(`~/git/continuity`: a list of `continuity.receipt.v0` envelopes, each wrapping a
`MemoryObject` payload — see `src/continuity/receipts/memory_receipts.py` and
`src/continuity/api/models.py`). It is NOT live Continuity: no `continuity` import, no
subprocess, no network. The fixture is committed under Spine and parsed by this
Spine-owned adapter. Grounding the fixture in the real shape is deliberate — fixture
fiction is technical debt with a fake mustache — but Continuity stays outside the room.

The hard rule, made code:

- **Continuity declares LOCATION, not STATUS.** Every declared ref lands as
  ``reported_status = "unknown"``. Continuity's own lifecycle (``status`` =
  observed/committed/revoked, ``reliance_class``, ``supersedes``, ``confidence``,
  ``basis``) is *quarantined* verbatim into ``status_source_ref`` and visibly labelled
  "NOT Spine standing" — never mapped into a Spine claim or assertion. Even
  ``reliance_class: actionable`` confers nothing.
- **Foreign authority words are rejected.** Real Continuity does not emit
  ``canonical`` / ``ratified`` / ``authoritative`` / ``authority`` / ``latest`` /
  ``current`` (verified against its enum vocabulary). Their presence in a fixture is
  either a forgery or a smuggling attempt, so a record carrying such a *field* is
  refused (``ForeignAuthorityFieldError``). ``supersedes`` is NOT in this set: it is a
  genuine Continuity field, so it is quarantined as quoted metadata, not rejected.

The deep guarantee still rides underneath: the declared refs flow through
``load_manifest`` → ``build_index`` → ``check_entry_admissible`` like any other
manifest (crawl fence included), so nothing here can mint Spine standing even if the
adapter had a bug — the wall is downstream.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from .manifest import Manifest, load_manifest
from .refusal import INGRESS_PROVISIONAL_GIT, SpineRefusal
from .source import DeclaredManifest, SourceProvenance

# Source identity (humiliating on purpose — a *fixture*, a *shape*, a *v0*). NOT
# "ContinuitySource"; that name is too powerful, it starts wearing cologne.
SOURCE_KIND = "continuity_export_fixture_v0"

# Field NAMES that real Continuity never emits (checked against its StrEnum
# vocabulary). Their presence is smuggling — reject, don't normalize. NOTE:
# ``supersedes`` is deliberately absent — it IS a real Continuity field and is
# quarantined as quoted metadata, never rejected and never mapped to succession.
FOREIGN_AUTHORITY_FIELDS = frozenset({
    "canonical", "ratified", "authoritative", "authority", "latest", "current",
})

# Continuity-native lifecycle fields preserved (quarantined) as quoted metadata.
# Verbatim from the source, never read by Spine as a governing status.
_QUARANTINE_FIELDS = (
    "memory_id", "status", "reliance_class", "basis", "kind", "scope",
    "confidence", "supersedes",
)


class ContinuityShapeError(SpineRefusal):
    """The fixture is not a well-formed Continuity-shaped export, or a record
    declares no locatable ``repo``/``path``. A read plane fails clean and loud on a
    malformed declaration rather than guessing."""


class ForeignAuthorityFieldError(SpineRefusal):
    """A fixture record carries an authority-shaped field real Continuity never
    emits (``canonical`` / ``ratified`` / ``authority`` / ``latest`` / ``current``).
    Spine refuses it rather than letting a foreign authority word ride a declaration
    into the read plane — declaring is not conferring."""


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _all_keys_lower(obj: object):
    """Yield every mapping key (lowercased) anywhere in a nested structure. Keys
    only — never values — so free-text prose like a summary saying 'the canonical
    doc' is not a false hit; only a structural *field* trips the wall."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k).lower()
            yield from _all_keys_lower(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _all_keys_lower(item)


def _reject_foreign_authority(record: dict) -> None:
    hits = sorted({k for k in _all_keys_lower(record) if k in FOREIGN_AUTHORITY_FIELDS})
    if hits:
        raise ForeignAuthorityFieldError(
            f"Continuity-shaped record carries authority field(s) {hits!r} that real "
            "Continuity does not emit; refusing to let a foreign authority word ride a "
            "declaration into Spine (a source declares location, not standing)"
        )


def _quarantine(payload: dict) -> str:
    """Build the visibly-quarantined quotation of Continuity's own lifecycle. This
    is metadata about the *declaration*, never a Spine governing status."""
    parts = []
    for field in _QUARANTINE_FIELDS:
        value = payload.get(field)
        if value is not None:
            parts.append(f"{field}={value}")
    body = " ".join(parts)
    return f"continuity.receipt.v0[{body}] — declaration metadata, NOT Spine standing"


def _record_to_artifact(record: dict) -> dict:
    """Map one Continuity envelope to a Spine manifest artifact. reported_status is
    always ``unknown``: Continuity declares where to look, not whether it is governed."""
    if not isinstance(record, dict) or record.get("envelope") != "continuity.receipt.v0":
        raise ContinuityShapeError(
            "each record must be a continuity.receipt.v0 envelope"
        )
    _reject_foreign_authority(record)

    payload = record.get("payload")
    if not isinstance(payload, dict):
        raise ContinuityShapeError("envelope is missing a payload object")
    content = payload.get("content")
    if not isinstance(content, dict):
        raise ContinuityShapeError("payload is missing a content object")

    repo = content.get("repo")
    path = content.get("path")
    if not (isinstance(repo, str) and repo.strip() and isinstance(path, str) and path.strip()):
        raise ContinuityShapeError(
            "record declares no locatable repo/path in its content; a declaration "
            "must name a concrete artifact to locate"
        )

    return {
        "repo": repo,
        "path": path,
        "reported_status": "unknown",          # Continuity confers no governing status
        "status_source_ref": _quarantine(payload),
        "witness_ref": None,
    }


class ContinuityExportFixtureSource:
    """A :class:`~spine.source.DeclarationSource` over a static Continuity-shaped
    export fixture. Emits a :class:`~spine.source.DeclaredManifest` whose refs are
    declared by Continuity but whose *status is Spine's `unknown`* — the envelope is
    Continuity's, the verdict is not."""

    source_kind = SOURCE_KIND

    def __init__(self, fixture_path: str | Path, *, source_ref: str | None = None):
        self._path = Path(fixture_path)
        self._source_ref = source_ref if source_ref is not None else str(fixture_path)

    def declare(self) -> DeclaredManifest:
        raw = self._path.read_bytes()
        try:
            records = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ContinuityShapeError(f"fixture is not valid JSON: {exc}") from exc
        if not isinstance(records, list):
            raise ContinuityShapeError("a Continuity export fixture is a list of envelopes")

        artifacts = [_record_to_artifact(rec) for rec in records]

        # Route the translated refs through the SAME manifest loader as every other
        # source: the crawl fence, adapter check, and structural validation all apply.
        # Ingress stays git (refs are repo:path); the *declaration source* is recorded
        # separately in provenance below.
        manifest_dict = {"adapter": INGRESS_PROVISIONAL_GIT, "artifacts": artifacts}
        manifest: Manifest = load_manifest(self._path, content=yaml.safe_dump(manifest_dict))

        provenance = SourceProvenance(
            source_kind=self.source_kind,
            source_ref=self._source_ref,
            export_digest=_sha256(raw),
            declared_at=None,
        )
        return DeclaredManifest(manifest=manifest, provenance=provenance)
