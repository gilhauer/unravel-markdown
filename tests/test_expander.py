import pytest

from unravel.parser import Chunk, ChunkLine
from unravel.expander import expand_chunk
from unravel.exceptions import UndefinedChunkError, CircularReferenceError


def make_chunk(name: str, lines: list[str], defined_at: int = 1) -> Chunk:
    """Build a Chunk from plain strings for use in tests."""
    chunk_lines = [ChunkLine(text=t, lineno=defined_at + i + 1) for i, t in enumerate(lines)]
    return Chunk(name=name, lines=chunk_lines, defined_at=defined_at)


def test_simple_expansion():
    chunks = {"main": make_chunk("main", ["hello", "world"])}
    assert expand_chunk("main", chunks, "src.md") == ["hello", "world"]


def test_nested_expansion():
    chunks = {
        "main": make_chunk("main", ["before", "<<inner>>", "after"]),
        "inner": make_chunk("inner", ["inside"]),
    }
    assert expand_chunk("main", chunks, "src.md") == ["before", "inside", "after"]


def test_indentation_preserved():
    chunks = {
        "main": make_chunk("main", ["def f():", "    <<body>>"]),
        "body": make_chunk("body", ["x = 1", "return x"]),
    }
    result = expand_chunk("main", chunks, "src.md")
    assert result == ["def f():", "    x = 1", "    return x"]


def test_nested_indentation():
    chunks = {
        "outer": make_chunk("outer", ["  <<inner>>"]),
        "inner": make_chunk("inner", ["  <<leaf>>"]),
        "leaf": make_chunk("leaf", ["deep"]),
    }
    result = expand_chunk("outer", chunks, "src.md")
    assert result == ["    deep"]


def test_blank_lines_preserved():
    chunks = {"main": make_chunk("main", ["a", "", "b"])}
    assert expand_chunk("main", chunks, "src.md") == ["a", "", "b"]


def test_blank_lines_not_indented():
    chunks = {
        "main": make_chunk("main", ["    <<body>>"]),
        "body": make_chunk("body", ["x = 1", "", "y = 2"]),
    }
    result = expand_chunk("main", chunks, "src.md")
    assert result == ["    x = 1", "", "    y = 2"]


def test_undefined_chunk_raises():
    chunks = {"main": make_chunk("main", ["<<missing>>"])}
    with pytest.raises(UndefinedChunkError):
        expand_chunk("main", chunks, "src.md")


def test_undefined_chunk_error_message():
    chunks = {"main": make_chunk("main", ["<<missing>>"], defined_at=5)}
    with pytest.raises(UndefinedChunkError) as exc_info:
        expand_chunk("main", chunks, "src.md")
    msg = str(exc_info.value)
    assert '"missing"' in msg
    assert '"main"' in msg
    assert "src.md:6" in msg


def test_circular_reference_raises():
    chunks = {
        "a": make_chunk("a", ["<<b>>"]),
        "b": make_chunk("b", ["<<a>>"]),
    }
    with pytest.raises(CircularReferenceError) as exc_info:
        expand_chunk("a", chunks, "src.md")
    assert "a -> b -> a" in str(exc_info.value)


def test_self_reference_raises():
    chunks = {"a": make_chunk("a", ["<<a>>"])}
    with pytest.raises(CircularReferenceError) as exc_info:
        expand_chunk("a", chunks, "src.md")
    assert "a -> a" in str(exc_info.value)


def test_three_chunk_cycle_raises():
    chunks = {
        "a": make_chunk("a", ["<<b>>"]),
        "b": make_chunk("b", ["<<c>>"]),
        "c": make_chunk("c", ["<<a>>"]),
    }
    with pytest.raises(CircularReferenceError) as exc_info:
        expand_chunk("a", chunks, "src.md")
    assert "a -> b -> c -> a" in str(exc_info.value)


def test_multiple_references_in_chunk():
    chunks = {
        "main": make_chunk("main", ["<<a>>", "<<b>>"]),
        "a": make_chunk("a", ["line_a"]),
        "b": make_chunk("b", ["line_b"]),
    }
    assert expand_chunk("main", chunks, "src.md") == ["line_a", "line_b"]
