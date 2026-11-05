# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
# Generated from sieve.md by unravel; edit the Markdown source and regenerate.

from math import isqrt


def sieve(n: int) -> list[int]:
    """Return the primes through integer n, or an empty list when n < 2."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for prime in range(2, isqrt(n) + 1):
        if is_prime[prime]:
            for multiple in range(prime * prime, n + 1, prime):
                is_prime[multiple] = False
    return [number for number in range(2, n + 1) if is_prime[number]]
