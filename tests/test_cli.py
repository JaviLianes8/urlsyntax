import io
import os
import subprocess
import sys
from pathlib import Path

from urlsyntax._cli import main

SRC = Path(__file__).resolve().parents[1] / "src"


def _run(argv: list[str], stdin: str = "") -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = main(argv, stdin=io.StringIO(stdin), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def test_prints_the_normal_form_of_each_argument() -> None:
    code, out, err = _run(["HTTP://Example.COM:80/a/../b", "https://[::0:1]/"])
    assert (code, out, err) == (0, "http://example.com/b\nhttps://[::1]/\n", "")


def test_reads_lines_from_stdin_and_skips_blank_ones() -> None:
    code, out, _ = _run([], "http://A/\r\n\nhttps://b:443\n")
    assert (code, out) == (0, "http://a/\nhttps://b/\n")


def test_reports_invalid_urls_and_exits_one() -> None:
    code, out, err = _run(["http://a/", "ftp://b/", "http://127.1/"])
    assert code == 1
    assert out == "http://a/\n"
    assert (
        err == "invalid (unsupported-scheme): ftp://b/\ninvalid (ambiguous-ipv4): http://127.1/\n"
    )


def test_check_prints_nothing() -> None:
    assert _run(["--check", "http://a/"]) == (0, "", "")
    assert _run(["--check", "http://a b/"])[0] == 1


def test_no_userinfo_refuses_credentials() -> None:
    assert _run(["http://u@a/"])[0] == 0
    code, _, err = _run(["--no-userinfo", "http://u@a/"])
    assert code == 1
    assert "userinfo-not-allowed" in err


def test_usage_errors_exit_two() -> None:
    assert _run(["--bogus"])[0] == 2


def test_runs_as_a_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "urlsyntax", "http://A:80"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )
    assert (result.returncode, result.stdout) == (0, "http://a/\n"), result.stderr
