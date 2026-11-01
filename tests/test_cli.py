from __future__ import annotations

import io
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

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
    assert err == "invalid (unsupported-scheme)\ninvalid (ambiguous-ipv4)\n"


def test_check_prints_nothing() -> None:
    assert _run(["--check", "http://a/"]) == (0, "", "")
    assert _run(["--check", "http://a b/"])[0] == 1


def test_no_userinfo_refuses_credentials() -> None:
    assert _run(["http://u@a/"])[0] == 0
    code, _, err = _run(["--no-userinfo", "http://u@a/"])
    assert code == 1
    assert "userinfo-not-allowed" in err


def test_invalid_lines_are_printed_without_credentials_or_control_characters() -> None:
    code, _, err = _run(["--no-userinfo"], "http://u:secret@a/\nhttp://a/\x1b[31m\n")
    assert code == 1
    assert err == ("invalid (userinfo-not-allowed)\ninvalid (illegal-character)\n")


def test_usage_errors_exit_two_on_the_given_streams() -> None:
    code, out, err = _run(["--bogus"])
    assert (code, out) == (2, "")
    assert "invalid command-line arguments" in err


def test_help_goes_to_the_given_stdout() -> None:
    code, out, _ = _run(["--help"])
    assert code == 0
    assert "--no-userinfo" in out


def test_runs_as_a_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "urlsyntax", "http://A:80"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )
    assert (result.returncode, result.stdout) == (0, "http://a/\n"), result.stderr


@pytest.mark.parametrize("argv", [[], ["--check"]])
@pytest.mark.parametrize("prefix", [b"", b"http://a/\n" * 2000], ids=["invalid", "mixed"])
def test_malformed_stdin_encoding_has_a_fixed_diagnostic(argv: list[str], prefix: bytes) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "urlsyntax", *argv],
        input=prefix + b"http://user:secret@x/\xff\nhttp://after/\n",
        capture_output=True,
        timeout=30,
        env={**os.environ, "PYTHONPATH": str(SRC), "PYTHONIOENCODING": "utf-8:strict"},
    )
    assert (result.returncode, result.stderr.splitlines()) == (
        1,
        [b"invalid (stdin-decoding-error)"],
    )
    if argv or not prefix:
        assert result.stdout == b""
    else:
        # Decoder read-ahead determines how much of the valid prefix was processed.
        assert all(line == b"http://a/" for line in result.stdout.splitlines())
        assert 0 < len(result.stdout.splitlines()) <= 2000


def test_stdin_decoding_failure_retains_output_for_preceding_lines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def lines() -> Iterator[str]:
        yield "HTTP://Example.COM:80/a/../b\n"
        yield "https://B:443\n"
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")

    # Controlled iteration makes the contract independent of decoder read-ahead.
    monkeypatch.setattr(sys, "stdin", lines())
    out, err = io.StringIO(), io.StringIO()
    code = main([], stdout=out, stderr=err)
    assert (code, out.getvalue(), err.getvalue()) == (
        1,
        "http://example.com/b\nhttps://b/\n",
        "invalid (stdin-decoding-error)\n",
    )


@pytest.mark.parametrize("value", [" http://a/", "http://a/ ", "\thttp://a/", "http://a/\t"])
def test_stdin_preserves_invalid_whitespace(value: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "urlsyntax"],
        input=value + "\n",
        text=True,
        capture_output=True,
        timeout=30,
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )
    assert (result.returncode, result.stdout, result.stderr) == (
        1,
        "",
        "invalid (illegal-character)\n",
    )


def test_no_userinfo_refuses_an_empty_userinfo_delimiter() -> None:
    assert _run(["--no-userinfo", "http://@a/"]) == (
        1,
        "",
        "invalid (userinfo-not-allowed)\n",
    )
