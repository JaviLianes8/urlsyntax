"""Safe, semantics-preserving normalization of http and https URLs."""

from __future__ import annotations

from ._parse import parse_http_url


def normalize(value: str) -> str:
    """Return the normal form of ``value`` without changing what it addresses.

    Follows RFC 3986 section 6.2.2 and 6.2.3 with the http(s) rules of RFC 9110
    section 4.2.3: lower-case scheme and host, upper-case hex in percent escapes and
    decode those that stand for unreserved characters, resolve ``.`` and ``..``
    segments, drop an empty or default port (80 for http, 443 for https), and turn an
    empty path into ``/``. IPv6 literals follow RFC 5952 section 4, written entirely in
    hexadecimal (not the mixed notation of its section 5), as browsers write them.
    Left untouched on purpose: userinfo case, query parameter order, a trailing
    slash, and an empty ``?`` or ``#``. Raises ``InvalidURLError`` (a ``ValueError``)
    for anything ``parse_http_url`` refuses, and ``TypeError`` for a non-string.
    """
    return str(parse_http_url(value))
