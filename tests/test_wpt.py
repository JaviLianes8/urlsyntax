"""Agreement with the WHATWG URL Standard on the web-platform-tests corpus.

The corpus is not committed. `python scripts/fetch_upstream.py` fetches urltestdata.json and
toascii.json at the revision pinned in tests/upstream/MANIFEST.json; these tests skip until
then and fail if a file differs from the manifest.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Any

import pytest
from conftest import read_upstream

from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve
from urlsyntax._chars import normalize_percent
from urlsyntax._parse import check_characters


def _cases(name: str) -> list[dict[str, Any]]:
    entries = json.loads(read_upstream(name).decode("utf-8"))
    return [e for e in entries if isinstance(e, dict)]


@pytest.fixture(scope="module")
def urls() -> list[dict[str, Any]]:
    return _cases("urltestdata.json")


@pytest.fixture(scope="module")
def hosts() -> list[dict[str, Any]]:
    return _cases("toascii.json")


def _whatwg_view(url: str) -> str:
    """Apply the two WHATWG serialization habits that RFC 3986 does not share.

    From url.bs: the userinfo percent-encode set covers ";", "=" and ":" (inside a
    password), an empty password or userinfo is not serialized, and the special-query
    percent-encode set covers "'". None of these change the RFC 3986 meaning of
    ``normalize``'s output, but they change the text.
    """
    parsed = parse_http_url(url)
    userinfo = parsed.userinfo
    if userinfo is not None:
        user, colon, password = userinfo.partition(":")
        user = user.replace(";", "%3B").replace("=", "%3D")
        password = password.replace(";", "%3B").replace("=", "%3D").replace(":", "%3A")
        userinfo = f"{user}:{password}" if colon and password else user
        userinfo = userinfo or None
    query = None if parsed.query is None else parsed.query.replace("'", "%27")
    return str(dataclasses.replace(parsed, userinfo=userinfo, query=query))


def _is_http_base(base: object) -> bool:
    return isinstance(base, str) and is_valid_http_url(base)


def test_no_input_the_browser_parser_rejects_is_accepted(urls: list[dict[str, Any]]) -> None:
    accepted = [c["input"] for c in urls if c.get("failure") and is_valid_http_url(c["input"])]
    assert accepted == []


def test_accepted_inputs_normalize_like_the_browser_href(urls: list[dict[str, Any]]) -> None:
    checked = 0
    for case in urls:
        if not is_valid_http_url(case["input"]):
            continue
        assert _whatwg_view(normalize(case["input"])) == normalize(case["href"]), case
        checked += 1
    assert checked >= 85


def test_resolved_references_agree_with_the_browser(urls: list[dict[str, Any]]) -> None:
    checked = 0
    for case in urls:
        if is_valid_http_url(case["input"]) or not _is_http_base(case.get("base")):
            continue
        try:
            target = resolve(case["base"], case["input"])
        except InvalidURLError:
            continue
        assert not case.get("failure"), case
        assert _whatwg_view(normalize(target)) == normalize(case["href"]), case
        checked += 1
    assert checked >= 30


def _plain_uri_text(href: str) -> bool:
    try:
        check_characters(href)
    except InvalidURLError:
        return False
    return True


def test_every_browser_href_made_of_uri_characters_is_accepted(urls: list[dict[str, Any]]) -> None:
    hrefs = [
        c["href"] for c in urls if not c.get("failure") and c.get("protocol") in ("http:", "https:")
    ]
    plain = [h for h in hrefs if _plain_uri_text(h)]
    assert len(plain) >= 230
    # Browsers leave "[", "]" and a second "#" unescaped in the path and fragment;
    # RFC 3986 allows none of them there. Those are the only refusals.
    refused = {}
    for href in plain:
        try:
            parse_http_url(href)
        except InvalidURLError as error:
            refused[href] = error.reason
    assert refused == {
        "http://foo/path;a??e#f#g": "bad-fragment",
        "http://example.org/foo/[61:24:74]:98": "bad-path",
        "http://example.org/foo/[61:27]/:foo": "bad-path",
    }
    plain = [h for h in plain if h not in refused]
    # The browser's own output is already in normal form, apart from percent escapes,
    # which browsers keep as written and RFC 3986 section 6.2.2 canonicalizes.
    for href in plain:
        assert normalize(href) == normalize_percent(href), href


def test_ascii_hosts_follow_the_browser_domain_parser(hosts: list[dict[str, Any]]) -> None:
    ascii_cases = [c for c in hosts if c["input"].isascii()]
    assert len(ascii_cases) >= 20
    for case in ascii_cases:
        url = f"http://{case['input']}/"
        if case["output"] is None:
            assert not is_valid_http_url(url), case
        else:
            assert parse_http_url(url).host == case["output"], case
