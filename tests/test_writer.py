import pytest
from pathlib import Path

from unravel.parser import Chunk, ChunkLine
from unravel.writer import write_roots, is_root


def make_chunk(name: str, lines: list[str]) -> Chunk:
    chunk_lines = [ChunkLine(text=t, lineno=i + 1) for i, t in enumerate(lines)]
    return Chunk(name=name, lines=chunk_lines, defined_at=1)


def test_is_root():
    assert is_root("main.py")
    assert is_root("README.md")
    assert is_root("style.css")
    assert not is_root("helper")
    assert not is_root("cross_out")


def test_write_root_chunk(tmp_path):
    chunks = {"main.py": make_chunk("main.py", ["print('hello')"])}
    written = write_roots(chunks, "src.md", tmp_path)
    assert "main.py" in written
    assert (tmp_path / "main.py").read_text() == "print('hello')\n"


def test_non_root_not_written(tmp_path):
    chunks = {
        "main.py": make_chunk("main.py", ["x = 1"]),
        "helper": make_chunk("helper", ["pass"]),
    }
    written = write_roots(chunks, "src.md", tmp_path)
    assert "main.py" in written
    assert "helper" not in written
    assert not (tmp_path / "helper").exists()


def test_root_expansion(tmp_path):
    chunks = {
        "main.py": make_chunk("main.py", ["<<greeting>>"]),
        "greeting": make_chunk("greeting", ["print('hi')"]),
    }
    write_roots(chunks, "src.md", tmp_path)
    assert (tmp_path / "main.py").read_text() == "print('hi')\n"


def test_blank_lines_in_output(tmp_path):
    chunks = {"out.txt": make_chunk("out.txt", ["a", "", "b"])}
    write_roots(chunks, "src.md", tmp_path)
    assert (tmp_path / "out.txt").read_text() == "a\n\nb\n"


def test_output_dir_created(tmp_path):
    output_dir = tmp_path / "nested" / "output"
    chunks = {"out.txt": make_chunk("out.txt", ["hello"])}
    write_roots(chunks, "src.md", output_dir)
    assert (output_dir / "out.txt").exists()


def test_multiple_root_chunks_written(tmp_path):
    chunks = {
        "a.py": make_chunk("a.py", ["x = 1"]),
        "b.py": make_chunk("b.py", ["y = 2"]),
    }
    written = write_roots(chunks, "src.md", tmp_path)
    assert set(written) == {"a.py", "b.py"}
    assert (tmp_path / "a.py").read_text() == "x = 1\n"
    assert (tmp_path / "b.py").read_text() == "y = 2\n"
