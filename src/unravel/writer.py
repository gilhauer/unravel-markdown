"""Plan, validate, and materialize deterministic generated trees."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from .exceptions import CheckError, ManifestError, OwnershipError, UnsafePathError
from .expander import expand_chunk
from .parser import Chunk, is_root

MANIFEST_NAME = ".unravel-manifest.json"
TEMP_PREFIX = ".unravel-tmp-"
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
    "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4",
    "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


@dataclass(frozen=True)
class GenerationPlan:
    output_dir: Path
    files: dict[str, bytes]
    manifest_bytes: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_output_path(name: str) -> tuple[str, ...]:
    """Validate a portable relative output path without normalizing aliases."""
    if not name or "\\" in name:
        raise UnsafePathError(f'unsafe output path "{name}": empty or contains a backslash')
    win = PureWindowsPath(name)
    if name.startswith("/") or win.drive or win.root:
        raise UnsafePathError(f'unsafe output path "{name}": absolute or drive-qualified')
    parts = tuple(name.split("/"))
    for part in parts:
        if part in {"", ".", ".."}:
            raise UnsafePathError(f'unsafe output path "{name}": invalid path component')
        if any(ord(char) < 32 or ord(char) == 127 for char in part):
            raise UnsafePathError(f'unsafe output path "{name}": control character')
        if ":" in part:
            raise UnsafePathError(f'unsafe output path "{name}": colon/alternate stream')
        if part.endswith((".", " ")):
            raise UnsafePathError(f'unsafe output path "{name}": trailing dot or space')
        if part.split(".", 1)[0].rstrip(" .").upper() in WINDOWS_RESERVED:
            raise UnsafePathError(f'unsafe output path "{name}": Windows-reserved name')
        if part == MANIFEST_NAME or part.startswith(TEMP_PREFIX):
            raise UnsafePathError(f'unsafe output path "{name}": reserved by unravel')
    return parts


def _validate_collisions(names: list[str]) -> None:
    seen_paths: dict[str, str] = {}
    seen_components: dict[tuple[str, ...], tuple[str, ...]] = {}
    file_keys: dict[tuple[str, ...], str] = {}
    for name in sorted(names):
        parts = validate_output_path(name)
        folded = tuple(part.casefold() for part in parts)
        full_key = "/".join(folded)
        if full_key in seen_paths:
            raise UnsafePathError(
                f'output collision between "{seen_paths[full_key]}" and "{name}"'
            )
        seen_paths[full_key] = name
        for index in range(1, len(parts) + 1):
            prefix_key = folded[:index]
            prefix = parts[:index]
            previous = seen_components.get(prefix_key)
            if previous is not None and previous != prefix:
                raise UnsafePathError(
                    f'case-insensitive path collision between '
                    f'"{"/".join(previous)}" and "{"/".join(prefix)}"'
                )
            seen_components[prefix_key] = prefix
            if index < len(parts) and prefix_key in file_keys:
                raise UnsafePathError(
                    f'output "{file_keys[prefix_key]}" is also a parent of "{name}"'
                )
        file_keys[folded] = name
    for folded, name in file_keys.items():
        for other_folded, other_name in file_keys.items():
            if len(other_folded) > len(folded) and other_folded[: len(folded)] == folded:
                raise UnsafePathError(f'output "{name}" is also a parent of "{other_name}"')


def _manifest_bytes(files: dict[str, bytes]) -> bytes:
    payload = {
        "version": 1,
        "files": {name: _sha256(files[name]) for name in sorted(files)},
    }
    return (json.dumps(payload, indent=2) + "\n").encode("utf-8")


def _lexists(path: Path) -> bool:
    return os.path.lexists(path)


def _is_link_like(path: Path) -> bool:
    """Recognize symlinks and Windows directory junctions without following."""
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def _reject_symlinked_output_path(output_dir: Path) -> None:
    absolute = Path(os.path.abspath(output_dir))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if _is_link_like(current):
            raise OwnershipError(f"output path contains a symlink or junction: {current}")
        if not _lexists(current):
            break
        try:
            current.lstat()
        except OSError as exc:
            raise OwnershipError(f"cannot inspect output path {current}: {exc}") from exc


def _reject_tree_links(output_dir: Path) -> None:
    if not _lexists(output_dir):
        return
    if _is_link_like(output_dir) or not output_dir.is_dir():
        raise OwnershipError(f"output directory is not a real directory: {output_dir}")
    for root, dirs, files in os.walk(output_dir, followlinks=False):
        root_path = Path(root)
        for entry in dirs + files:
            path = root_path / entry
            if _is_link_like(path):
                raise OwnershipError(f"symlink or junction found inside output tree: {path}")


def _load_manifest(output_dir: Path) -> tuple[dict[str, str] | None, bytes | None]:
    path = output_dir / MANIFEST_NAME
    if not _lexists(path):
        return None, None
    if _is_link_like(path) or not path.is_file() or path.stat().st_nlink != 1:
        raise ManifestError(f"manifest is not a private regular file: {path}")
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"invalid manifest {path}: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"version", "files"}:
        raise ManifestError(f"invalid manifest schema: {path}")
    if type(data["version"]) is not int or data["version"] != 1 or not isinstance(data["files"], dict):
        raise ManifestError(f"unsupported or invalid manifest: {path}")
    files: dict[str, str] = {}
    for name, digest in data["files"].items():
        if not isinstance(name, str) or not isinstance(digest, str):
            raise ManifestError(f"invalid manifest entry in {path}")
        try:
            validate_output_path(name)
        except UnsafePathError as exc:
            raise ManifestError(f"unsafe manifest entry: {exc}") from exc
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ManifestError(f'invalid SHA-256 for "{name}" in {path}')
        files[name] = digest
    try:
        _validate_collisions(list(files))
    except UnsafePathError as exc:
        raise ManifestError(f"invalid manifest paths: {exc}") from exc
    return files, raw


def _inspect_ownership(
    output_dir: Path,
    files: dict[str, bytes],
    source_path: Path | None,
    checking: bool,
) -> tuple[bytes | None, list[str]]:
    _reject_symlinked_output_path(output_dir)
    _reject_tree_links(output_dir)
    owned, old_manifest = _load_manifest(output_dir)
    problems: list[str] = []
    if owned is None:
        if checking:
            problems.append(f"missing manifest: {output_dir / MANIFEST_NAME}")
        for name in files:
            destination = output_dir.joinpath(*name.split("/"))
            if _lexists(destination):
                problems.append(f"unowned destination exists: {name}")
    else:
        stale = sorted(set(owned) - set(files))
        problems.extend(f"stale owned output: {name}" for name in stale)
        for name, expected_hash in owned.items():
            destination = output_dir.joinpath(*name.split("/"))
            if not _lexists(destination):
                if checking and name in files:
                    problems.append(f"missing output: {name}")
                continue
            if _is_link_like(destination) or not destination.is_file():
                problems.append(f"owned output is not a regular file: {name}")
                continue
            if destination.stat().st_nlink != 1:
                problems.append(f"owned output has multiple hard links: {name}")
                continue
            actual = _sha256(destination.read_bytes())
            if actual != expected_hash:
                problems.append(f"locally modified owned output: {name}")
        for name in set(files) - set(owned):
            destination = output_dir.joinpath(*name.split("/"))
            if _lexists(destination):
                problems.append(f"unowned destination exists: {name}")

    for name in files:
        destination = output_dir.joinpath(*name.split("/"))
        for parent in destination.parents:
            if parent == output_dir.parent:
                break
            if _lexists(parent) and not parent.is_dir():
                problems.append(f"output parent is not a directory: {parent}")

    if source_path is not None:
        source_abs = Path(os.path.abspath(source_path))
        for name in files:
            destination = Path(os.path.abspath(output_dir.joinpath(*name.split("/"))))
            if destination == source_abs:
                problems.append(f"output would overwrite input Markdown: {name}")
            elif _lexists(destination):
                try:
                    if os.path.samefile(source_abs, destination):
                        problems.append(f"output aliases input Markdown: {name}")
                except OSError:
                    pass
    return old_manifest, problems


def plan_generation(
    chunks: dict[str, Chunk],
    source_file: str,
    output_dir: Path,
    source_path: Path | None = None,
    *,
    checking: bool = False,
) -> GenerationPlan:
    names = sorted(name for name in chunks if is_root(name))
    _validate_collisions(names)
    files: dict[str, bytes] = {}
    for name in names:
        text = "\n".join(expand_chunk(name, chunks, source_file)) + "\n"
        files[name] = text.encode("utf-8")
    manifest = _manifest_bytes(files)
    old_manifest, problems = _inspect_ownership(output_dir, files, source_path, checking)
    if checking and old_manifest is not None and old_manifest != manifest:
        problems.append(f"manifest content differs: {MANIFEST_NAME}")
    if checking:
        for name, expected in files.items():
            destination = output_dir.joinpath(*name.split("/"))
            if _lexists(destination) and destination.is_file() and not _is_link_like(destination):
                if destination.read_bytes() != expected:
                    problems.append(f"generated content differs: {name}")
    if problems:
        error = CheckError if checking else OwnershipError
        raise error("\n".join(sorted(set(problems))))
    return GenerationPlan(output_dir=output_dir, files=files, manifest_bytes=manifest)


def _atomic_write(path: Path, data: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=TEMP_PREFIX, dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def apply_plan(plan: GenerationPlan) -> list[str]:
    plan.output_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(plan.files):
        destination = plan.output_dir.joinpath(*name.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(destination, plan.files[name])
    _atomic_write(plan.output_dir / MANIFEST_NAME, plan.manifest_bytes)
    return sorted(plan.files)


def write_roots(
    chunks: dict[str, Chunk],
    source_file: str,
    output_dir: Path,
    source_path: Path | None = None,
) -> list[str]:
    """Validate the full tree, then write roots in portable path order."""
    return apply_plan(plan_generation(chunks, source_file, output_dir, source_path))


def check_roots(
    chunks: dict[str, Chunk],
    source_file: str,
    output_dir: Path,
    source_path: Path | None = None,
) -> list[str]:
    """Validate that a generated tree is current without changing it."""
    plan = plan_generation(chunks, source_file, output_dir, source_path, checking=True)
    return sorted(plan.files)
