# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
# Generated from sieve.md by unravel; edit the Markdown source and regenerate.

import unittest

from sieve import sieve


class SieveChecks(unittest.TestCase):
    def test_primes_through_thirty(self):
        self.assertEqual(sieve(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

    def test_prime_squares_are_eliminated(self):
        for square in (4, 9, 25, 49, 121):
            with self.subTest(square=square):
                self.assertNotIn(square, sieve(square))

    def test_bounds_below_two_have_no_primes(self):
        for bound in (-100, -1, 0, 1):
            with self.subTest(bound=bound):
                self.assertEqual(sieve(bound), [])

    def test_a_prime_bound_is_included(self):
        for prime in (2, 3, 29, 97):
            with self.subTest(prime=prime):
                self.assertEqual(sieve(prime)[-1], prime)

    def test_results_match_trial_division(self):
        for bound in range(-5, 201):
            expected = [
                candidate
                for candidate in range(2, bound + 1)
                if all(candidate % divisor for divisor in range(2, candidate))
            ]
            with self.subTest(bound=bound):
                self.assertEqual(sieve(bound), expected)


if __name__ == "__main__":
    unittest.main()
