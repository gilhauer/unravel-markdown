import pytest
from pathlib import Path

from unravel.parser import parse, Chunk, ChunkLine


@pytest.fixture
def md(tmp_path):
    """Write content to a temp source.md and return its path."""
    def write(content: str) -> Path:
        p = tmp_path / "source.md"
        p.write_text(content)
        return p
    return write


def test_single_chunk(md):
    path = md("```python <<greet>>\nprint('hello')\n```\n")
    chunks, _ = parse(path)
    assert "greet" in chunks
    assert [l.text for l in chunks["greet"].lines] == ["print('hello')"]


def test_two_chunks(md):
    path = md("```python <<a>>\nline_a\n```\n\n```python <<b>>\nline_b\n```\n")
    chunks, _ = parse(path)
    assert set(chunks) == {"a", "b"}


def test_chunk_concatenation(md):
    path = md("```python <<a>>\nfirst\n```\n\n```python <<a>>\nsecond\n```\n")
    chunks, _ = parse(path)
    texts = [l.text for l in chunks["a"].lines]
    assert texts == ["first", "second"]


def test_blank_lines_preserved(md):
    path = md("```python <<a>>\nx = 1\n\ny = 2\n```\n")
    chunks, _ = parse(path)
    texts = [l.text for l in chunks["a"].lines]
    assert texts == ["x = 1", "", "y = 2"]


def test_language_optional(md):
    path = md("``` <<helper>>\npass\n```\n")
    chunks, _ = parse(path)
    assert "helper" in chunks


def test_line_numbers(md):
    # Line 1: "# Title", Line 2: blank, Line 3: fence open, Line 4: "line one"
    path = md("# Title\n\n```python <<chunk>>\nline one\n```\n")
    chunks, _ = parse(path)
    assert chunks["chunk"].defined_at == 3
    assert chunks["chunk"].lines[0].lineno == 4


def test_source_filename(md):
    path = md("# empty\n")
    _, name = parse(path)
    assert name == "source.md"


def test_no_chunks(md):
    path = md("# Just text\n\nNo code here.\n")
    chunks, _ = parse(path)
    assert chunks == {}


def test_regular_fence_ignored(md):
    path = md("```python\nnot a chunk\n```\n")
    chunks, _ = parse(path)
    assert chunks == {}


def test_multiple_definitions_preserve_order(md):
    path = md(
        "```python <<a>>\nfirst\nsecond\n```\n"
        "\n"
        "```python <<a>>\nthird\n```\n"
    )
    chunks, _ = parse(path)
    texts = [l.text for l in chunks["a"].lines]
    assert texts == ["first", "second", "third"]


def test_defined_at_is_first_definition(md):
    # First definition is at line 1; second at line 4
    path = md("```python <<a>>\nfirst\n```\n```python <<a>>\nsecond\n```\n")
    chunks, _ = parse(path)
    assert chunks["a"].defined_at == 1
