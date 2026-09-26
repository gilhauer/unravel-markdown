import argparse
import sys
from pathlib import Path

from .parser import parse
from .writer import write_roots, is_root
from .exceptions import UnravelError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="unravel",
        description="Extract source files from a literate Markdown document.",
    )
    p.add_argument("source", type=Path, help="Markdown source file")
    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Directory to write output files (default: same directory as source)",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List all chunks and indicate which are roots",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir: Path = args.output_dir or args.source.parent

    try:
        chunks, source_file = parse(args.source)
    except FileNotFoundError:
        print(f"unravel: file not found: {args.source}", file=sys.stderr)
        return 1
    except UnravelError as e:
        print(f"unravel: {e}", file=sys.stderr)
        return 1

    if args.list:
        for name in chunks:
            marker = " [root]" if is_root(name) else ""
            print(f"  {name}{marker}")
        return 0

    try:
        written = write_roots(chunks, source_file, output_dir)
    except UnravelError as e:
        print(f"unravel: {e}", file=sys.stderr)
        return 1

    for name in written:
        print(f"wrote {output_dir / name}")

    return 0
