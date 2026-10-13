"""Hand-written cases for the browser agreement that tests/test_wpt.py checks on the full corpus.

These run without the fetched corpus. Every case below is written by hand from the rules in
the WHATWG URL Standard (https://url.spec.whatwg.org/), not copied from web-platform-tests.
"""

from __future__ import annotations

import pytest

from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve

# Hand-written: inputs a browser URL parser refuses, so this library must refuse them too.
BROWSER_FAILURES = [
    "http://a b/",
    "http://[::1/",
    "http://1.2.3.4.5/",
    "http://0x7f.1/",
    "http://example.com:65536/",
    "http://exa%2Fmple/",
    "https://",
    "http://a:b@c:-1/",
    "http://@/x",
]

# Hand-written: input and the normal form whose text matches the browser href.
BROWSER_NORMAL_FORMS = [
    ("HTTP://EXAMPLE.com:80/a/../b", "http://example.com/b"),
    ("https://example.com:443/?", "https://example.com/?"),
    ("http://example.com/%7Efoo", "http://example.com/~foo"),
    ("http://[0:0:0:0:0:0:0:1]/", "http://[::1]/"),
    ("http://EXAMPLE.COM.", "http://example.com./"),
    ("http://example.com/a/./b/", "http://example.com/a/b/"),
]

# Hand-written: base, reference and the resolved URL a browser gives.
BROWSER_RESOLUTIONS = [
    ("http://example.org/foo/bar", "../baz", "http://example.org/baz"),
    ("http://example.org/foo/bar", "//other/x", "http://other/x"),
    ("http://example.org/foo/bar", "?q", "http://example.org/foo/bar?q"),
    ("http://example.org/foo/bar", "#f", "http://example.org/foo/bar#f"),
    ("http://example.org/a/b/c", "../../../../g", "http://example.org/g"),
]

# Hand-written: ASCII hosts and the host a browser domain parser returns (None: refused).
BROWSER_HOSTS = [
    ("EXAMPLE.com", "example.com"),
    ("example.com.", "example.com."),
    ("xn--nxasmq6b.com", "xn--nxasmq6b.com"),
    ("127.0.0.1", "127.0.0.1"),
    ("x_y.example", "x_y.example"),
    ("192.168.0.257", None),
]


@pytest.mark.parametrize("url", BROWSER_FAILURES)
def test_inputs_the_browser_refuses_are_refused(url: str) -> None:
    assert not is_valid_http_url(url)


@pytest.mark.parametrize(("url", "expected"), BROWSER_NORMAL_FORMS)
def test_normal_form_matches_the_browser_href(url: str, expected: str) -> None:
    assert normalize(url) == expected


@pytest.mark.parametrize(("base", "reference", "expected"), BROWSER_RESOLUTIONS)
def test_resolution_matches_the_browser(base: str, reference: str, expected: str) -> None:
    assert resolve(base, reference) == expected


@pytest.mark.parametrize(("host", "expected"), BROWSER_HOSTS)
def test_ascii_host_matches_the_browser_domain_parser(host: str, expected: str | None) -> None:
    url = f"http://{host}/"
    if expected is None:
        with pytest.raises(InvalidURLError):
            parse_http_url(url)
    else:
        assert parse_http_url(url).host == expected
