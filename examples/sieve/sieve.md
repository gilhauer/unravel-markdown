# The sieve of Eratosthenes: finding primes by elimination

Suppose we want every prime number up to a chosen integer limit. A prime is an
integer greater than 1 whose only positive divisors are 1 and itself. Through
100, the list ends with 97. How much work can we save when finding the whole
list?

One reliable approach is **trial division**: take each candidate in turn and
try possible divisors. Finding a divisor settles the matter; otherwise, we
must check enough possibilities to establish that the candidate is prime.
The next candidate starts a fresh investigation, often involving the same
divisors. As the limit grows, this repeated work becomes costly.

## Compare the cost

The chart gives that cost a scale. It compares the sieve implementation we
will develop here with a separate trial-division implementation. Each builds
the same complete list of primes at each limit. Follow the two lines as the
limit increases: both times grow, but they pull farther apart.

![Median elapsed time at eight equally spaced limits from 50,000 to 400,000. Trial division, shown as a solid line, rises from 26.3 ms to 576.5 ms; the sieve, shown as a dashed line, rises from 6.1 ms to 56.2 ms.](png/runtime-comparison.png)

At a limit of 50,000, trial division took about 26 ms and the sieve about 6 ms.
At 400,000, those times were about 577 ms and 56 ms: the sieve took roughly
one tenth as long. Both methods needed more time for the larger problem, but
the cost of testing candidates independently grew much faster in this run.

Each point is the median of seven measurements using CPython 3.12.3 on Linux
with an AMD Ryzen 7 7735HS processor. The trial-division implementation skips
even candidates, tries only odd divisors up to and including the candidate's
integer square root, and stops at the first factor. These are local measurements
of these two implementations; individual timings vary with machine and system
load.

## Find the shortcut

Knowing a prime tells us something about many other numbers at once. Although
`3` is prime, `3 * 3` gives `9`, which cannot be prime: we have just constructed
it from two factors greater than 1. Such a number is **composite**. We can mark
`9` as composite now and save a separate primality test later.

The same observation applies to every larger multiple of 3. We can reach them
directly by counting in threes. This is the shortcut behind the sieve of
Eratosthenes: generate numbers with known factors and cross them off a list
of candidates.

Try the idea on the integers from 2 through 30. Keep 2 and cross out 4, 6, 8,
and the remaining even numbers. This round of marking a prime's larger
multiples is an **elimination pass**. The next surviving candidate is 3;
its pass crosses out 6, 9, 12, and so on. Some of those numbers were already
crossed out, but 9, 15, 21, and 27 are newly excluded.

There is no need for a pass using 4. Every multiple of 4 was already reached
by the pass for 2. We continue with the next surviving candidate, 5.

The method leaves us with two useful questions. Can a pass skip multiples
already dealt with by smaller primes? And when have we made enough passes
to know that every survivor is prime?

This literate program develops that approach in Python. It assumes familiarity
with Python functions, lists, and loops. The code appears in the order that
develops the argument; `unravel` assembles a module, a demonstration, and
executable checks in the order Python requires. This follows the approach in
[A brief introduction to literate programming](../../docs/explanation/literate-programming/literate-programming.md).

## Begin with the result

The function `sieve(n)` will return the primes up to and including the integer
bound `n`, in ascending order. Bounds below 2 produce an empty list. For
example, the primes through 30 are `2, 3, 5, 7, 11, 13, 17, 19, 23, 29`.

The function needs four steps: handle an empty range, prepare the candidates,
cross out the composites, and collect the survivors. We can give those steps
names before working out their details.

Each named code block is an `unravel` **chunk**; its caption repeats the name
in the opening Markdown fence. A line such as `<<prepare the candidate table>>`
tells `unravel` to insert that chunk's contents here, like copying and pasting
its code. The definition can appear later in the document.

*`<<the sieve function>>`* `=`

```python <<the sieve function>>
def sieve(n: int) -> list[int]:
    """Return the primes through integer n, or an empty list when n < 2."""
    <<handle bounds below two>>
    <<prepare the candidate table>>
    <<eliminate the composites>>
    <<collect the surviving primes>>
```

The list through 30 gives us a first check on the result. We will place checks
beside the decisions they test, then collect them into a test class at the end.

*`<<sieve checks>>`* `=`

```python <<sieve checks>>
def test_primes_through_thirty(self):
    self.assertEqual(sieve(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

```

## Let composites identify themselves

Consider the pass for 5. We could start at 10 and visit 15, 20, 25, and so on.
But 10 and 20 are even, and 15 was reached by the pass for 3. The first number
this pass must eliminate is 25.

We will record this information in a table: `is_prime[k]` is `True` while `k`
remains a candidate and `False` once it has been excluded. Until the sieve is
finished, a `True` entry is a possibility, rather than a proof of primality.

The starting points now form a pattern: 4 for the pass using 2, 9 for the pass
using 3, and 25 for the pass using 5. Each is the square of the prime. To use
this rule for every pass, we need to explain why it holds.

The same reasoning applies to any prime `prime`. A smaller composite multiple
has the form `prime * factor` with `2 <= factor < prime`. That factor is either
prime itself or has a smaller prime divisor, whose earlier pass has already
eliminated the multiple. Consequently, this pass can start at `prime * prime`.

*`<<cross out multiples of this prime>>`* `=`

```python <<cross out multiples of this prime>>
for multiple in range(prime * prime, n + 1, prime):
    is_prime[multiple] = False
```

The step size `prime` visits its successive multiples. The exclusive stop
`n + 1` includes `n` itself when it is a multiple.

Some later multiples still receive more than one mark: 30, for example, is
reached by 2, 3, and 5. Setting an entry to `False` again is harmless. Starting
at the square removes the redundant beginning of each pass.

## Discover when the work is finished

For a limit of 100, the pass for 7 starts at 49. The next surviving candidate
is 11, whose square is 121: already beyond the end of the table. Could a
composite below 100 still be waiting for its first mark?

Any composite at most 100 has two factors greater than 1. They cannot both
exceed 10, because their product would then exceed 100. At least one factor
is at most 10; if that factor is composite, it in turn has a prime divisor
no larger than itself. A prime at most 10 must therefore have reached the
number already.

The same argument works for any bound `n >= 2`. If both factors exceeded the
square root of `n`, their product would exceed `n`. Every composite through
`n` must therefore have a prime divisor no greater than that square root.
Once we have processed those primes, every composite has been eliminated.

For the limit 100, the square-root boundary is 10:

| Prime used for a pass | First multiple that needs this pass |
| --- | --- |
| 2 | 4 |
| 3 | 9 |
| 5 | 25 |
| 7 | 49 |

Finding every prime through 100 therefore requires elimination passes for only
four numbers: 2, 3, 5, and 7. The other candidates through 10 have already been
eliminated. After those four passes, every remaining number greater than 1 is
prime. Larger survivors such as 11 and 97 can be collected without performing
their own passes.

Python's `isqrt(n)` gives the greatest integer no larger than the square root
of `n`, using exact integer arithmetic. It supplies the boundary for our loop.

*`<<sieve imports>>`* `=`

```python <<sieve imports>>
from math import isqrt
```

We examine candidates in increasing order. If a candidate is still marked,
none of the smaller primes divides it, so it is prime and can eliminate its
multiples. A candidate already crossed out contributes no new work.

*`<<eliminate the composites>>`* `=`

```python <<eliminate the composites>>
for prime in range(2, isqrt(n) + 1):
    if is_prime[prime]:
        <<cross out multiples of this prime>>
```

Here `unravel` expands the nested reference at its indentation, placing the
marking loop inside the `if` block.

The `+ 1` matters at the boundary. With a limit of 49, stopping before 7
would leave 49 unmarked. Since `range` excludes its upper bound, we add 1
to ensure that the pass for 7 runs. The next check protects that decision.

Using the name `sieve checks` again adds to the earlier chunk. `unravel`
combines these definitions in document order wherever that chunk is referenced.

*`<<sieve checks>>`* `=` (continued)

```python <<sieve checks>>
def test_prime_squares_are_eliminated(self):
    for square in (4, 9, 25, 49, 121):
        with self.subTest(square=square):
            self.assertNotIn(square, sieve(square))

```

## Give each candidate a place

We now know how to cross out composites and when to stop. The table itself
can stay simple: let each integer serve as its own address. For `n >= 2`,
`n + 1` entries give us indices from 0 through `n`. Mark 0 and 1 as excluded
immediately, since neither is prime; every other entry starts as a candidate.

*`<<prepare the candidate table>>`* `=`

```python <<prepare the candidate table>>
is_prime = [True] * (n + 1)
is_prime[0] = is_prime[1] = False
```

This representation uses space proportional to `n`. It makes each mark and
lookup straightforward, at the cost of retaining a place for every integer up
to the bound.

One small case needs attention before we create the table. A bound below 2
has no primes, so we can return an empty list immediately. This also keeps
negative values away from `isqrt` and ensures that indices 0 and 1 exist when
we initialize the table. The function outline already puts this guard first,
although its definition appears here.

*`<<handle bounds below two>>`* `=`

```python <<handle bounds below two>>
if n < 2:
    return []
```

*`<<sieve checks>>`* `=` (continued)

```python <<sieve checks>>
def test_bounds_below_two_have_no_primes(self):
    for bound in (-100, -1, 0, 1):
        with self.subTest(bound=bound):
            self.assertEqual(sieve(bound), [])

```

## Read what remains

What remains in the table? No prime has been crossed out: every mark was
made at a product of factors greater than 1. No composite has escaped: each
has a prime divisor within the boundary we processed. Those two facts settle
the original question. The surviving entries are exactly the primes.

Scanning their indices in increasing order produces the promised sorted list.
Again, the stop `n + 1` makes the bound inclusive.

*`<<collect the surviving primes>>`* `=`

```python <<collect the surviving primes>>
return [number for number in range(2, n + 1) if is_prime[number]]
```

In particular, a prime bound must survive as the last element of the result.
The smallest cases, 2 and 3, also exercise a sieve with no elimination passes.

*`<<sieve checks>>`* `=` (continued)

```python <<sieve checks>>
def test_a_prime_bound_is_included(self):
    for prime in (2, 3, 29, 97):
        with self.subTest(prime=prime):
            self.assertEqual(sieve(prime)[-1], prime)

```

## Check the argument from another direction

Trial division now has another use. For small limits, its straightforward
approach gives us an independent way to check the sieve. Here we use a simpler
version than the one in the timing chart: try every divisor from 2 up to, but
not including, the candidate. If every remainder is nonzero, the candidate is
prime. For 2, there are no divisors to try, and `all` returns `True`.

This calculation shares neither the sieve's table nor its square-root stopping
rule. A mistake in those decisions is therefore less likely to be repeated
in the check. Comparing complete lists can reveal missing primes, surviving
composites, incorrect ordering, or duplicates. The small limits keep the
comparison inexpensive. These tests check our implementation; the argument
above explains why the method works for every allowed bound.

*`<<sieve checks>>`* `=` (continued)

```python <<sieve checks>>
def test_results_match_trial_division(self):
    for bound in range(-5, 201):
        expected = [
            candidate
            for candidate in range(2, bound + 1)
            if all(candidate % divisor for divisor in range(2, candidate))
        ]
        with self.subTest(bound=bound):
            self.assertEqual(sieve(bound), expected)

```

## Assemble the program after explaining it

We have developed the function in the order of its decisions: how to eliminate
composites, when to stop, and what to keep. Three final chunks arrange the code
for Python. `sieve.py` puts the import before the function; `main.py` calls
the function with a limit of 100; `check_sieve.py` collects the checks into a
standard-library `unittest` class.

Each file shares a copyright, license, and generated-file notice, defined once
and reused below.

*`<<generated file notice>>`* `=`

```python <<generated file notice>>
# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
# Generated from sieve.md by unravel; edit the Markdown source and regenerate.
```

The chunk named `sieve.py` defines an output file. Its references insert the
notice, import, and function in the order shown.

*`<<sieve.py>>`* `=`

```python <<sieve.py>>
<<generated file notice>>

<<sieve imports>>


<<the sieve function>>
```

*`<<main.py>>`* `=`

```python <<main.py>>
<<generated file notice>>

from sieve import sieve


if __name__ == "__main__":
    print(sieve(100))
```

*`<<check_sieve.py>>`* `=`

```python <<check_sieve.py>>
<<generated file notice>>

import unittest

from sieve import sieve


class SieveChecks(unittest.TestCase):
    <<sieve checks>>

if __name__ == "__main__":
    unittest.main()
```

## Generate, run, and verify

From the repository root, use the checked-out version of `unravel` through `uv`:

```bash
uv run unravel examples/sieve/sieve.md -o examples/sieve/generated
uv run python examples/sieve/generated/main.py
uv run python examples/sieve/generated/check_sieve.py
uv run unravel examples/sieve/sieve.md -o examples/sieve/generated --check
```

The demonstration prints:

```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
```

The generated checks exercise the program's behavior. The final `--check`
command serves a separate purpose: it verifies that the generated files and
their ownership manifest still match this document.

```text
examples/sieve/
├── sieve.md
└── generated/
    ├── .unravel-manifest.json
    ├── check_sieve.py
    ├── main.py
    └── sieve.py
```

Edit `sieve.md` and regenerate to change the example. Keep the manifest with
the generated files when using `unravel` to update or check them; Python can
run the generated program independently of the document and manifest.
