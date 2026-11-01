"""Hand-written contracts for the underlying contents of str subclasses."""

from __future__ import annotations

from collections.abc import Iterator
from typing import SupportsIndex

import pytest

from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve


class MaskedIndex(str):
    def __getitem__(self, key: SupportsIndex | slice) -> str:
        return "a"


class HiddenText(str):
    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return False


class ReplacedText(str):
    def __str__(self) -> str:
        return "http://replacement/"


@pytest.mark.parametrize("string_type", [MaskedIndex, HiddenText, ReplacedText])
@pytest.mark.parametrize(
    ("value", "reason"),
    [("http://x/%zz", "bad-percent-escape"), ("http://x/#ok\nsecret", "illegal-character")],
)
def test_subclass_invalid_contents_are_rejected(
    string_type: type[str], value: str, reason: str
) -> None:
    text = string_type(value)
    for operation in (parse_http_url, normalize):
        with pytest.raises(InvalidURLError) as caught:
            operation(text)
        assert caught.value.reason == reason
    assert not is_valid_http_url(text)


@pytest.mark.parametrize("string_type", [MaskedIndex, HiddenText, ReplacedText])
@pytest.mark.parametrize(
    ("value", "reason"),
    [("http://x/%zz", "bad-percent-escape"), ("http://x/#ok\nsecret", "illegal-character")],
)
def test_resolve_validates_subclass_base_contents(
    string_type: type[str], value: str, reason: str
) -> None:
    with pytest.raises(InvalidURLError) as caught:
        resolve(string_type(value), "https://other/")
    assert caught.value.reason == reason


@pytest.mark.parametrize("string_type", [MaskedIndex, HiddenText, ReplacedText])
@pytest.mark.parametrize(
    ("value", "reason"),
    [("%zz/../ok", "bad-percent-escape"), ("#ok\nsecret", "illegal-character")],
)
def test_resolve_validates_subclass_reference_contents(
    string_type: type[str], value: str, reason: str
) -> None:
    with pytest.raises(InvalidURLError) as caught:
        resolve("http://x/", string_type(value))
    assert caught.value.reason == reason


@pytest.mark.parametrize("string_type", [MaskedIndex, HiddenText, ReplacedText])
def test_valid_subclasses_use_contents_without_custom_methods(string_type: type[str]) -> None:
    value = string_type("HTTP://Example.com:80/%7e?")
    assert parse_http_url(value) == parse_http_url("http://example.com/~?")
    assert normalize(value) == "http://example.com/~?"
    assert is_valid_http_url(value)
    assert resolve(value, string_type("")) == "HTTP://Example.com:80/%7e?"
    assert resolve(value, string_type("./%61")) == "HTTP://Example.com:80/%61"
