# unravel

`unravel` is a small literate-programming command-line tool for generating a
multi-file project from named chunks in one Markdown document. It supports
forward references, recursive expansion, indentation propagation, and continued
helper chunks while protecting existing files with a deterministic ownership
manifest.

Use it when prose should teach concepts in a natural order but generated source
files must follow the directory structure required by their own tools.

> **Project status:** early development. The `unravel-markdown` distribution
> requires Python 3.12 or newer and has not yet published its first release.

## Features

- Generate nested project trees from one Markdown source.
- Compose roots from reusable chunks in any source order.
- Produce byte-reproducible UTF-8/LF output and a SHA-256 manifest.
- Preview chunk classification with `--list`.
- Verify a generated tree without changing it with `--check`.
- Reject traversal, nonportable names, collisions, filesystem links, stale
  output, and unowned-file overwrites.
- Run without runtime dependencies beyond Python.

## Installation

Clone the repository and install the command with
[uv](https://docs.astral.sh/uv/):

```sh
git clone https://github.com/gilhauer/unravel-markdown.git
cd unravel-markdown
uv tool install .
unravel --help
```

For development, `uv run unravel` uses the checked-out source directly and does
not require a tool installation.

The distribution is named `unravel-markdown`; the installed command and Python
import package are both named `unravel`.

## Quick start

Create `hello.md`:

````markdown
# Hello

Explain the greeting before assembling the program.

```python <<greeting>>
message = "Hello, Reykjavík!"
print(message)
```

```python <<application/main.py>>
def main():
    <<greeting>>

if __name__ == "__main__":
    main()
```
````

Generate the project and verify it:

```sh
unravel hello.md -o generated
unravel hello.md -o generated --check
python generated/application/main.py
```

The generated tree contains:

```text
generated/
├── .unravel-manifest.json
└── application/
    └── main.py
```

Generation reports files in sorted path order. Check mode exits successfully
only when every expected file and the manifest are current.

## Command-line usage

```text
usage: unravel [-h] [-o DIR] [--list | --check] source
```

| Option | Meaning |
| --- | --- |
| `source` | UTF-8 Markdown document containing named chunks. |
| `-o DIR`, `--output-dir DIR` | Output tree; defaults to the source directory. |
| `--list` | List chunks and identify output roots without writing. |
| `--check` | Verify generated files and the manifest without writing. |

`--list` and `--check` are mutually exclusive. The installed `unravel` command
and `python -m unravel` expose the same behavior.

Exit status `0` means generation or checking succeeded. Status `1` reports an
invalid source, unsafe path, ownership conflict, stale/missing/changed output,
manifest problem, or expected I/O/encoding error. Invalid command-line syntax
uses status `2`.

## Writing an unravel document

An executable chunk is a backtick or tilde fenced block whose opening line ends
in `<<name>>`:

````markdown
```python <<application/main.py>>
def main():
    <<function body>>
```

```python <<function body>>
print("hello")
```
````

References must occupy a whole line. The indentation before a reference is
applied recursively to its expanded lines; blank lines remain blank. Forward
references and repeated helper definitions are supported and retain source
order.

A chunk is currently considered an output root when its name contains a period.
This legacy convention means helper names cannot contain periods and does not
reliably represent extensionless output files. Repeating an output-root
definition is an error; assemble a root from repeatable helper chunks instead.
This is a deliberate compatibility change from version 0.1.0, which silently
concatenated repeated roots.

A named-looking fence inside an ordinary backtick or tilde fence is treated as
literal Markdown. Closing fences must use the opening character and at least its
length. Unterminated executable chunks are errors. This is the supported fenced
block subset, not a complete CommonMark implementation.

## Generated-tree ownership

Before writing, `unravel` parses and expands every root, validates all paths and
destinations, and computes every expected byte. Predictable validation failures
therefore do not leave partial output.

Each output tree contains `.unravel-manifest.json`:

```json
{
  "version": 1,
  "files": {
    "application/main.py": "<sha256-of-generated-bytes>"
  }
}
```

The manifest contains sorted relative paths and SHA-256 hashes without
timestamps or machine-specific paths. On first generation, `unravel` creates new
destinations but does not adopt existing files. Later runs update only
manifest-owned files whose bytes still match their recorded hashes. Missing
owned files can be regenerated; modified owned files and unrelated files are
left untouched.

If a manifest-owned path is no longer generated, it is reported as stale and
generation stops without deleting anything. Inspect the tree and manifest,
preserve anything important, and generate into a new empty directory. This
version intentionally provides no automatic pruning or broad `--force` option.

Files are atomically replaced individually and the manifest is published last.
This is not a transactional whole-tree update: an operating-system failure can
still interrupt a multi-file write. After such a failure, inspect the tree and
regenerate into a new empty directory if ownership hashes no longer match.

## Path and filesystem safety

Root names are portable, relative, forward-slash-separated paths. `unravel`
rejects:

- POSIX absolute paths, Windows drives, UNC paths, and backslashes;
- empty, `.` or `..` components, control characters, colons/alternate streams;
- Windows-reserved names and components ending in a dot or space;
- case-insensitive component collisions and file/directory collisions;
- its manifest and `.unravel-tmp-` temporary namespace;
- symlinks or Windows directory junctions in the output path or tree;
- multiply linked owned files, the input document, and unowned destinations.

Python 3.12's `Path.is_junction()` is used on Windows. Other exotic Windows
reparse-point types have not been tested and are not claimed as supported.
Linux symlink and hard-link behavior is covered by the test suite; the project
has not yet been tested on Windows or macOS.

The safety model protects against predictable document mistakes and
pre-existing filesystem aliases. It is not a sandbox for hostile documents
racing filesystem changes. Concurrent writers and adversarial path swapping
are outside scope.

## Reproducibility

Markdown is read as UTF-8. Generated files are UTF-8 without a byte-order mark
and use LF newlines on every platform. Every output ends in one added LF after
its logical source lines: an empty root contains `"\n"`, while intentional
trailing blank lines remain intact.

Chunks and continued definitions are never reordered. Equivalent inputs produce
the same relative files, bytes, hashes, and manifest in different output
directories, processes, and Python hash seeds.

## Development and testing

Install the locked development environment and run the package suite:

```sh
uv sync --locked
uv run pytest
```

Build the wheel and source distribution:

```sh
uv build
```

Exercise the included offline Open Observatory fixture:

```sh
uv run unravel tests/fixtures/open_observatory.md -o /tmp/unravel-observatory
uv run unravel tests/fixtures/open_observatory.md -o /tmp/unravel-observatory --check
uv run pytest /tmp/unravel-observatory/tests/test_observation.py
```

Terraform and Ansible checks are optional and are not package dependencies. No
test provisions infrastructure or claims that generated files prove a working
VM lab.

## Support and contributing

Report bugs and propose improvements through
[GitHub Issues](https://github.com/gilhauer/unravel-markdown/issues). Changes to
protected branches should be submitted through a pull request and include tests
for behavior changes.

This repository does not currently include a license file. Do not assume rights
beyond those provided by applicable law until the maintainer adds one.
