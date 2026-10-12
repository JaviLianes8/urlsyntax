"""Syntax-only validation of http and https URLs."""

from __future__ import annotations

from ._errors import InvalidURLError
from ._parse import parse_http_url


def is_valid_http_url(value: object, *, allow_userinfo: bool = True) -> bool:
    """Return whether ``value`` is a valid http or https URL string.

    Applies exactly the rules of ``parse_http_url``: no name resolution, no network.
    Anything that is not a ``str`` gives False.
    """
    if not isinstance(value, str):
        return False
    try:
        parse_http_url(value, allow_userinfo=allow_userinfo)
    except InvalidURLError:
        return False
    return True
