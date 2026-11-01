"""Hand-written contracts for stdin contents, line endings and normalization."""

from __future__ import annotations

import io

import pytest

from urlsyntax._cli import main


@pytest.mark.parametrize("check", [False, True], ids=["normal", "check"])
def test_empty_stdin_succeeds_without_output(check: bool) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = main(["--check"] if check else [], io.StringIO(""), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (0, "", "")


@pytest.mark.parametrize("check", [False, True], ids=["normal", "check"])
@pytest.mark.parametrize("whitespace", [" ", "\t", " \t"], ids=["space", "tab", "mixed"])
@pytest.mark.parametrize("ending", ["\n", "\r\n", ""], ids=["lf", "crlf", "unterminated"])
def test_whitespace_only_stdin_is_invalid(check: bool, whitespace: str, ending: str) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = main(["--check"] if check else [], io.StringIO(whitespace + ending), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (1, "", "invalid (illegal-character)\n")


@pytest.mark.parametrize("check", [False, True], ids=["normal", "check"])
@pytest.mark.parametrize(
    ("stdin", "expected"),
    [
        ("http://a/a%2Fb\n", "http://a/a%2Fb\n"),
        ("http://a/a%3Fb\n", "http://a/a%3Fb\n"),
        ("HTTP://A:80/%7e%23b?x=%2f#%3f\n", "http://a/~%23b?x=%2F#%3F\n"),
    ],
    ids=["encoded-slash", "encoded-question", "encoded-hash-and-normalization"],
)
def test_stdin_preserves_reserved_percent_escapes(check: bool, stdin: str, expected: str) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = main(["--check"] if check else [], io.StringIO(stdin), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (0, "" if check else expected, "")


@pytest.mark.parametrize("check", [False, True], ids=["normal", "check"])
@pytest.mark.parametrize("delimiter", ["?", "#", "?#"], ids=["query", "fragment", "both"])
def test_stdin_preserves_empty_query_and_fragment(check: bool, delimiter: str) -> None:
    stdin = "http://a/" + delimiter + "\n"
    out, err = io.StringIO(), io.StringIO()
    code = main(["--check"] if check else [], io.StringIO(stdin), out, err)
    assert (code, out.getvalue(), err.getvalue()) == (0, "" if check else stdin, "")


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
