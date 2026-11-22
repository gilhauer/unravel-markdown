# A brief introduction to literate programming

<!-- REVIEW 2: Call the single source a document, as the rest of the page does. -->
Literate programming is an approach to software development that gives priority
to the narrative through which a human reader understands a program. The
presentation follows the development of ideas and their rationale, while the
code is assembled separately in the order required by the compiler or
interpreter. Donald E. Knuth developed the approach and described its principles
in his 1984 paper,
[“Literate Programming” (free PDF)](https://www.cs.tufts.edu/~nr/cs257/archive/literate-programming/01-knuth-lp.pdf).
Prose and code form a single document that introduces the problem, develops a
solution, and explains the decisions that connect the two. Its structure gives
the reader a reason to encounter each idea: what problem it addresses, what
earlier ideas it depends on, and how it contributes to the whole.

<!-- REVIEW 1, 3: Say "chunks" and "generated files", the terms used throughout the documentation. -->
The reader should be able to follow both the implementation and the reasoning
behind it. This includes the assumptions under which an algorithm works, the
alternatives considered, and the constraints that shaped the design. Named code
chunks and references connect that explanation to generated files assembled by a
tool. The author chooses the order of exposition while remaining responsible
for producing a correct program.

## A program as an explanation

Knuth treats the programmer as an author addressing an audience. The author
chooses terminology, introduces unfamiliar ideas, and decides when the reader
has enough context to understand a detail. A literate program can begin with an
overall strategy, a motivating example, or a small component whose purpose is
already clear. Its organization should serve the explanation.

This view connects programming with craftsmanship. In his earlier essay,
[“Computer Programming as an Art” (1974, free PDF)](https://www.cs.bilkent.edu.tr/~canf/bilir_web/documents/knuth1974.pdf),
Knuth discusses creativity, judgment, style, and the satisfaction of constructing
well-designed programs. Literate programming gives that concern for the quality
of a program's presentation a concrete form: names, explanations, and the
sequence of ideas become deliberate parts of its design.

<!-- REVIEW 6: Fold the citation into the last sentence so it does not read as a fragment. -->
Writing the explanation is also an opportunity to examine the solution. An
author who must justify a data structure or state an algorithm's assumptions
may discover an omission or an unresolved decision. Knuth reported that writing
for an audience helped clarify his thinking and reduced his debugging effort.
He presented this as his experience, while acknowledging that the approach
might not suit everyone. It is a rationale for the method rather than a
guarantee of fewer defects or faster development
([Knuth, sections A and L](https://www.cs.tufts.edu/~nr/cs257/archive/literate-programming/01-knuth-lp.pdf)).

## Explanatory order and program structure

<!-- REVIEW 1, 3: Use "chunk" and "generated files", and give Knuth's term once. -->
Named code chunks connect the explanation to the generated files. Knuth calls
these named sections; this documentation calls them chunks. References specify
where each chunk is incorporated, independently of its position in the
document. A reference instructs the tool to insert a chunk's code at that
location when assembling the source. It does not itself call a
function during execution.

<!-- REVIEW 3: Say "generated files" rather than "generated source". -->
For example, an explanation of a reporting program might begin with the required
report, introduce the calculations that produce it, and then describe input
handling. The generated file may place imports and declarations first, followed
by helper definitions and the code that calls them. This distinction allows the
explanation to develop a sequence of ideas while the generated files satisfy
the language's structural requirements.

<!-- REVIEW 1: Say "chunk references". -->
Three orders are involved: the order in which a reader encounters ideas, the
order of code in the generated files, and the order in which instructions run.
The author controls the first through the document and the second through
chunk references; the resulting program determines the third.

<!-- REVIEW 6: Fold the citation into the last sentence. -->
There is no requirement to explain everything from the highest level downward.
Knuth explicitly allows movement between an overview and individual details as
the exposition requires. The final explanation can also be reorganized after
the solution has been discovered; it need not reproduce the author's sequence
of experiments and false starts
([Knuth, section J](https://www.cs.tufts.edu/~nr/cs257/archive/literate-programming/01-knuth-lp.pdf)).

## Explanation and implementation together

Comments in conventional source files can also explain intent, assumptions,
and design decisions. Literate programming adds a document structure that can
develop those ideas independently of the layout of the generated files. The
distinction concerns how the work is organized, rather than the number of
comments it contains.

<!-- REVIEW 2: Call it the literate source. -->
A single literate source also avoids maintaining a separate copy of the code solely for
documentation. It does not establish that the prose is accurate: an explanation
can still become outdated when an algorithm changes. Maintaining a literate
program includes reviewing its reasoning alongside its code.

## Tangling and weaving

<!-- REVIEW 4: Connect tangling to the assembly described earlier. -->
Knuth's original `WEB` system combined Pascal code with TeX documentation and
provided two processing paths from the same literate source. Tangling is the
assembly described above; weaving produces the document for reading:

| Process and tool | Output | Subsequent step |
| --- | --- | --- |
| Tangling: `TANGLE` | Pascal source assembled from the chunks | A Pascal compiler produces the executable program. |
| Weaving: `WEAVE` | A TeX document containing the explanation and formatted code | TeX typesets the document for reading. |

<!-- REVIEW 1, 2, 6: Say "chunks" in the table, "literate source" here, and fold in the citation. -->
Both outputs derive from the same literate source. Compilation and
typesetting remain separate steps
([Knuth, section B](https://www.cs.tufts.edu/~nr/cs257/archive/literate-programming/01-knuth-lp.pdf)).

<!-- REVIEW 7: Match Knuth's account of CWEB's history; fold in the citation. -->
The approach extends beyond Pascal. Silvio Levy adapted `WEB` to C in 1987, and
he and Knuth have since revised and extended the result, `CWEB`, together. Its
corresponding tools are `CTANGLE` and `CWEAVE`
([Knuth and Levy's account of `CWEB`](https://cs.stanford.edu/~knuth/cweb.html)).

## Value and practical limits

The practical value of an explanation depends on what a future reader needs to
understand. For a complex algorithm, that may be the reasoning behind a stopping
condition. For a scientific calculation, it may be the assumptions connecting a
model to its implementation. For long-lived software, it may be the reason a
seemingly simpler alternative was rejected. These are situations in which
preserving reasoning can be useful; they do not establish that every program
needs an extended narrative.

<!-- REVIEW 1, 2: Say "chunk boundaries" and "literate source". -->
There are corresponding maintenance costs. Refactoring can require changes to
the explanation, chunk boundaries, and references as well as the code.
Editors, build tools, and debugging workflows must accommodate the relationship
between the literate source and the generated files. The appropriate
amount of explanation therefore depends on the audience, the complexity of the
decisions, and the effort required to keep the document useful.

## Literate programming in `unravel`

<!-- REVIEW 3, 5: Name unravel instead of "It", and say "generated files". -->
`unravel` applies the separation of explanatory order and generated-file order
to Markdown documents. Authors combine prose with named code chunks and use
references such as `<<greeting>>` to specify their placement in generated files.
`unravel` provides the tangling part of the workflow. Markdown viewers and
documentation tools present the explanation; `unravel` assembles the generated
files for
subsequent execution, compilation, or other processing.

Using Markdown makes the approach available without adopting `WEB` or its
original languages. The writing task remains the same: develop an explanation
that helps a reader understand why the program takes its particular form, and
connect that explanation to the code that implements it.

<!-- REVIEW 8: Point to the sieve example, which links here and, like Knuth's example, finds primes. -->
The [first-project tutorial](../../tutorials/first-project/first-project.md)
illustrates this approach by presenting a greeting before the program structure
that incorporates it. The [sieve example](../../../examples/sieve/sieve.md)
applies it to a longer argument and, like Knuth's own example, finds prime
numbers.

## Further reading

- **[“Literate Programming” (1984, free PDF)](https://www.cs.tufts.edu/~nr/cs257/archive/literate-programming/01-knuth-lp.pdf):**
  the original argument and a complete `WEB` example that prints prime numbers.
  Start here to see how Knuth develops an explanation alongside a working
  program. The [publication record](https://doi.org/10.1093/comjnl/27.2.97)
  identifies the article in *The Computer Journal*.
- **[“Computer Programming as an Art” (1974, free PDF)](https://www.cs.bilkent.edu.tr/~canf/bilir_web/documents/knuth1974.pdf):**
  Knuth's earlier account of programming as a creative activity involving
  technical knowledge, taste, and judgment.
- **[*Literate Programming* (1992), Knuth's book overview](https://cs.stanford.edu/~knuth/lp.html):**
  a collection of essays and examples, including “How to Read a `WEB`,” excerpts
  from the TeX and METAFONT programs, and discussions of mathematical writing.
  “The Errors of TeX” and “The Error Log of TeX” extend the collection to the
  analysis and history of defects in a substantial program. The linked page
  provides the contents and publication details, rather than the full book.

Related guides are listed in the [documentation index](../../README.md).
