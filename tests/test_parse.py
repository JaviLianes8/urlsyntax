import dataclasses
import pickle

import pytest

from urlsyntax import HttpURL, InvalidURLError, Reason, normalize, parse_http_url


def test_components_are_in_normal_form() -> None:
    url = parse_http_url("HTTP://Us%65r:pw@Ex%41mple.COM:8080/a/./b/%7e?q=1#Top")
    assert url == HttpURL(
        scheme="http",
        userinfo="User:pw",
        host="example.com",
        host_kind="name",
        port=8080,
        path="/a/b/~",
        query="q=1",
        fragment="Top",
    )


def test_absent_and_empty_components_differ() -> None:
    bare = parse_http_url("https://example.com")
    empty = parse_http_url("https://@example.com/?#")
    assert (bare.userinfo, bare.query, bare.fragment, bare.path) == (None, None, None, "/")
    assert (empty.userinfo, empty.query, empty.fragment) == ("", "", "")


@pytest.mark.parametrize(
    ("url", "host", "kind"),
    [
        ("http://192.0.2.1/", "192.0.2.1", "ipv4"),
        ("http://%31%39%32.0.2.1/", "192.0.2.1", "ipv4"),
        ("http://[2001:DB8::0:1]/", "2001:db8::1", "ipv6"),
        ("http://example.com/", "example.com", "name"),
        ("http://1.2.3.x/", "1.2.3.x", "name"),
    ],
)
def test_host_kind_says_what_the_host_denotes(url: str, host: str, kind: str) -> None:
    parsed = parse_http_url(url)
    assert (parsed.host, parsed.host_kind) == (host, kind)


def test_default_port_is_none_and_effective_port_fills_it() -> None:
    assert parse_http_url("http://a:80/").port is None
    assert parse_http_url("http://a/").effective_port == 80
    assert parse_http_url("https://a/").effective_port == 443
    assert parse_http_url("https://a:8443/").effective_port == 8443
    assert parse_http_url("http://a:0/").port == 0


def test_str_is_the_normal_form() -> None:
    for url in ("http://[::1]:81/x?#", "https://u@h/", "http://a"):
        assert str(parse_http_url(url)) == normalize(url)


def test_the_result_is_immutable() -> None:
    url = parse_http_url("http://a/")
    with pytest.raises(dataclasses.FrozenInstanceError):
        url.host = "b"  # type: ignore[misc]


REASONS: list[tuple[str, Reason]] = [
    ("", "empty"),
    ("http://a b/", "illegal-character"),
    ("http://a/\u00e9", "illegal-character"),
    ("http://a/%4", "bad-percent-escape"),
    ("ftp://a/", "unsupported-scheme"),
    ("a/b", "unsupported-scheme"),
    ("http:/a", "missing-authority"),
    ("http://a[@b/", "bad-userinfo"),
    ("http://a@b@c/", "bad-userinfo"),
    ("http:///", "empty-host"),
    ("http://:80/", "empty-host"),
    ("http://a:b:c/", "bad-port"),
    ("http://ex]ample/", "bad-host"),
    ("http://[::1/", "bad-host"),
    ("http://[::1]x/", "bad-host"),
    ("http://[::g]/", "bad-ipv6"),
    ("http://[::1%25lo]/", "bad-ipv6"),
    ("http://[v7.a:b]/", "unsupported-ip-literal"),
    ("http://ex%2Fample/", "host-escape"),
    ("http://%C3%BC.example/", "host-escape"),
    ("http://127.1/", "ambiguous-ipv4"),
    ("http://a.0x10/", "ambiguous-ipv4"),
    ("http://0x/", "ambiguous-ipv4"),
    ("http://a:8o/", "bad-port"),
    ("http://a:65536/", "port-out-of-range"),
    ("http://a/[", "bad-path"),
    ("http://a/?[", "bad-query"),
    ("http://a/#]", "bad-fragment"),
    ("http://a/##", "bad-fragment"),
]


@pytest.mark.parametrize(("url", "reason"), REASONS)
def test_each_rule_reports_its_reason(url: str, reason: Reason) -> None:
    with pytest.raises(InvalidURLError) as caught:
        parse_http_url(url)
    assert caught.value.reason == reason
    assert f"({reason})" in str(caught.value)


def test_every_reason_is_reachable() -> None:
    reached = {reason for _, reason in REASONS} | {"userinfo-not-allowed"}
    assert reached == set(Reason.__args__)  # type: ignore[attr-defined]


def test_userinfo_not_allowed_is_its_own_reason() -> None:
    with pytest.raises(InvalidURLError) as caught:
        parse_http_url("http://user:secret@a/", allow_userinfo=False)
    assert caught.value.reason == "userinfo-not-allowed"
    assert "secret" not in str(caught.value)


def test_the_error_pickles_with_its_reason() -> None:
    error = InvalidURLError("bad-host")
    copy = pickle.loads(pickle.dumps(error))
    assert type(copy) is InvalidURLError
    assert (copy.reason, str(copy)) == (error.reason, str(error))


def test_non_string_input_raises_type_error() -> None:
    with pytest.raises(TypeError):
        parse_http_url(b"http://a/")  # type: ignore[arg-type]
