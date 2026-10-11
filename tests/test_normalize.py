import pytest

from urlsyntax import normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("HTTP://Example.COM/", "http://example.com/"),
        ("https://EXAMPLE.com/Path", "https://example.com/Path"),
        ("http://example.com:80/", "http://example.com/"),
        ("https://example.com:443/", "https://example.com/"),
        ("http://example.com:8080/", "http://example.com:8080/"),
        ("https://example.com:0443/", "https://example.com/"),
        ("http://example.com", "http://example.com/"),
        ("http://example.com/a/./b/../c", "http://example.com/a/c"),
        ("http://example.com/a/b/../../d", "http://example.com/d"),
        ("http://example.com/..", "http://example.com/"),
        ("http://example.com/?", "http://example.com/"),
        ("http://example.com/#", "http://example.com/"),
        ("http://example.com/%7euser", "http://example.com/~user"),
        ("http://example.com/%2f", "http://example.com/%2F"),
        ("https://[2001:DB8::1]/", "https://[2001:db8::1]/"),
    ],
)
def test_applies_expected_normalizations(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


def test_keeps_query_parameter_order() -> None:
    assert normalize("http://example.com/?b=2&a=1") == "http://example.com/?b=2&a=1"


def test_keeps_userinfo_case() -> None:
    assert normalize("http://User@example.com/") == "http://User@example.com/"


def test_keeps_trailing_slash_on_non_empty_path() -> None:
    assert normalize("http://example.com/dir/") == "http://example.com/dir/"


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "HTTP://Example.COM:80/a/./b/../c?q=1#x",
        "https://user@EXAMPLE.com:443/%7euser/?",
        "http://[2001:DB8::1]/a/../b",
    ],
)
def test_normalize_is_idempotent(url: str) -> None:
    once = normalize(url)
    assert normalize(once) == once


def test_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        normalize("ftp://example.com")
    with pytest.raises(ValueError):
        normalize("not a url")
