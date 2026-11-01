"""Hand-written contracts for stdin line endings and component case."""

from __future__ import annotations

import io

import pytest

from urlsyntax._cli import main


@pytest.mark.parametrize("check", [False, True], ids=["normal", "check"])
@pytest.mark.parametrize("invalid", [False, True], ids=["valid", "invalid"])
@pytest.mark.parametrize("prefix", ["", "http://first/\n"], ids=["single", "final"])
def test_unterminated_stdin_line_is_processed(check: bool, invalid: bool, prefix: str) -> None:
    stdin = prefix + ("ftp://bad/" if invalid else "HTTP://A:80/Path")
    out, err = io.StringIO(), io.StringIO()
    code = main(["--check"] if check else [], io.StringIO(stdin), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (
        1 if invalid else 0,
        "" if check else prefix + ("" if invalid else "http://a/Path\n"),
        "invalid (unsupported-scheme)\n" if invalid else "",
    )


@pytest.mark.parametrize("ending", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_stdin_preserves_case_outside_scheme_and_host(ending: str) -> None:
    stdin = "HTTP://UsEr:PaSs@Example.COM:80/Path?Key=Value#Frag" + ending
    out, err = io.StringIO(), io.StringIO()
    code = main([], io.StringIO(stdin), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (
        0,
        "http://UsEr:PaSs@example.com/Path?Key=Value#Frag\n",
        "",
    )
