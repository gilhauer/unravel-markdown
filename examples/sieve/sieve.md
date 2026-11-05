# The sieve of Eratosthenes: finding primes by elimination

The problem is to find every prime number up to a chosen integer limit. A prime
is an integer greater than 1 whose only positive divisors are 1 and itself.

One way to build the list is to test each number for primality by trying
possible divisors. This method is called **trial division**. It is correct,
but treating every candidate as a separate problem repeats many divisibility
checks across the list. As the limit grows, this repeated work becomes costly.

## Compare the cost

The chart compares trial division with the sieve of Eratosthenes, the approach
we will develop next. It measures the time to build the entire prime list;
both implementations return the same list at each limit, using the program developed in this example.

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

The relationship between primes and their multiples suggests a shortcut. Once
a prime is known, every larger multiple of it is composite: a product of two
integers greater than 1. For example, `3` is prime, but `3 * 3` gives `9`,
which has `3` as a divisor. We mark `9` as composite so it does not need a
separate primality test.

We can visit those multiples directly, in steps of the prime, and rule them
out together. This is the idea behind the sieve of Eratosthenes. Understanding
that relationship lets us generate and mark known composites instead of
searching independently for a factor of each candidate.

Start with the integers from 2 through the limit as candidates. Beginning with
2, cross out its larger multiples. Continue with the next larger candidate
that has not been crossed out and repeat.

One round of crossing out a single prime's larger multiples within the limit
is an **elimination pass**. For example, the pass for 2 crosses out 4, 6, 8,
and so on. Once every composite has been crossed out, the remaining candidates
are the primes we want. The questions to resolve are where each pass should
begin and how soon we can safely stop making passes.

This literate program develops that approach in Python. It assumes familiarity
with Python functions, lists, and loops. The explanation introduces code where
it helps the reasoning; `unravel` will assemble a module,
a demonstration, and executable checks in the order Python requires. This
follows the approach described in
[A brief introduction to literate programming](../../docs/explanation/literate-programming/literate-programming.md).

## Begin with the result

The function `sieve(n)` will return the primes up to and including the integer
bound `n`, in ascending order. Bounds below 2 produce an empty list. For
example, the primes through 30 are `2, 3, 5, 7, 11, 13, 17, 19, 23, 29`.

A caption such as *`<<chunk-name>>`* `=` means that the code below defines that
named chunk. Within the code, a reference such as `<<chunk-name>>` tells
`unravel` to insert the chunk's contents at that point. The definition can
appear later in the document.

If a helper chunk has several definitions, `unravel` joins their contents in
document order. Each reference to that name inserts the combined contents.
This lets us develop a chunk in stages while keeping its uses easy to read.

The first chunk defines `sieve(n)` and outlines its main steps through named
references. We can understand the function's overall structure before
examining the code that implements each step.

*`<<the sieve function>>`* `=`

```python <<the sieve function>>
def sieve(n: int) -> list[int]:
    """Return the primes through integer n, or an empty list when n < 2."""
    <<handle bounds below two>>
    <<prepare the candidate table>>
    <<eliminate the composites>>
    <<collect the surviving primes>>
```

The small example also gives us a concrete acceptance check. We will collect
checks alongside the decisions they exercise and assemble them into a test
class at the end.

*`<<sieve checks>>`* `=`

```python <<sieve checks>>
def test_primes_through_thirty(self):
    self.assertEqual(sieve(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

```

## Let composites identify themselves

Each elimination pass uses one prime to exclude its larger multiples. To turn
that approach into code, we need to record which candidates remain and decide
where to start crossing out multiples.

We will record this information in a table: `is_prime[k]` is `True` while `k`
remains a candidate and `False` once it has been excluded. Until the sieve is
finished, a `True` entry is a possibility, rather than a proof of primality.

For 2, elimination begins at 4. For 3, it can begin at 9: the earlier multiple
6 was already eliminated by 2. For 5, the multiples 10, 15, and 20 were already
eliminated by 2 or 3, so the first unfinished work is at 25.

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

## Discover when the work is finished

Suppose a composite number `number` has factors `left` and `right`, ordered so
that `left <= right`. If both factors exceeded the square root of `number`,
their product would exceed `number`. At least one factor, and therefore at
least one prime divisor, must be no greater than that square root.

Every composite through `n` therefore has a prime divisor no greater than the
square root of `n`. After processing primes through that boundary, every
composite has been eliminated. There is no need to use the larger survivors
as starting points for further passes.

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

Python's `isqrt(n)` gives the integer square root exactly, avoiding a
floating-point approximation. Its import can be introduced here, where the
reason for needing it becomes clear.

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

The `+ 1` is essential because `range` excludes its upper bound. At an exact
prime square such as 49, the pass for 7 must still run. These checks target that
boundary; they extend the earlier `sieve checks` chunk.

*`<<sieve checks>>`* `=` (continued)

```python <<sieve checks>>
def test_prime_squares_are_eliminated(self):
    for square in (4, 9, 25, 49, 121):
        with self.subTest(square=square):
            self.assertNotIn(square, sieve(square))

```

## Give each candidate a place

The elimination argument determines the table we need. For `n >= 2`, allocate
`n + 1` entries so that the integer `k` is represented directly by index `k`.
Exclude 0 and 1 immediately: neither is prime. Every other entry begins as a
candidate.

*`<<prepare the candidate table>>`* `=`

```python <<prepare the candidate table>>
is_prime = [True] * (n + 1)
is_prime[0] = is_prime[1] = False
```

This representation uses space proportional to `n`. It makes each mark and
lookup straightforward, at the cost of retaining a place for every integer up
to the bound.

For a bound below 2, there are no candidates. Returning immediately also keeps
negative bounds away from `isqrt` and ensures the table has room for indices
0 and 1 whenever initialization is reached. The function outline places this
guard before the table and the elimination loop, even though its definition
appears later in the explanation.

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

We can now justify both directions of the result. A prime has never been
crossed out because every elimination marks a product of factors greater than 1.
Every composite has been crossed out by a prime divisor within our stopping
boundary. The surviving entries are therefore exactly the primes.

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

The checks so far protect specific decisions. A broader comparison can use a
different method: for each candidate, try every potential divisor between 2
and the candidate itself, excluding the candidate. A nonzero remainder for
every divisor establishes primality. For 2, the divisor range is empty, and
`all` correctly returns `True`.

This deliberately simple reference calculation shares neither the sieve's
table nor its square-root stopping rule. Comparing complete lists checks for
missing primes, surviving composites, ordering, and duplicates. The modest
range keeps the slower reference calculation inexpensive; testing supports the
argument without replacing it.

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

All the algorithmic decisions are now in place. The output chunks arrange them
into three files. `sieve.py` puts the import before the function; `main.py`
imports that function and prints the primes through 100; `check_sieve.py`
places the accumulated checks inside a standard-library `unittest` class.

Each file shares a copyright, license, and generated-file notice, defined once
and reused below.

*`<<generated file notice>>`* `=`

```python <<generated file notice>>
# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
# Generated from sieve.md by unravel; edit the Markdown source and regenerate.
```

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

`unravel` follows the forward references in the function outline and expands
nested references, carrying indentation into the elimination loop. Repeated
definitions of `sieve checks` join in document order. The narrative can thus
introduce each check beside its reasoning while the generated file collects
them into one class.

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
