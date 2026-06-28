# SPDX-License-Identifier: Apache-2.0
"""The refusal — the spine of Spine.

> Spine indexes status-bearing objects; it does not bear status.
> Spine can say *"the sign says ratified."* Spine cannot say *"ratified."*

This module is the doctrine made code: the closed vocabularies an index entry may
use, the legitimacy verbs it may NEVER assert, and the typed refusals that fire
when an entry tries to launder index presence into authority. Everything else in
the repo is plumbing around this wall.
"""

from __future__ import annotations

from collections.abc import Iterable

# --------------------------------------------------------------------------- #
# What Spine may assert about an entry. Closed, and boring on purpose.
# --------------------------------------------------------------------------- #

LOCATED = "located"   # Spine found it at the canonical location.
RENDERED = "rendered"  # Spine presented it.
SPINE_ASSERTIONS = frozenset({LOCATED, RENDERED})

# What Spine may NEVER assert. Findability is not legitimacy: an index entry that
# claims any of these has stopped being a navigational record and started being a
# governing surface — the one thing the read plane is forbidden to be.
LEGITIMACY_VERBS = frozenset({
    "ratified", "governed", "valid", "admitted", "authorized",
    "witnessed", "certified", "approved", "supported", "promoted",
})

# --------------------------------------------------------------------------- #
# Reported status — a QUOTATION of a governing surface, never Spine's own word.
# --------------------------------------------------------------------------- #

STATUS_RATIFIED = "ratified"
STATUS_CANDIDATE = "candidate"
STATUS_NON_BINDING = "non-binding"
STATUS_UNKNOWN = "unknown"
REPORTED_STATUSES = frozenset({
    STATUS_RATIFIED, STATUS_CANDIDATE, STATUS_NON_BINDING, STATUS_UNKNOWN,
})

# Statuses that CLAIM governed authority. Claiming one is the heavy act, so it
# carries the heavy requirement (a witness). The rest are explicit
# non-authoritative markers — candidate/non-binding/unknown say, on their face,
# "do not cite me as authority."
AUTHORITATIVE_STATUSES = frozenset({STATUS_RATIFIED})
NON_AUTHORITATIVE_STATUSES = REPORTED_STATUSES - AUTHORITATIVE_STATUSES

# The provisional ingress adapter (named ugly on purpose; see manifest.py).
INGRESS_PROVISIONAL_GIT = "provisional_git_manifest_v0"
KNOWN_INGRESS_ADAPTERS = frozenset({INGRESS_PROVISIONAL_GIT})


# --------------------------------------------------------------------------- #
# Typed refusals. Each names exactly which laundering was attempted.
# --------------------------------------------------------------------------- #


class SpineRefusal(ValueError):
    """Base for every read-plane refusal."""


class SpineBearsStatusError(SpineRefusal):
    """An entry tried to make Spine *assert* legitimacy (a legitimacy verb in
    ``spine_assertions``, or an unknown assertion). Spine asserts only
    ``located`` / ``rendered``."""


class UnsourcedStatusError(SpineRefusal):
    """A reported_status with no ``status_source_ref``. Spine may report what a
    governing surface says; it may not become the surface saying it — so a
    reported status without a pointer to its source is meaningless and refused."""


class UnwitnessedGovernedClaimError(SpineRefusal):
    """An entry claims a governed status (``ratified``) without a ``witness_ref``.
    A missing witness on a governed claim is a HARD refusal, never a soft
    warning."""


class UnknownStatusError(SpineRefusal):
    """reported_status is not in the closed vocabulary."""


class UnknownIngressError(SpineRefusal):
    """ingress_adapter is not a known adapter."""


class CrawlAttemptError(SpineRefusal):
    """The manifest tried to make the adapter discover material (a glob, a
    directory, a recurse flag). The provisional adapter is *incapable of
    crawling*: it reads declared, concrete file references or it refuses."""


class MalformedManifestError(SpineRefusal):
    """The manifest is structurally invalid (wrong shape, unknown key, wrong
    type). Surfaced as a typed refusal, not a raw stack trace — a read plane
    fails clean and loud."""


class EditionExistsError(SpineRefusal):
    """The target edition directory already exists. An Edition is immutable: it
    freezes what was *found* and is never overwritten in place. Re-running into
    an occupied edition directory is a refusal, not a silent clobber — the
    no-overwrite rule is the point, so it fails loud."""


# --------------------------------------------------------------------------- #
# The wall, as a pure check. Raises a typed SpineRefusal or returns None.
# --------------------------------------------------------------------------- #


def check_spine_assertions(spine_assertions: Iterable[str]) -> None:
    """The wall, isolated: Spine may assert only ``located`` / ``rendered``.

    Shared by the index-entry path (:func:`check_entry_admissible`) and the
    Edition path (:func:`spine.edition.build_edition`) so the *package* layer
    cannot launder a legitimacy verb either. Freezing a render adds immutability,
    never authority."""
    illegal = [a for a in spine_assertions if a not in SPINE_ASSERTIONS]
    if illegal:
        # Name the legitimacy verb explicitly when that's what was attempted.
        raise SpineBearsStatusError(
            f"spine_assertions may contain only {sorted(SPINE_ASSERTIONS)}; "
            f"Spine may not assert {illegal!r} "
            f"(findability is not legitimacy)"
        )


def check_entry_admissible(
    *,
    canonical_location: str,
    reported_status: str,
    status_source_ref: str | None,
    witness_ref: str | None,
    ingress_adapter: str,
    spine_assertions: Iterable[str],
) -> None:
    """Enforce the read-plane wall on a would-be index entry.

    Order is the doctrine:

    1. Spine may assert only ``located`` / ``rendered`` — never a legitimacy
       verb (``SpineBearsStatusError``). This is the wall: index presence
       confers no status.
    2. reported_status must be in the closed vocabulary (``UnknownStatusError``).
    3. A reported status must quote its source (``UnsourcedStatusError``) —
       except ``unknown``, which is the honest "Spine doesn't know" and needs no
       source.
    4. A governed claim (``ratified``) must carry a witness
       (``UnwitnessedGovernedClaimError``).
    5. The ingress adapter must be known (``UnknownIngressError``).
    """
    if not canonical_location or not canonical_location.strip():
        raise SpineRefusal("canonical_location is required")

    check_spine_assertions(spine_assertions)

    if reported_status not in REPORTED_STATUSES:
        raise UnknownStatusError(
            f"reported_status {reported_status!r} not in {sorted(REPORTED_STATUSES)}"
        )

    if reported_status != STATUS_UNKNOWN and not (status_source_ref and status_source_ref.strip()):
        raise UnsourcedStatusError(
            f"reported_status {reported_status!r} requires a status_source_ref "
            "(Spine quotes a governing surface; it does not become one)"
        )

    if reported_status in AUTHORITATIVE_STATUSES and not (witness_ref and witness_ref.strip()):
        raise UnwitnessedGovernedClaimError(
            f"reported_status {reported_status!r} claims governed authority and "
            "requires a witness_ref; a missing witness on a governed claim is a "
            "hard refusal, not a warning"
        )

    if ingress_adapter not in KNOWN_INGRESS_ADAPTERS:
        raise UnknownIngressError(
            f"ingress_adapter {ingress_adapter!r} not in {sorted(KNOWN_INGRESS_ADAPTERS)}"
        )
