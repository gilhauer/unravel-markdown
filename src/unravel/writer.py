from pathlib import Path
from .parser import Chunk
from .expander import expand_chunk


def is_root(name: str) -> bool:
    """A root chunk is one whose name contains a period (i.e., a filename)."""
    return "." in name


def write_roots(
    chunks: dict[str, Chunk],
    source_file: str,
    output_dir: Path,
) -> list[str]:
    """Expand and write all root chunks to disk.

    Returns the list of filenames written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    for name in chunks:
        if is_root(name):
            lines = expand_chunk(name, chunks, source_file)
            output_path = output_dir / name
            output_path.write_text("\n".join(lines) + "\n")
            written.append(name)

    return written
