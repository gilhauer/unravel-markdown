# unravel documentation

`unravel` generates source files from named chunks in a Markdown document. You
can present those chunks alongside their explanations in the order that best
helps a reader understand the program. Chunk references assemble the generated
files in the order required by the compiler or interpreter, independently of
the order in which you explain the code.

## Start here

1. Read [A brief introduction to literate programming](explanation/literate-programming/literate-programming.md)
   for Knuth's idea of organizing code around human understanding.
2. Follow [Build your first project](tutorials/first-project/first-project.md).
   Install `unravel`, write a small Python example in Markdown, generate and run
   the program, then change the source and verify the result.

After the tutorial, explore [chunk syntax](../README.md#writing-an-unravel-document)
and [generated-file ownership](../README.md#generated-tree-ownership) before
applying the workflow to your own project.

## Find what you need

- [Tutorials](#tutorials): learn through guided exercises.
- [How-to guides](#how-to-guides): complete a specific task.
- [Reference](#reference): look up syntax, options, and rules.
- [Explanation](#explanation): understand the behavior and design.

## Tutorials

- [Build your first project](tutorials/first-project/first-project.md): a guided
  introduction for Python users working in Linux with Bash.

## How-to guides

- [Install the command](../README.md#installation).
- [Generate and check a project](../README.md#quick-start).
- [Develop and test](../README.md#development-and-testing).
- [Work with automated releases](../README.md#automated-releases).

## Reference

- [Command-line options and exit codes](../README.md#command-line-usage).
- [Markdown chunk syntax](../README.md#writing-an-unravel-document).
- [Path rules and filesystem restrictions](../README.md#path-and-filesystem-safety).

## Explanation

- [A brief introduction to literate programming](explanation/literate-programming/literate-programming.md):
  Knuth's approach and the distinction between explanation order and generated-file order.
- [The sieve of Eratosthenes](../examples/sieve/sieve.md): a complete literate
  program that develops the algorithm's reasoning before assembling its files.
- [Generated-file ownership and update behavior](../README.md#generated-tree-ownership).
- [Reproducible output](../README.md#reproducibility).

## License

This documentation and its examples and tutorial snippets use
`GPL-3.0-only`, the same license as the tool. See the
[project license information](../README.md#license) and [LICENSE](../LICENSE).
