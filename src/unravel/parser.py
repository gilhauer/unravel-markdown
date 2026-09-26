import re
from dataclasses import dataclass, field
from pathlib import Path

from .exceptions import MalformedChunkError

# This intentionally implements only the fenced-block subset documented in the
# README.  In particular, executable fences cannot be nested in ordinary ones.
FENCE_OPEN = re.compile(
    r"^ {0,3}((?:`{3,})|(?:~{3,}))[ \t]*(?:[^\s<>]+[ \t]+)?<<([^>]+)>>[ \t]*$"
)
ANY_FENCE_OPEN = re.compile(r"^ {0,3}((?:`{3,})|(?:~{3,}))(.*)$")


@dataclass
class ChunkLine:
    text: str
    lineno: int


@dataclass
class Chunk:
    name: str
    lines: list[ChunkLine] = field(default_factory=list)
    defined_at: int = 0  # line number of the opening fence
    definitions: list[int] = field(default_factory=list)


def is_root(name: str) -> bool:
    """Return whether a chunk name uses the legacy filename convention."""
    return "." in name


def _is_close(line: str, marker: str) -> bool:
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    return (
        indent <= 3
        and stripped.startswith(marker[0] * len(marker))
        and len(stripped.rstrip()) >= len(marker)
        and set(stripped.rstrip()) == {marker[0]}
    )


def parse(source: Path) -> tuple[dict[str, Chunk], str]:
    """Parse a Markdown file and return a chunk table and the source filename."""
    chunks: dict[str, Chunk] = {}
    lines = source.read_text(encoding="utf-8").splitlines()

    current_chunk: Chunk | None = None
    fence_marker: str | None = None
    ordinary_marker: str | None = None

    for lineno, line in enumerate(lines, 1):
        if ordinary_marker is not None:
            if _is_close(line, ordinary_marker):
                ordinary_marker = None
            continue

        if current_chunk is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence_marker = m.group(1)
                name = m.group(2).strip()
                if not name:
                    raise MalformedChunkError(f"{source}:{lineno}: empty chunk name")
                if name not in chunks:
                    chunks[name] = Chunk(
                        name=name, defined_at=lineno, definitions=[lineno]
                    )
                else:
                    if is_root(name):
                        first = chunks[name].defined_at
                        raise MalformedChunkError(
                            f'{source}:{lineno}: duplicate output root "{name}"; '
                            f"first defined at {source}:{first}"
                        )
                    chunks[name].definitions.append(lineno)
                current_chunk = chunks[name]
                continue
            ordinary = ANY_FENCE_OPEN.match(line)
            if ordinary:
                ordinary_marker = ordinary.group(1)
        else:
            if _is_close(line, fence_marker):
                current_chunk = None
                fence_marker = None
            else:
                current_chunk.lines.append(ChunkLine(text=line, lineno=lineno))

    if current_chunk is not None:
        raise MalformedChunkError(
            f'{source}:{current_chunk.definitions[-1]}: unterminated chunk "{current_chunk.name}"'
        )

    return chunks, source.name
