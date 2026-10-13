"""Syntax-only http and https URL validation, parsing, normalization and resolution."""

from __future__ import annotations

from ._errors import InvalidURLError, Reason
from ._host import HostKind
from ._normalize import normalize
from ._parse import HttpURL, Scheme, parse_http_url
from ._resolve import resolve
from ._validate import is_valid_http_url

__version__ = "0.2.1"

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
