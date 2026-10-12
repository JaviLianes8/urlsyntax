"""Character sets and percent-encoding helpers from RFC 3986."""

from __future__ import annotations

import string

UNRESERVED = frozenset(string.ascii_letters + string.digits + "-._~")
SUB_DELIMS = frozenset("!$&'()*+,;=")
_GEN_DELIMS = frozenset(":/?#[]@")
_HEX = frozenset(string.hexdigits)

# Every ASCII character that may appear literally somewhere in a URI.
ALLOWED = UNRESERVED | _GEN_DELIMS | SUB_DELIMS | frozenset("%")

# Per-component sets from the RFC 3986 ABNF, with "%" standing for a pct-encoded triplet.
USERINFO = UNRESERVED | SUB_DELIMS | frozenset(":%")
REG_NAME = UNRESERVED | SUB_DELIMS | frozenset("%")
PATH = UNRESERVED | SUB_DELIMS | frozenset(":@/%")
QUERY = PATH | frozenset("?")


def only(text: str, allowed: frozenset[str]) -> bool:
    """True when every character of ``text`` is in ``allowed``."""
    return all(c in allowed for c in text)


def percent_escapes_are_valid(text: str) -> bool:
    """True when every ``%`` is followed by exactly two hexadecimal digits."""
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "%":
            if i + 2 >= n or text[i + 1] not in _HEX or text[i + 2] not in _HEX:
                return False
            i += 3
        else:
            i += 1
    return True


def normalize_percent(text: str) -> str:
    """Upper-case hex in escapes and decode escapes that stand for unreserved bytes.

    Assumes the escapes are already well formed. Decoding an unreserved octet is
    safe because the escaped and literal forms are equivalent in RFC 3986.
    """
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "%":
            hex_pair = text[i + 1 : i + 3].upper()
            decoded = chr(int(hex_pair, 16))
            out.append(decoded if decoded in UNRESERVED else "%" + hex_pair)
            i += 3
        else:
            out.append(text[i])
            i += 1
    return "".join(out)
