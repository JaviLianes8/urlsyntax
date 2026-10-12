import pytest

from urlsyntax import is_valid_http_url

VALID = [
    "http://example.com",
    "https://example.com/",
    "https://example.com/path?q=1#frag",
    "http://example.com:8080/a/b",
    "https://user:pass@example.com/secure",
    "http://192.168.0.1/",
    "https://[2001:db8::1]:443/",
    "http://example.com/%7euser",
    "https://sub.domain.example.co.uk/path",
]

INVALID = [
    "",
    "ftp://example.com",
    "mailto:someone@example.com",
    "file:///etc/hosts",
    "ws://example.com/socket",
    "http:///no-host",
    "https://",
    "example.com",
    "//example.com",
    "http://exa mple.com",
    "http://example.com/a\tb",
    "http://example.com/é",
    "http://example.com/%zz",
    "http://example.com/%2",
    "http://example.com:notaport/",
    "http://example.com:99999/",
    "http://[not-ipv6]/",
]


@pytest.mark.parametrize("url", VALID)
def test_accepts_valid_http_urls(url: str) -> None:
    assert is_valid_http_url(url) is True


@pytest.mark.parametrize("url", INVALID)
def test_rejects_invalid_or_non_http_urls(url: str) -> None:
    assert is_valid_http_url(url) is False


def test_rejects_non_string_input() -> None:
    assert is_valid_http_url(None) is False  # type: ignore[arg-type]
    assert is_valid_http_url(123) is False  # type: ignore[arg-type]
