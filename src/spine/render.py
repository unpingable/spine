# SPDX-License-Identifier: Apache-2.0
"""The sign-says view — render an index so the refusal is visible.

The rendered output must never print a bare legitimacy verb for an entry. It
prints *"the sign says <reported_status>"* (with the source), and *"witness:
NONE — unwitnessed"* where there is no witness. The reader is never allowed to
mistake a found thing for a warranted thing.
"""

from __future__ import annotations

from .index import SpineIndex
from .refusal import AUTHORITATIVE_STATUSES, STATUS_UNKNOWN

_HEADER = """\
# Spine index — {adapter}

> **Findability is not legitimacy.** Every entry below is *located and rendered*
> by Spine. Spine reports what each artifact's governing surface says; it does
> not certify, ratify, or witness anything here. "The sign says ratified" is not
> "ratified."

Ingress: `{adapter}` (provisional — Spine reads from Continuity in the final
architecture). Observed at: `{observed_at}`. Index digest: `{index_digest}`.

| Artifact | Spine asserts | The sign says | Source | Witness |
|----------|---------------|---------------|--------|---------|
"""


def _status_cell(entry) -> str:
    """The reported status, always framed as a quotation — never a bare verb."""
    if entry.reported_status == STATUS_UNKNOWN:
        return "_(no status reported)_"
    governed = entry.reported_status in AUTHORITATIVE_STATUSES
    # Even a governed claim is quoted, never asserted by Spine.
    mark = " ⚠ governed-claim" if governed else ""
    return f'the sign says **{entry.reported_status}**{mark}'


def render_markdown(index: SpineIndex) -> str:
    """Render a ``SpineIndex`` as a navigable markdown table with the refusal
    visible. Pure; returns the string."""
    out = [
        _HEADER.format(
            adapter=index.ingress_adapter,
            observed_at=index.observed_at,
            index_digest=index.index_digest,
        )
    ]
    for e in index.entries:
        asserts = " · ".join(e.spine_assertions)
        source = f"`{e.status_source_ref}`" if e.status_source_ref else "—"
        witness = f"`{e.witness_ref}`" if e.witness_ref else "**NONE — unwitnessed**"
        out.append(
            f"| `{e.canonical_location}` | {asserts} | {_status_cell(e)} "
            f"| {source} | {witness} |"
        )
    out.append("")
    out.append(
        "_Spine asserts only `located` / `rendered`. A blank or unwitnessed "
        "entry is exactly that — navigational, not authoritative._"
    )
    return "\n".join(out) + "\n"
