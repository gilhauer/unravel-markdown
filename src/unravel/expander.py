import re
from .parser import Chunk, ChunkLine
from .exceptions import UndefinedChunkError, CircularReferenceError

# Matches a chunk reference, possibly indented: optional whitespace + <<name>>
REFERENCE_RE = re.compile(r"^(\s*)<<([^>]+)>>\s*$")


def expand_chunk(
    name: str,
    chunks: dict[str, Chunk],
    source_file: str,
    indent: str = "",
    stack: list[str] | None = None,
    reference_sites: list[str] | None = None,
) -> list[str]:
    """Recursively expand a chunk, propagating indentation and detecting cycles.

    ``indent`` is the cumulative indentation inherited from parent references.
    ``stack`` is the current expansion path, used for cycle detection.
    """
    if stack is None:
        stack = []
    if reference_sites is None:
        reference_sites = []

    if name in stack:
        start = stack.index(name)
        cycle = stack[start:] + [name]
        raise CircularReferenceError(cycle, reference_sites[start:])

    chunk = chunks[name]  # caller ensures name is present
    new_stack = stack + [name]
    result: list[str] = []

    for chunk_line in chunk.lines:
        m = REFERENCE_RE.match(chunk_line.text)
        if m:
            ref_indent = m.group(1)
            ref_name = m.group(2).strip()
            if ref_name not in chunks:
                raise UndefinedChunkError(
                    ref_name,
                    name,
                    f"{source_file}:{chunk_line.lineno}",
                    new_stack + [ref_name],
                )
            expanded = expand_chunk(
                ref_name,
                chunks,
                source_file,
                indent + ref_indent,
                new_stack,
                reference_sites + [f"{source_file}:{chunk_line.lineno}"],
            )
            result.extend(expanded)
        elif chunk_line.text.strip() == "":
            # Blank lines stay blank regardless of indentation context
            result.append("")
        else:
            result.append(indent + chunk_line.text)

    return result
