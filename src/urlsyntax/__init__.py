"""Syntax-only HTTP and HTTPS URL validation and safe normalization."""

from __future__ import annotations

from ._normalize import normalize
from ._validate import is_valid_http_url

__version__ = "0.1.0"

__all__ = ["is_valid_http_url", "normalize"]
