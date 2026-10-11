"""Syntax-only validation of HTTP and HTTPS URLs."""

from __future__ import annotations

from urllib.parse import urlsplit

from ._chars import has_only_allowed_chars, percent_escapes_are_valid
from ._netloc import host_is_valid, port_is_valid, split_authority

_SCHEMES = frozenset({"http", "https"})


def is_valid_http_url(value: str) -> bool:
    """Return whether ``value`` is a syntactically valid http or https URL.

    The check is purely textual: no name resolution, no network, no DNS. The
    input must already be a valid URI string, so every character is ASCII and
    every ``%`` introduces a two-digit escape. A reg-name host is accepted on
    its syntax alone, without DNS label rules or a trailing-dot check.
    """
    if not isinstance(value, str):
        return False
    if not value or not has_only_allowed_chars(value) or not percent_escapes_are_valid(value):
        return False

    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    if parts.scheme.lower() not in _SCHEMES:
        return False

    authority = split_authority(parts.netloc)
    return host_is_valid(authority.host) and port_is_valid(authority.port)
