"""Hand-written stdin contracts for the installed console executable."""

from __future__ import annotations

import subprocess
from pathlib import Path


def check_stdin_contracts(script: Path, work: Path) -> None:
    cases = [
        ("", 0, "", ""),
        (" \n", 1, "", "invalid (illegal-character)\n"),
        ("\t\n", 1, "", "invalid (illegal-character)\n"),
        (" \t\n", 1, "", "invalid (illegal-character)\n"),
        ("http://a/a%2Fb\n", 0, "http://a/a%2Fb\n", ""),
        ("http://a/a%3Fb\n", 0, "http://a/a%3Fb\n", ""),
        ("HTTP://A:80/%7e%23b?x=%2f#%3f\n", 0, "http://a/~%23b?x=%2F#%3F\n", ""),
        ("http://a/?\n", 0, "http://a/?\n", ""),
        ("http://a/#\n", 0, "http://a/#\n", ""),
        ("http://a/?#\n", 0, "http://a/?#\n", ""),
    ]
    for check in (False, True):
        for stdin, status, stdout, stderr in cases:
            result = subprocess.run(
                [str(script), *(["--check"] if check else [])],
                input=stdin,
                text=True,
                capture_output=True,
                cwd=work,
                timeout=60,
            )
            assert (result.returncode, result.stdout, result.stderr) == (
                status,
                "" if check else stdout,
                stderr,
            ), (check, stdin)
