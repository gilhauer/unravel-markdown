# Copyright (C) 2026 Gil Hauer
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE in the project root for the full license text.

import ast
import runpy
import subprocess
import sys
from pathlib import Path

from unravel.cli import main


def test_sieve_example_is_current_and_runs(tmp_path):
    example = Path(__file__).resolve().parents[1] / "examples" / "sieve"
    source = example / "sieve.md"
    output = tmp_path / "generated"

    assert main([str(source), "-o", str(output)]) == 0
    generated = {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert set(generated) == {
        Path("main.py"),
        Path("sieve.py"),
        Path("check_sieve.py"),
        Path(".unravel-manifest.json"),
    }
    for relative, contents in generated.items():
        assert contents == (example / "generated" / relative).read_bytes(), relative

    assert main([str(source), "-o", str(output), "--check"]) == 0

    checks = subprocess.run(
        [sys.executable, "-B", str(output / "check_sieve.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert checks.returncode == 0, checks.stdout + checks.stderr

    demo = subprocess.run(
        [sys.executable, "-B", str(output / "main.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert demo.returncode == 0, demo.stdout + demo.stderr
    assert ast.literal_eval(demo.stdout) == [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
        43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    ]


def test_sieve_example_matches_trial_division(tmp_path):
    source = Path(__file__).resolve().parents[1] / "examples" / "sieve" / "sieve.md"
    output = tmp_path / "generated"

    assert main([str(source), "-o", str(output)]) == 0
    sieve = runpy.run_path(str(output / "sieve.py"))["sieve"]

    for bound in range(-5, 201):
        expected = [
            candidate
            for candidate in range(2, bound + 1)
            if all(candidate % divisor for divisor in range(2, candidate))
        ]
        assert sieve(bound) == expected, bound
