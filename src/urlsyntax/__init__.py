"""Syntax-only http and https URL operations.

``Scheme``, ``HostKind`` and ``Reason`` are Literal type aliases, not constructors.

>>> from typing import get_args
>>> get_args(Scheme)
('http', 'https')
>>> get_args(HostKind)
('name', 'ipv4', 'ipv6')
>>> 'bad-host' in get_args(Reason)
True
"""

from __future__ import annotations

from ._errors import InvalidURLError, Reason
from ._host import HostKind
from ._normalize import normalize
from ._parse import HttpURL, Scheme, parse_http_url
from ._resolve import resolve
from ._validate import is_valid_http_url

__version__ = "1.0.0"

del annotations

__all__ = [
    "HostKind",
    "HttpURL",
    "InvalidURLError",
    "Reason",
    "Scheme",
    "is_valid_http_url",
    "normalize",
    "parse_http_url",
    "resolve",
]
