"""The public API is typed: mypy infers the documented types and rejects wrong ones."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

api = pytest.importorskip("mypy.api")

SRC = Path(__file__).resolve().parents[1] / "src"

SNIPPET = """
from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve
url = parse_http_url("http://a/")
reveal_type(url.scheme)
reveal_type(url.host_kind)
reveal_type(url.port)
reveal_type(url.effective_port)
reveal_type(url.query)
reveal_type(normalize("http://a/"))
reveal_type(resolve("http://a/", "b"))
reveal_type(is_valid_http_url(None))
reveal_type(InvalidURLError("bad-host").reason)
InvalidURLError("no-such-reason")
parse_http_url("http://a/", False)
normalize(b"http://a/")
url.port = 1
"""


@pytest.fixture(scope="module")
def mypy_output(tmp_path_factory: pytest.TempPathFactory) -> str:
    folder = tmp_path_factory.mktemp("typing")
    target = folder / "snippet.py"
    target.write_text(SNIPPET, encoding="utf-8")
    config = folder / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {SRC.as_posix()}\n", encoding="utf-8")
    cache = str(folder / "cache")
    out, err, _ = api.run(
        ["--strict", "--config-file", str(config), "--cache-dir", cache, str(target)]
    )
    return str(out) + str(err)


def test_fields_have_their_documented_types(mypy_output: str) -> None:
    assert re.findall(r"'(\w+)'", _revealed(mypy_output, 4)) == ["http", "https"]
    assert re.findall(r"'(\w+)'", _revealed(mypy_output, 5)) == ["name", "ipv4", "ipv6"]
    assert _revealed(mypy_output, 6) == "int | None"
    assert _revealed(mypy_output, 7) == "int"
    assert _revealed(mypy_output, 8) == "str | None"


def test_functions_return_plain_types(mypy_output: str) -> None:
    assert _revealed(mypy_output, 9) == "str"
    assert _revealed(mypy_output, 10) == "str"
    assert _revealed(mypy_output, 11) == "bool"


def test_reasons_are_a_closed_set(mypy_output: str) -> None:
    assert "'ambiguous-ipv4'" in _revealed(mypy_output, 12)
    assert re.search(r"snippet\.py:13: error: .*\[arg-type\]", mypy_output), mypy_output


def test_misuse_is_rejected(mypy_output: str) -> None:
    assert re.search(r"snippet\.py:14: error: Too many positional arguments", mypy_output)
    assert re.search(r"snippet\.py:15: error: .*\[arg-type\]", mypy_output)
    assert re.search(r"snippet\.py:16: error: .*\[misc\]", mypy_output)


def _revealed(output: str, line: int) -> str:
    match = re.search(rf"snippet\.py:{line}: note: Revealed type is \"(.+)\"", output)
    assert match, output
    # Older mypy releases spell builtins with their module prefix.
    return match.group(1).replace("builtins.", "")
