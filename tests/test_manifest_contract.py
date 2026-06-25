# SPDX-License-Identifier: Apache-2.0
"""The provisional_git_manifest_v0 contract: declared, concrete, no crawling.

> The adapter is incapable of crawling — it reads declared, concrete file
> references or it refuses.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spine import build_index, load_manifest
from spine.refusal import CrawlAttemptError, MalformedManifestError, UnknownIngressError

_SPECIMEN = Path(__file__).resolve().parents[1] / "specimens" / "predicate_witness_manifest.yaml"
_OBSERVED = "2026-06-25T00:00:00Z"


def _write(tmp_path, data) -> Path:
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(data))
    return p


def _artifact(path: str) -> dict:
    return {
        "repo": "agent_gov",
        "path": path,
        "reported_status": "candidate",
        "status_source_ref": "self:header",
    }


# --- the specimen corpus loads and builds ----------------------------------- #


def test_specimen_manifest_builds():
    manifest = load_manifest(_SPECIMEN)
    index = build_index(manifest, observed_at=_OBSERVED)
    assert len(index.entries) == 7
    # The whole family is candidate + unwitnessed — and the index says so.
    assert all(e.reported_status == "candidate" for e in index.entries)
    assert all(e.witness_ref is None for e in index.entries)


def test_specimen_index_is_deterministic():
    """Same manifest, same observed_at -> byte-identical index (stable order +
    stable digests)."""
    m = load_manifest(_SPECIMEN)
    a = build_index(m, observed_at=_OBSERVED)
    b = build_index(load_manifest(_SPECIMEN), observed_at=_OBSERVED)
    assert a.index_digest == b.index_digest
    assert a.model_dump_json() == b.model_dump_json()
    # Sorted by canonical_location.
    locs = [e.canonical_location for e in a.entries]
    assert locs == sorted(locs)


# --- no crawling: discovery directives are refused, not executed ------------ #


@pytest.mark.parametrize(
    "bad_path",
    [
        "docs/**/*.md",        # recursive glob
        "docs/*.md",           # glob
        "docs/",               # directory
        "docs/cross-tool",     # directory (no extension is still treated as a ref;
                               #   the trailing-slash + glob rules are the crawl fence)
    ],
)
def test_manifest_does_not_crawl_repositories(tmp_path, bad_path):
    """A path that asks the adapter to discover material is refused. (The
    no-extension dir case is allowed as a concrete ref; only globs/dirs crawl.)"""
    data = {"adapter": "provisional_git_manifest_v0", "artifacts": [_artifact(bad_path)]}
    if bad_path.endswith("/") or any(m in bad_path for m in ("*", "?", "[", "]", "{", "}")):
        with pytest.raises(CrawlAttemptError):
            load_manifest(_write(tmp_path, data))
    else:
        # A bare directory-looking ref with no trailing slash / glob is treated as
        # a concrete (if odd) reference — the fence is globs and trailing slashes,
        # not a heuristic guess about directories.
        m = load_manifest(_write(tmp_path, data))
        assert m.artifacts[0].path == bad_path


def test_unknown_adapter_refused(tmp_path):
    data = {"adapter": "spine_crawls_everything_v9", "artifacts": []}
    with pytest.raises(UnknownIngressError):
        load_manifest(_write(tmp_path, data))


def test_extra_top_level_key_refused(tmp_path):
    """A crawl-shaped top-level key (e.g. recurse: true) is refused by the closed
    schema — surfaced as a typed MalformedManifestError, not a raw stack trace."""
    data = {
        "adapter": "provisional_git_manifest_v0",
        "artifacts": [],
        "recurse": True,
    }
    with pytest.raises(MalformedManifestError):
        load_manifest(_write(tmp_path, data))
