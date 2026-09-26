"""Unravel: extract source files from a literate Markdown document."""

from .parser import parse, Chunk, ChunkLine
from .expander import expand_chunk
from .writer import check_roots, plan_generation, write_roots
from .parser import is_root
from .exceptions import UnravelError, UndefinedChunkError, CircularReferenceError, MalformedChunkError

__all__ = [
    "parse",
    "Chunk",
    "ChunkLine",
    "expand_chunk",
    "write_roots",
    "check_roots",
    "plan_generation",
    "is_root",
    "UnravelError",
    "UndefinedChunkError",
    "CircularReferenceError",
    "MalformedChunkError",
]
