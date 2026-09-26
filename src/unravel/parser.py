import re
from dataclasses import dataclass, field
from pathlib import Path

# Matches an opening fence: backticks, optional language, chunk name in <<...>>
FENCE_OPEN = re.compile(r"^(`{3,})\s*(?:\w+\s+)?<<([^>]+)>>\s*$")


@dataclass
class ChunkLine:
    text: str
    lineno: int


@dataclass
class Chunk:
    name: str
    lines: list[ChunkLine] = field(default_factory=list)
    defined_at: int = 0  # line number of the opening fence


def parse(source: Path) -> tuple[dict[str, Chunk], str]:
    """Parse a Markdown file and return a chunk table and the source filename."""
    chunks: dict[str, Chunk] = {}
    lines = source.read_text().splitlines()

    current_chunk: Chunk | None = None
    fence_marker: str | None = None

    for lineno, line in enumerate(lines, 1):
        if current_chunk is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence_marker = m.group(1)
                name = m.group(2).strip()
                if name not in chunks:
                    chunks[name] = Chunk(name=name, defined_at=lineno)
                current_chunk = chunks[name]
        else:
            # A closing fence starts with the same backticks and has nothing else
            if line.startswith(fence_marker) and line[len(fence_marker):].strip() == "":
                current_chunk = None
                fence_marker = None
            else:
                current_chunk.lines.append(ChunkLine(text=line, lineno=lineno))

    return chunks, source.name
