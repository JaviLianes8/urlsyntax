"""IPv6 literals: parsed by the RFC 3986 grammar, written in RFC 5952 canonical form."""

from __future__ import annotations

import string

_HEX = frozenset(string.hexdigits)


def is_dec_octet(text: str) -> bool:
    """True for an RFC 3986 ``dec-octet``: 0 to 255 in decimal, no leading zero."""
    if not text or len(text) > 3 or not all(c in string.digits for c in text):
        return False
    if len(text) > 1 and text[0] == "0":
        return False
    return int(text) <= 255


def is_dotted_ipv4(text: str) -> bool:
    """True for an RFC 3986 ``IPv4address``: four dotted ``dec-octet`` parts."""
    parts = text.split(".")
    return len(parts) == 4 and all(is_dec_octet(p) for p in parts)


def _h16(text: str) -> int | None:
    if not 1 <= len(text) <= 4 or not all(c in _HEX for c in text):
        return None
    return int(text, 16)


def _pieces(parts: list[str], last_may_be_ipv4: bool) -> list[int] | None:
    out: list[int] = []
    for index, part in enumerate(parts):
        if last_may_be_ipv4 and index == len(parts) - 1 and "." in part:
            if not is_dotted_ipv4(part):
                return None
            a, b, c, d = (int(x) for x in part.split("."))
            out += [(a << 8) | b, (c << 8) | d]
            continue
        value = _h16(part)
        if value is None:
            return None
        out.append(value)
    return out


def parse_ipv6(text: str) -> tuple[int, ...] | None:
    """Return the eight 16-bit pieces of an RFC 3986 ``IPv6address``, or None.

    Zone identifiers are not part of that grammar and are refused.
    """
    if text.count("::") > 1:
        return None
    if "::" in text:
        head_text, tail_text = text.split("::")
        head = _pieces(head_text.split(":"), False) if head_text else []
        tail = _pieces(tail_text.split(":"), True) if tail_text else []
        # "::" stands for at least one zero piece.
        if head is None or tail is None or len(head) + len(tail) > 7:
            return None
        return (*head, *([0] * (8 - len(head) - len(tail))), *tail)
    pieces = _pieces(text.split(":"), True)
    if pieces is None or len(pieces) != 8:
        return None
    return tuple(pieces)


def format_ipv6(pieces: tuple[int, ...]) -> str:
    """Write eight pieces as RFC 5952 section 4 text, entirely in hexadecimal."""
    best_start, best_len = -1, 1
    run_start, run_len = -1, 0
    for index, piece in enumerate(pieces):
        if piece == 0:
            if run_len == 0:
                run_start = index
            run_len += 1
            if run_len > best_len:
                best_start, best_len = run_start, run_len
        else:
            run_len = 0
    words = [format(p, "x") for p in pieces]
    if best_start == -1:
        return ":".join(words)
    head = ":".join(words[:best_start])
    tail = ":".join(words[best_start + best_len :])
    return f"{head}::{tail}"
