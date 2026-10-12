"""Check a host and write it in normal form."""

from __future__ import annotations

import string
from typing import Literal

from ._chars import REG_NAME, SUB_DELIMS, UNRESERVED, normalize_percent, only
from ._errors import InvalidURLError
from ._ipv6 import format_ipv6, is_dotted_ipv4, parse_ipv6

HostKind = Literal["name", "ipv4", "ipv6"]

_IPVFUTURE_TAIL = UNRESERVED | SUB_DELIMS | frozenset(":")


def canonical_host(host: str) -> tuple[str, HostKind]:
    """Return the host in normal form and what it denotes, or raise ``InvalidURLError``.

    ``host`` is the text between the userinfo and the port; an IPv6 literal keeps its
    brackets on input and loses them on output.
    """
    if not host:
        raise InvalidURLError("empty-host")
    if host.startswith("["):
        return _ip_literal(host), "ipv6"
    if not only(host, REG_NAME):
        raise InvalidURLError("bad-host")
    decoded = normalize_percent(host)
    # Browsers percent-decode the host and reject or remap anything that is not a plain
    # ASCII name, so only escapes of unreserved characters are kept as equivalent.
    if "%" in decoded:
        raise InvalidURLError("host-escape")
    decoded = decoded.lower()
    if _ends_in_a_number(decoded):
        # RFC 3986 section 7.4: "0x7f.1" or "127.1" reach 127.0.0.1 in most resolvers.
        if not is_dotted_ipv4(decoded):
            raise InvalidURLError("ambiguous-ipv4")
        return decoded, "ipv4"
    return decoded, "name"


def _ip_literal(host: str) -> str:
    if not host.endswith("]"):
        raise InvalidURLError("bad-host")
    inner = host[1:-1]
    if _is_ipvfuture(inner):
        raise InvalidURLError("unsupported-ip-literal")
    pieces = parse_ipv6(inner)
    if pieces is None:
        raise InvalidURLError("bad-ipv6")
    return format_ipv6(pieces)


def _is_ipvfuture(text: str) -> bool:
    # IPvFuture = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
    if text[:1] not in ("v", "V"):
        return False
    version, dot, tail = text[1:].partition(".")
    return (
        bool(version and dot and tail)
        and only(version, frozenset(string.hexdigits))
        and only(tail, _IPVFUTURE_TAIL)
    )


def _ends_in_a_number(host: str) -> bool:
    # The WHATWG URL Standard "ends in a number checker".
    parts = host.split(".")
    if parts[-1] == "" and len(parts) > 1:
        parts.pop()
    last = parts[-1]
    if last and only(last, frozenset(string.digits)):
        return True
    return last[:2] == "0x" and only(last[2:], frozenset(string.hexdigits))
