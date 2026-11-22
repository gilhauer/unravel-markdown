# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.
"""Time the generated sieve against trial division for the runtime chart.

Run from the repository root after generating the example:

    uv run unravel examples/sieve/sieve.md -o examples/sieve/generated
    uv run python examples/sieve/benchmark.py

The script prints the median of seven runs at each limit, followed by the two
``line`` rows used in ``diagrams/runtime-comparison.mmd``.
"""

import platform
import statistics
import sys
import time
from math import isqrt
from pathlib import Path

sys.dont_write_bytecode = True  # Keep generated/ limited to unravel's output.
sys.path.insert(0,str(Path(__file__).resolve().parent / "generated"))
from sieve import sieve  # noqa: E402

LIMITS = range(50_000, 400_001, 50_000)
RUNS = 7


def passes_trial_division(candidate: int) -> bool:
    """Return whether no divisor from 2 through isqrt(candidate) divides it."""
    for divisor in range(2, isqrt(candidate) + 1):
        if candidate % divisor == 0:
            return False
    return True


def trial_division(n: int) -> list[int]:
    """Return the primes through n, testing each candidate independently."""
    return [k for k in range(2, n + 1) if passes_trial_division(k)]


def median_ms(function, n: int) -> float:
    """Return the median elapsed time of RUNS calls, in milliseconds."""
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        function(n)
        times.append((time.perf_counter() - start) * 1000)
    return round(statistics.median(times), 3)


def main() -> None:
    for n in (30, 1_000, 10_000):
        assert sieve(n) == trial_division(n), n

    print(f"Python {platform.python_version()} on {platform.machine()}, "
          f"median of {RUNS} runs")
    print(f"{'limit':>8}  {'trial (ms)':>11}  {'sieve (ms)':>11}")
    trial, fast = [], []
    for n in LIMITS:
        trial.append(median_ms(trial_division, n))
        fast.append(median_ms(sieve, n))
        print(f"{n:>8}  {trial[-1]:>11.3f}  {fast[-1]:>11.3f}")
    print("line", trial)
    print("line", fast)


if __name__ == "__main__":
    main()
