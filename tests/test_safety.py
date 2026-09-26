import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from unravel.exceptions import (
    CheckError,
    MalformedChunkError,
    ManifestError,
    OwnershipError,
    UnsafePathError,
)
from unravel.parser import Chunk, ChunkLine, parse
from unravel.writer import MANIFEST_NAME, check_roots, plan_generation, write_roots


def chunk(name: str, lines: list[str], line: int = 1) -> Chunk:
    return Chunk(
        name=name,
        lines=[ChunkLine(text=text, lineno=line + i + 1) for i, text in enumerate(lines)],
        defined_at=line,
        definitions=[line],
    )


def generate(source: Path, output: Path) -> list[str]:
    chunks, source_file = parse(source)
    return write_roots(chunks, source_file, output, source)


@pytest.mark.parametrize(
    "name",
    [
        "../escape.py",
        "a/../escape.py",
        "a/./x.py",
        "a//x.py",
        "/absolute.py",
        r"C:\absolute.py",
        "C:relative.py",
        r"\\server\share\x.py",
        r"a\b.py",
        "NUL.txt",
        "com1.py",
        "CON .txt",
        "trailing./x.py",
        "trailing /x.py",
        "stream.py:secret",
        "bad\x00.py",
        ".unravel-manifest.json",
        ".unravel-tmp-owned.py",
    ],
)
def test_rejects_nonportable_paths_before_creating_output(tmp_path, name):
    output = tmp_path / "new"
    with pytest.raises(UnsafePathError):
        plan_generation({name: chunk(name, ["x"])}, "source.md", output)
    assert not output.exists()


@pytest.mark.parametrize(
    "names",
    [
        ["A/x.py", "a/y.py"],
        ["a.py", "A.py"],
        ["dir.py", "dir.py/child.txt"],
    ],
)
def test_rejects_portable_collisions(tmp_path, names):
    chunks = {name: chunk(name, [name]) for name in names}
    with pytest.raises(UnsafePathError):
        plan_generation(chunks, "source.md", tmp_path / "output")


def test_full_plan_expands_before_any_filesystem_change(tmp_path):
    output = tmp_path / "output"
    chunks = {
        "a.txt": chunk("a.txt", ["valid"]),
        "z.txt": chunk("z.txt", ["<<missing>>"]),
    }
    with pytest.raises(Exception, match="missing"):
        write_roots(chunks, "source.md", output)
    assert not output.exists()


def test_nested_generation_manifest_and_sorted_reporting(tmp_path):
    output = tmp_path / "output"
    chunks = {
        "z/file.txt": chunk("z/file.txt", ["z"]),
        "a/deep/file.txt": chunk("a/deep/file.txt", ["héllo", ""]),
    }
    assert write_roots(chunks, "source.md", output) == [
        "a/deep/file.txt",
        "z/file.txt",
    ]
    assert (output / "a/deep/file.txt").read_bytes() == "héllo\n\n".encode()
    manifest = json.loads((output / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest == {
        "version": 1,
        "files": {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in ["a/deep/file.txt", "z/file.txt"]
        },
    }


def test_empty_chunks_trailing_blanks_and_crlf_have_explicit_lf_policy(tmp_path):
    source = tmp_path / "source.md"
    source.write_bytes(
        b"```text <<empty.txt>>\r\n```\r\n"
        b"```text <<blank.txt>>\r\nline\r\n\r\n```\r\n"
    )
    output = tmp_path / "output"
    generate(source, output)
    assert (output / "empty.txt").read_bytes() == b"\n"
    assert (output / "blank.txt").read_bytes() == b"line\n\n"


def test_repeat_and_fresh_generation_are_byte_identical(tmp_path):
    source = Path(__file__).parent / "fixtures/open_observatory.md"
    first, second = tmp_path / "first", tmp_path / "second"
    generate(source, first)
    before = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    generate(source, first)
    generate(source, second)
    after = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    fresh = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert before == after == fresh


def test_owned_update_and_missing_file_recovery(tmp_path):
    output = tmp_path / "output"
    write_roots({"x.txt": chunk("x.txt", ["one"])}, "source.md", output)
    write_roots({"x.txt": chunk("x.txt", ["two"])}, "source.md", output)
    assert (output / "x.txt").read_bytes() == b"two\n"
    (output / "x.txt").unlink()
    write_roots({"x.txt": chunk("x.txt", ["two"])}, "source.md", output)
    assert (output / "x.txt").read_bytes() == b"two\n"


def test_refuses_modified_owned_unowned_and_stale_files(tmp_path):
    output = tmp_path / "output"
    write_roots({"x.txt": chunk("x.txt", ["one"])}, "source.md", output)
    (output / "x.txt").write_text("local\n")
    with pytest.raises(OwnershipError, match="locally modified"):
        write_roots({"x.txt": chunk("x.txt", ["two"])}, "source.md", output)
    assert (output / "x.txt").read_text() == "local\n"

    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "x.txt").write_text("unowned\n")
    with pytest.raises(OwnershipError, match="unowned"):
        write_roots({"x.txt": chunk("x.txt", ["one"])}, "source.md", clean)
    assert (clean / "x.txt").read_text() == "unowned\n"

    stale = tmp_path / "stale"
    write_roots({"old.txt": chunk("old.txt", ["old"])}, "source.md", stale)
    with pytest.raises(OwnershipError, match="stale"):
        write_roots({"new.txt": chunk("new.txt", ["new"])}, "source.md", stale)
    assert (stale / "old.txt").read_bytes() == b"old\n"
    assert not (stale / "new.txt").exists()


def test_manifest_is_strictly_validated(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    (output / MANIFEST_NAME).write_text('{"version": 2, "files": {}}')
    with pytest.raises(ManifestError):
        write_roots({"x.txt": chunk("x.txt", ["x"])}, "source.md", output)


def test_check_is_read_only_for_current_changed_missing_stale_and_absent(tmp_path):
    output = tmp_path / "output"
    chunks = {"x.txt": chunk("x.txt", ["x"])}
    write_roots(chunks, "source.md", output)
    paths = [output / "x.txt", output / MANIFEST_NAME]
    snapshot = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
    assert check_roots(chunks, "source.md", output) == ["x.txt"]
    assert snapshot == [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]

    (output / "x.txt").write_text("changed")
    changed = (output / "x.txt").read_bytes(), (output / "x.txt").stat().st_mtime_ns
    with pytest.raises(CheckError):
        check_roots(chunks, "source.md", output)
    assert changed == ((output / "x.txt").read_bytes(), (output / "x.txt").stat().st_mtime_ns)

    missing = tmp_path / "missing"
    with pytest.raises(CheckError, match="missing manifest"):
        check_roots(chunks, "source.md", missing)
    assert not missing.exists()

    stale = tmp_path / "stale-check"
    write_roots(
        {"old.txt": chunk("old.txt", ["old"]), "x.txt": chunk("x.txt", ["x"])},
        "source.md",
        stale,
    )
    stale_before = {
        path.relative_to(stale): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in stale.rglob("*") if path.is_file()
    }
    with pytest.raises(CheckError, match="stale owned output"):
        check_roots(chunks, "source.md", stale)
    assert stale_before == {
        path.relative_to(stale): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in stale.rglob("*") if path.is_file()
    }


def test_input_symlink_and_hardlink_protection(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("``` <<source.md>>\nchanged\n```\n")
    with pytest.raises(OwnershipError, match="input Markdown"):
        generate(source, tmp_path)
    assert source.read_text().startswith("```")

    target = tmp_path / "target"
    target.mkdir()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("safe")
    os.symlink(sentinel, target / "x.txt")
    with pytest.raises(OwnershipError, match="symlink"):
        write_roots({"x.txt": chunk("x.txt", ["bad"])}, "source.md", target)
    assert sentinel.read_text() == "safe"

    linked = tmp_path / "linked"
    write_roots({"x.txt": chunk("x.txt", ["old"])}, "source.md", linked)
    alias = tmp_path / "alias.txt"
    os.link(linked / "x.txt", alias)
    with pytest.raises(OwnershipError, match="hard links"):
        write_roots({"x.txt": chunk("x.txt", ["new"])}, "source.md", linked)
    assert alias.read_bytes() == b"old\n"


def test_output_directory_symlink_and_dangling_link_are_rejected(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    with pytest.raises(OwnershipError, match="symlink"):
        write_roots({"x.txt": chunk("x.txt", ["x"])}, "source.md", link)
    dangling = tmp_path / "dangling"
    dangling.symlink_to(tmp_path / "nowhere")
    with pytest.raises(OwnershipError, match="symlink"):
        write_roots({"x.txt": chunk("x.txt", ["x"])}, "source.md", dangling)


def test_fixture_has_expected_composition(tmp_path):
    source = Path(__file__).parent / "fixtures/open_observatory.md"
    output = tmp_path / "output"
    names = generate(source, output)
    assert names == sorted([
        "application/observatory.py",
        "tests/test_observation.py",
        "ansible/inventory.yml",
        "ansible/playbooks/site.yml",
        "ansible/roles/observatory/tasks/main.yml",
        "terraform/main.tf",
        "terraform/variables.tf",
        "terraform/outputs.tf",
        "terraform/modules/station/main.tf",
    ])
    application = (output / "application/observatory.py").read_text(encoding="utf-8")
    assert "Reykjavík" in application
    assert 'NETWORK = "open-observatory"' in application

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(output / "tests/test_observation.py")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_separate_processes_and_hash_seeds_are_reproducible(tmp_path):
    source = Path(__file__).parent / "fixtures/open_observatory.md"
    snapshots = []
    for seed in ("1", "987654"):
        output = tmp_path / f"seed-{seed}"
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = seed
        completed = subprocess.run(
            [sys.executable, "-m", "unravel", str(source), "-o", str(output)],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        snapshots.append(
            {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
        )
    assert snapshots[0] == snapshots[1]


def test_duplicate_root_unclosed_chunk_and_literal_fences(tmp_path):
    duplicate = tmp_path / "duplicate.md"
    duplicate.write_text("``` <<x.py>>\na\n```\n``` <<x.py>>\nb\n```\n")
    with pytest.raises(MalformedChunkError, match=r":4:.*first defined.*:1"):
        parse(duplicate)

    unclosed = tmp_path / "unclosed.md"
    unclosed.write_text("~~~python <<x.py>>\nx\n")
    with pytest.raises(MalformedChunkError, match=r":1: unterminated"):
        parse(unclosed)

    literal = tmp_path / "literal.md"
    literal.write_text("````markdown\n```python <<fake.py>>\nbad\n```\n````\n")
    chunks, _ = parse(literal)
    assert chunks == {}
