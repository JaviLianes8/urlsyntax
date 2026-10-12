"""Parse an http or https URL into its components in normal form."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, NamedTuple

from ._chars import (
    ALLOWED,
    PATH,
    QUERY,
    USERINFO,
    normalize_percent,
    only,
    percent_escapes_are_valid,
)
from ._dots import remove_dot_segments
from ._errors import InvalidURLError
from ._host import HostKind, canonical_host

Scheme = Literal["http", "https"]

# RFC 3986 Appendix B, copied as published.
_APPENDIX_B = re.compile(r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?")
_DEFAULT_PORT = {"http": 80, "https": 443}


class Parts(NamedTuple):
    """The five components of a URI reference; None means the delimiter was absent."""

    scheme: str | None
    authority: str | None
    path: str
    query: str | None
    fragment: str | None


def split_reference(text: str) -> Parts:
    """Split a URI reference with the RFC 3986 Appendix B regular expression."""
    match = _APPENDIX_B.match(text)
    assert match is not None  # every group is optional, so the pattern always matches
    return Parts(match[2], match[4], match[5], match[7], match[9])


def check_characters(value: str) -> None:
    """Raise unless ``value`` is non-empty URI text with well-formed escapes."""
    if not value:
        raise InvalidURLError("empty")
    if not only(value, ALLOWED):
        raise InvalidURLError("illegal-character")
    if not percent_escapes_are_valid(value):
        raise InvalidURLError("bad-percent-escape")


@dataclass(frozen=True)
class HttpURL:
    """An http or https URL, every component in normal form.

    ``str(url)`` gives the same text as ``normalize``. ``userinfo``, ``query`` and
    ``fragment`` are None when absent and ``""`` when present but empty. ``port`` is
    None when it is absent, empty or the default for the scheme. An IPv6 ``host`` is
    written without brackets.
    """

    scheme: Scheme
    userinfo: str | None
    host: str
    host_kind: HostKind
    port: int | None
    path: str
    query: str | None
    fragment: str | None

    @property
    def effective_port(self) -> int:
        """The port a client connects to: ``port``, or 80 / 443 when it is None."""
        return self.port if self.port is not None else _DEFAULT_PORT[self.scheme]

    def __str__(self) -> str:
        host = f"[{self.host}]" if self.host_kind == "ipv6" else self.host
        userinfo = "" if self.userinfo is None else f"{self.userinfo}@"
        port = "" if self.port is None else f":{self.port}"
        query = "" if self.query is None else f"?{self.query}"
        fragment = "" if self.fragment is None else f"#{self.fragment}"
        return f"{self.scheme}://{userinfo}{host}{port}{self.path}{query}{fragment}"


def parse_http_url(value: str, *, allow_userinfo: bool = True) -> HttpURL:
    """Parse ``value`` as an http or https URL, or raise ``InvalidURLError``.

    The check follows the RFC 3986 grammar and RFC 9110, with no network access. It
    also refuses ports above 65535, IPvFuture literals, host escapes that do not stand
    for unreserved characters, and hosts that end in a number without being a
    dotted-decimal IPv4 address. Raises ``TypeError`` when ``value`` is not a ``str``.
    With ``allow_userinfo=False`` a URL carrying ``user@`` or ``user:password@`` is
    refused, as RFC 9110 section 4.2.4 recommends for untrusted input.
    """
    if not isinstance(value, str):
        raise TypeError(f"expected str, got {type(value).__name__}")
    check_characters(value)
    parts = split_reference(value)
    scheme = (parts.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise InvalidURLError("unsupported-scheme")
    if parts.authority is None:
        raise InvalidURLError("missing-authority")
    userinfo, at, hostport = parts.authority.rpartition("@")
    if at and not only(userinfo, USERINFO):
        raise InvalidURLError("bad-userinfo")
    if at and not allow_userinfo:
        raise InvalidURLError("userinfo-not-allowed")
    host_text, port_text = _split_port(hostport)
    host, kind = canonical_host(host_text)
    port = _port(port_text, scheme)
    if not only(parts.path, PATH):
        raise InvalidURLError("bad-path")
    if parts.query is not None and not only(parts.query, QUERY):
        raise InvalidURLError("bad-query")
    if parts.fragment is not None and not only(parts.fragment, QUERY):
        raise InvalidURLError("bad-fragment")
    return HttpURL(
        scheme="https" if scheme == "https" else "http",
        userinfo=normalize_percent(userinfo) if at else None,
        host=host,
        host_kind=kind,
        port=port,
        path=remove_dot_segments(normalize_percent(parts.path)) or "/",
        query=None if parts.query is None else normalize_percent(parts.query),
        fragment=None if parts.fragment is None else normalize_percent(parts.fragment),
    )


def _split_port(hostport: str) -> tuple[str, str | None]:
    if hostport.startswith("["):
        end = hostport.find("]")
        if end == -1:
            return hostport, None
        rest = hostport[end + 1 :]
        if rest and not rest.startswith(":"):
            raise InvalidURLError("bad-host")
        return hostport[: end + 1], rest[1:] if rest else None
    host, colon, port = hostport.partition(":")
    return host, port if colon else None


def _port(text: str | None, scheme: str) -> int | None:
    if not text:
        return None
    if not text.isdigit():
        raise InvalidURLError("bad-port")
    number = int(text)
    if number > 65535:
        raise InvalidURLError("port-out-of-range")
    return None if number == _DEFAULT_PORT[scheme] else number
