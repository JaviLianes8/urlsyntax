import pytest

from urlsyntax import InvalidURLError, normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("HTTP://Example.COM/", "http://example.com/"),
        ("https://EXAMPLE.com/Path", "https://example.com/Path"),
        ("http://example.com:80/", "http://example.com/"),
        ("https://example.com:443/", "https://example.com/"),
        ("http://example.com:443/", "http://example.com:443/"),
        ("http://example.com:8080/", "http://example.com:8080/"),
        ("https://example.com:0443/", "https://example.com/"),
        ("http://example.com:08080/", "http://example.com:8080/"),
        ("http://example.com:/", "http://example.com/"),
        ("http://example.com", "http://example.com/"),
        ("http://example.com/a/./b/../c", "http://example.com/a/c"),
        ("http://example.com/a/b/../../d", "http://example.com/d"),
        ("http://example.com/..", "http://example.com/"),
        ("http://example.com/a/%2e%2E/b", "http://example.com/b"),
        ("http://example.com/?", "http://example.com/?"),
        ("http://example.com/#", "http://example.com/#"),
        ("http://example.com/%7euser", "http://example.com/~user"),
        ("http://example.com/%2f", "http://example.com/%2F"),
        ("http://example.com/?q=%7e%2b", "http://example.com/?q=~%2B"),
        ("http://example.com/#%7e", "http://example.com/#~"),
        ("http://us%65r@example.com/", "http://user@example.com/"),
        ("http://ex%41mple.COM/", "http://example.com/"),
        ("https://[2001:DB8::1]/", "https://[2001:db8::1]/"),
        ("http://[2001:0db8:0:0:0:0:2:1]/", "http://[2001:db8::2:1]/"),
        ("http://[2001:db8:0:1:1:1:1:1]/", "http://[2001:db8:0:1:1:1:1:1]/"),
        ("http://[2001:db8:0:0:1:0:0:1]/", "http://[2001:db8::1:0:0:1]/"),
        ("http://[::ffff:192.0.2.1]/", "http://[::ffff:c000:201]/"),
        ("http://[0:0:0:0:0:0:0:0]/", "http://[::]/"),
    ],
)
def test_applies_expected_normalizations(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


def test_keeps_query_parameter_order() -> None:
    assert normalize("http://example.com/?b=2&a=1") == "http://example.com/?b=2&a=1"


def test_keeps_userinfo_case_and_empty_parts() -> None:
    assert normalize("http://User@example.com/") == "http://User@example.com/"
    assert normalize("http://user:@example.com/") == "http://user:@example.com/"
    assert normalize("http://@example.com/") == "http://@example.com/"


def test_keeps_trailing_slash_on_non_empty_path() -> None:
    assert normalize("http://example.com/dir/") == "http://example.com/dir/"


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "HTTP://Example.COM:80/a/./b/../c?q=1#x",
        "https://user@EXAMPLE.com:443/%7euser/?",
        "http://[2001:DB8::1]/a/../b",
        "http://[::ffff:1.2.3.4]/%2e%2e/%2E",
    ],
)
def test_normalize_is_idempotent(url: str) -> None:
    once = normalize(url)
    assert normalize(once) == once


def test_rejects_invalid_input_with_a_reason() -> None:
    with pytest.raises(InvalidURLError) as caught:
        normalize("ftp://example.com")
    assert caught.value.reason == "unsupported-scheme"
    with pytest.raises(ValueError):
        normalize("not a url")


def test_rejects_non_string_input() -> None:
    with pytest.raises(TypeError):
        normalize(None)  # type: ignore[arg-type]
