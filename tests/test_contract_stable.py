"""Stable signatures, type aliases, values, documentation and safe diagnostics."""

from __future__ import annotations

import contextlib
import dataclasses
import doctest
import importlib
import inspect
import io
import pickle
import re
from pathlib import Path
from typing import get_args, get_type_hints

import pytest

import urlsyntax
from urlsyntax import (
    HostKind,
    HttpURL,
    InvalidURLError,
    Reason,
    Scheme,
    is_valid_http_url,
    parse_http_url,
)
from urlsyntax._cli import main


def test_signatures_and_defaults_are_stable() -> None:
    for name, parameters in {
        "parse_http_url": ["value", "allow_userinfo"],
        "is_valid_http_url": ["value", "allow_userinfo"],
        "normalize": ["value"],
        "resolve": ["base", "reference"],
        "InvalidURLError": ["reason"],
        "HttpURL": ["scheme", "userinfo", "host", "host_kind", "port", "path", "query", "fragment"],
    }.items():
        signature = inspect.signature(getattr(urlsyntax, name))
        assert list(signature.parameters) == parameters
        if "allow_userinfo" in parameters:
            option = signature.parameters["allow_userinfo"]
            assert option.default is True
            assert option.kind is inspect.Parameter.KEYWORD_ONLY
        assert get_type_hints(getattr(urlsyntax, name))
    assert get_args(Scheme) == ("http", "https")
    assert get_args(HostKind) == ("name", "ipv4", "ipv6")
    assert len(get_args(Reason)) == 18
    assert not hasattr(urlsyntax, "annotations")


def test_value_constructor_hash_copy_and_pickle() -> None:
    value = HttpURL("https", "", "::1", "ipv6", 0, "/", "", "")
    assert str(value) == "https://@[::1]:0/?#"
    assert value.effective_port == 0
    assert dataclasses.astuple(value) == ("https", "", "::1", "ipv6", 0, "/", "", "")
    restored = pickle.loads(pickle.dumps(value))
    assert restored == value and hash(restored) == hash(value)
    assert dataclasses.replace(value, fragment=None) != value
    assert HttpURL("http", None, "EXAMPLE", "name", 80, "", None, None).host == "EXAMPLE"


def test_public_docstrings_and_alias_examples_run() -> None:
    for name in urlsyntax.__all__:
        if name not in {"HostKind", "Reason", "Scheme"}:
            assert ">>>" in (getattr(urlsyntax, name).__doc__ or ""), name
    attempted = 0
    for module in ("urlsyntax", "_parse", "_errors", "_normalize", "_resolve", "_validate"):
        imported = importlib.import_module(
            module if module == "urlsyntax" else "urlsyntax." + module
        )
        result = doctest.testmod(imported)
        assert result.failed == 0
        attempted += result.attempted
    assert attempted >= 14


def test_guide_examples_run() -> None:
    guide = (Path(__file__).resolve().parents[1] / "GUIDE.md").read_text(encoding="utf-8")
    for block in re.findall(r"```python\n(.*?)```", guide, flags=re.DOTALL):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(block, "GUIDE.md", "exec"), {})
        assert out.getvalue().splitlines() == re.findall(r"^print\(.*\)  # (.+)$", block, re.M)


@pytest.mark.parametrize(
    "value",
    ["http://secret\n:password@host/", "ftp://h/?token=secret", "x" * 100000],
    ids=["malformed-credentials", "query-token", "long-input"],
)
def test_cli_invalid_diagnostics_never_repeat_input(value: str) -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main([value], stdout=out, stderr=err) == 1
    assert out.getvalue() == ""
    assert re.fullmatch(r"invalid \([a-z-]+\)\n", err.getvalue())
    assert len(err.getvalue()) < 64


def test_usage_diagnostics_are_bounded_and_do_not_quote_arguments() -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main(["--secret=" + "x" * 100000], stdout=out, stderr=err) == 2
    assert "secret" not in err.getvalue()
    assert len(err.getvalue()) < 250


def test_non_string_errors_do_not_quote_arbitrary_type_names() -> None:
    value = type("secret" * 10000, (), {})()
    with pytest.raises(TypeError, match=r"^value must be str$"):
        parse_http_url(value)


def test_empty_userinfo_is_rejected_when_disabled() -> None:
    with pytest.raises(InvalidURLError) as caught:
        parse_http_url("http://@a/", allow_userinfo=False)
    assert caught.value.reason == "userinfo-not-allowed"


def test_validator_rejects_empty_userinfo_when_disabled() -> None:
    assert not is_valid_http_url("http://@a/", allow_userinfo=False)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("scheme", "https"),
        ("userinfo", ""),
        ("host", "other"),
        ("host_kind", "name"),
        ("port", 80),
        ("path", "/other"),
        ("query", ""),
        ("fragment", ""),
    ],
)
def test_value_equality_compares_every_stored_field(field: str, replacement: object) -> None:
    value = HttpURL("http", None, "127.0.0.1", "ipv4", None, "/", None, None)
    assert dataclasses.replace(value, **{field: replacement}) != value  # type: ignore[arg-type]
