import argparse
import sys
from pathlib import Path

from .parser import is_root, parse
from .writer import check_roots, write_roots
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
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--list",
        action="store_true",
        help="List all chunks and indicate which are roots",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Check that output and its manifest are current without writing",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir: Path = args.output_dir or args.source.parent

    try:
        chunks, _ = parse(args.source)
        source_file = str(args.source)
    except FileNotFoundError:
        print(f"unravel: file not found: {args.source}", file=sys.stderr)
        return 1
    except (UnravelError, OSError, UnicodeError) as e:
        print(f"unravel: {e}", file=sys.stderr)
        return 1

    if args.list:
        for name in sorted(chunks):
            marker = " [root]" if is_root(name) else ""
            print(f"  {name}{marker}")
        return 0

    try:
        if args.check:
            written = check_roots(
                chunks, source_file, output_dir, source_path=args.source
            )
        else:
            written = write_roots(
                chunks, source_file, output_dir, source_path=args.source
            )
    except (UnravelError, OSError, UnicodeError) as e:
        print(f"unravel: {e}", file=sys.stderr)
        return 1

    for name in written:
        action = "current" if args.check else "wrote"
        print(f"{action} {output_dir / name}")

    return 0
