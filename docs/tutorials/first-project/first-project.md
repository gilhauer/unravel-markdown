# Build your first project

In this tutorial, you will write a Markdown document that explains a small Python
program, generate the program with `unravel`, and run it. You will then change the
Markdown and verify that the generated program follows your change.

The program prints `Hello, Tel Aviv!`. Its source is assembled from two named
chunks in one file, `hello.md`.

You edit `hello.md`. `unravel` expands its named chunks into
`generated/application/main.py` and records that output in
`generated/.unravel-manifest.json`. You will run the Python file yourself in
step 5.

![`unravel` reads `hello.md` and writes a Python program and ownership manifest inside `generated/`.](png/input-output.png)

## Before you start

This tutorial is for readers comfortable with Python, a terminal, and editing
text files. The commands target Linux with Bash.

You need:

- Python 3.12 or newer, available as `python3`.
- Git and `uv`, available in your terminal. See the
  [installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
  if you need to install `uv`.
- A text editor that saves UTF-8 files.
- Internet access to fetch `unravel` and download its build tools during installation.

Check the command-line prerequisites:

```bash
python3 --version
git --version
uv --version
```

Confirm that Python reports version 3.12 or newer. If a command is missing,
install that prerequisite before continuing.

Run the following steps in order in the same Bash session. Start in a directory
where you can create a new directory named `unravel-tutorial`.

## 1. Install `unravel`

Create a workspace and install release `v0.1.0` directly from its Git tag using
your Python interpreter. `uv` fetches the repository for you:

```bash
mkdir unravel-tutorial
cd unravel-tutorial
uv tool install --python python3 \
  "git+https://github.com/gilhauer/unravel-markdown.git@v0.1.0"
export PATH="$(uv tool dir --bin):$PATH"
unravel --help
```

The help output should begin with:

```text
usage: unravel [-h] [-o DIR] [--list | --check] source
```

The distribution is called `unravel-markdown`; its command is `unravel`.
`uv` installs the tool in its own environment. The `export` command makes `uv`'s
tool executables available in this Bash session. For use in future sessions,
see the [tool path setup instructions](https://docs.astral.sh/uv/concepts/tools/#tool-executables).

## 2. Create your Markdown source

Create a directory for the example inside `unravel-tutorial`:

```bash
mkdir first-project
cd first-project
```

<!-- REVIEW 2: Give the example real explanatory prose instead of an instruction to the author. -->
In your text editor, create `hello.md` in this directory. Save the following
contents as UTF-8. The triple-backtick lines shown inside the example are part
of the file:

````markdown
# Hello

This program greets one city. The greeting is the whole point of the program,
so we write it first and decide where it goes afterwards.

```python <<greeting>>
message = "Hello, Tel Aviv!"
print(message)
```

The program wraps the greeting in a `main()` function and calls it when the
file runs as a script.

```python <<application/main.py>>
def main():
    <<greeting>>

if __name__ == "__main__":
    main()
```
````

<!-- REVIEW 1, 4: Say how a chunk is defined, and mark the period rule as current. -->
A code block becomes a chunk when its opening fence names it:
`` ```python <<greeting>> `` defines a chunk called `greeting`, a reusable
helper chunk. `application/main.py` names the file to generate, relative to the
output directory. `unravel` currently identifies file-producing chunks, called
**output roots**, by a period in their name, so keep helper names such as
`greeting` free of periods.

<!-- REVIEW 5, 6: Say that blank lines are inserted but left blank; drop the out-of-place sentence. -->
Think of `<<greeting>>` as an instruction to copy the lines from the `greeting`
chunk and paste them at that location in the generated file. Keep the reference
on its own line. `unravel` adds the reference's indentation to each line it
inserts, leaving blank lines blank. In this Python example, the four spaces
place the inserted statements inside `main()`.

## 3. Preview the chunks

From `first-project`, list the chunks in your document:

```bash
unravel hello.md --list
```

Expected output:

```text
  application/main.py [root]
  greeting
```

<!-- REVIEW 3: Use the term "output root" introduced above. -->
The `[root]` marker identifies the output root, the chunk that becomes a file.
`greeting` supplies code for that file. This command lists the chunks without
creating generated files.

## 4. Generate and inspect the program

Choose `generated` as the output directory:

```bash
unravel hello.md -o generated
```

Expected output:

```text
wrote generated/application/main.py
```

`unravel` creates the output directory and the nested `application` directory.
Your example now has this layout:

```text
first-project/
├── hello.md
└── generated/
    ├── .unravel-manifest.json
    └── application/
        └── main.py
```

<!-- REVIEW 7: Address the reader as "you" throughout. -->
The manifest records the generated file and its hash so later `unravel` runs can
check whether that file has been modified. Keep it with the generated output
for future regeneration and verification. The generated Python
program runs independently and does not need the manifest.

Inspect the assembled Python:

```bash
cat generated/application/main.py
```

Expected contents:

```python
def main():
    message = "Hello, Tel Aviv!"
    print(message)

if __name__ == "__main__":
    main()
```

The helper's statements now appear inside `main()` with the indentation from
the reference. The Markdown heading, prose, and fences remain in `hello.md`.

## 5. Run the generated program

```bash
python3 generated/application/main.py
```

Expected output:

```text
Hello, Tel Aviv!
```

You have generated and run a Python program from your Markdown document.

## 6. Check that the output is current

Ask `unravel` to compare the generated files and manifest with your source:

```bash
unravel hello.md -o generated --check
```

Expected output:

```text
current generated/application/main.py
```

<!-- REVIEW 8: State the exit status, to contrast with the failing check in step 7. -->
The command exits with status `0`. It checks the output without rewriting it.

## 7. Change the source and regenerate

Open `hello.md` and replace the greeting's `message` line with:

```python
message = "Hello, Haifa!"
```

Save `hello.md`. Keep making changes in this Markdown source; directly editing
the generated Python file would cause `unravel` to refuse to overwrite it on a
later run.

Check the output again before regenerating:

```bash
unravel hello.md -o generated --check
```

This time, expect the following diagnostic and exit status `1`:

```text
unravel: generated content differs: application/main.py
manifest content differs: .unravel-manifest.json
```

This is the expected result: the generated program and manifest still describe
the old greeting. The check has reported the difference without changing them.

Regenerate the program, run it, and check once more:

```bash
unravel hello.md -o generated
python3 generated/application/main.py
unravel hello.md -o generated --check
```

Expected output, in command order:

```text
wrote generated/application/main.py
Hello, Haifa!
current generated/application/main.py
```

Your Markdown change now appears in the running program, and the final check
confirms that the generated output is current.

## Continue learning

You have practiced the edit, generate, run, and check cycle. Keep `hello.md` as
the source you edit and let `unravel` maintain the generated program and manifest.

<!-- REVIEW 9, 10: Match the link text to its heading; point to the explanation and the sieve example. -->
For more about chunk syntax, see
[Writing an unravel document](../../../README.md#writing-an-unravel-document).
For behavior when generated files change or disappear, see
[Generated-tree ownership](../../../README.md#generated-tree-ownership).
For the ideas behind this approach, read
[A brief introduction to literate programming](../../explanation/literate-programming/literate-programming.md).
For a longer literate program, see the
[sieve of Eratosthenes example](../../../examples/sieve/sieve.md).
Return to the [documentation index](../../README.md) to find the other guides.
