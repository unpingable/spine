# SPDX-License-Identifier: Apache-2.0
"""The stupid CLI. Three verbs: build, render, edition. No daemon, no database,
no plugins.

    spine build specimens/predicate_witness_manifest.yaml --out output/index.json
    spine render output/index.json --out output/index.md
    spine edition create specimens/predicate_witness_manifest.yaml \\
        --created-at 2026-06-25T00:00:00Z --out editions
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .edition import write_edition
from .index import SpineIndex, build_index
from .manifest import load_manifest
from .refusal import SpineRefusal
from .render import render_markdown


def _cmd_build(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    index = build_index(manifest, observed_at=args.observed_at)
    out = index.model_dump_json(indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out + "\n")
        print(f"built {len(index.entries)} entries -> {args.out} ({index.index_digest})")
    else:
        print(out)
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    index = SpineIndex.model_validate_json(Path(args.index).read_text())
    md = render_markdown(index)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(md)
        print(f"rendered {len(index.entries)} entries -> {args.out}")
    else:
        sys.stdout.write(md)
    return 0


def _cmd_edition_create(args: argparse.Namespace) -> int:
    edition, edition_dir = write_edition(
        args.manifest, created_at=args.created_at, out_root=args.out
    )
    print(f"froze edition {edition.edition_id} -> {edition_dir}")
    print("  (An Edition freezes what Spine located; it does not ratify it.)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spine", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a deterministic index from a manifest")
    b.add_argument("manifest")
    b.add_argument("--out", help="write index JSON here (default: stdout)")
    b.add_argument(
        "--observed-at",
        required=True,
        help="ISO 8601 observation time (explicit, for determinism)",
    )
    b.set_defaults(func=_cmd_build)

    r = sub.add_parser("render", help="render an index as the sign-says markdown view")
    r.add_argument("index")
    r.add_argument("--out", help="write markdown here (default: stdout)")
    r.set_defaults(func=_cmd_render)

    e = sub.add_parser(
        "edition", help="package an immutable, citable edition of a render"
    )
    esub = e.add_subparsers(dest="edition_cmd", required=True)
    ec = esub.add_parser(
        "create",
        help="freeze a manifest+index+render into an immutable edition directory",
    )
    ec.add_argument("manifest")
    ec.add_argument(
        "--created-at",
        required=True,
        help="ISO 8601 packaging time (explicit, for determinism)",
    )
    ec.add_argument(
        "--out",
        required=True,
        help="editions root; the edition is written to <out>/<edition_id>",
    )
    ec.set_defaults(func=_cmd_edition_create)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SpineRefusal as exc:
        # Fail closed and loud: a refusal is the point, not an error to swallow.
        print(f"spine refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
