# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
# Generated from sieve.md by unravel; edit the Markdown source and regenerate.

from sieve import sieve


if __name__ == "__main__":
    assert sieve(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for square in (4, 9, 25, 49, 121):
        assert square not in sieve(square)

    for bound in (-100, -1, 0, 1):
        assert sieve(bound) == []

    for p in (2, 3, 29, 97):
        assert sieve(p)[-1] == p
