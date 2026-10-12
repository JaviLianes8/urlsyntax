import pytest

from urlsyntax import is_valid_http_url

VALID = [
    "http://example.com",
    "https://example.com/",
    "HTTPS://example.com/",
    "https://example.com/path?q=1#frag",
    "http://example.com:8080/a/b",
    "http://example.com:/",
    "https://user:pass@example.com/secure",
    "http://192.168.0.1/",
    "https://[2001:db8::1]:443/",
    "http://[::ffff:192.0.2.1]/",
    "http://example.com/%7euser",
    "https://sub.domain.example.co.uk/path",
    "http://xn--bcher-kva.example/",
    "http://a/?q=/x?y#frag/?",
    "http://a/p:@!$&'()*+,;=",
    "http://ex%41mple.com/",
    "http://example.com./",
]

INVALID = [
    "",
    "ftp://example.com",
    "mailto:someone@example.com",
    "file:///etc/hosts",
    "ws://example.com/socket",
    "http:///no-host",
    "https://",
    "http:example.com",
    "example.com",
    "//example.com",
    "http://exa mple.com",
    "http://example.com/a\tb",
    "http://example.com/\u00e9",
    "http://b\u00fccher.example/",
    "http://example.com/%zz",
    "http://example.com/%2",
    "http://example.com:notaport/",
    "http://example.com:99999/",
    "http://[not-ipv6]/",
    "http://2001::1",
    "http://[::%31]/",
    "http://[fe80::1%25eth0]/",
    "http://[v1.future]/",
    "http://::@c@d:2",
    "http://a@b@example.com/",
    "http://example.com/[x]",
    "http://example.com/?a[]=1",
    "http://example.com/#a#b",
    "http://ho%00st/",
    "http://%e2%98%83/",
    "http://0x7f.1/",
    "http://127.1/",
    "http://010.0.0.1/",
    "http://1.2.3.4./",
    "http://4294967295/",
    "http://exa[mple.com/",
]


@pytest.mark.parametrize("url", VALID)
def test_accepts_valid_http_urls(url: str) -> None:
    assert is_valid_http_url(url) is True


@pytest.mark.parametrize("url", INVALID)
def test_rejects_invalid_or_non_http_urls(url: str) -> None:
    assert is_valid_http_url(url) is False


def test_rejects_non_string_input() -> None:
    assert is_valid_http_url(None) is False
    assert is_valid_http_url(123) is False
    assert is_valid_http_url(b"http://example.com/") is False


def test_userinfo_can_be_refused() -> None:
    assert is_valid_http_url("http://user@example.com/") is True
    assert is_valid_http_url("http://user@example.com/", allow_userinfo=False) is False
    assert is_valid_http_url("http://example.com/@x", allow_userinfo=False) is True
