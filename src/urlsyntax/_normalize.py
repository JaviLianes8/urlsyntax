"""Safe, semantics-preserving normalization of HTTP and HTTPS URLs."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from ._chars import normalize_percent
from ._netloc import split_authority
from ._validate import is_valid_http_url

_DEFAULT_PORT = {"http": "80", "https": "443"}


def normalize(value: str) -> str:
    """Return a canonical form of ``value`` without changing what it addresses.

    Applied: lower-case scheme and host, drop the default port (80 for http,
    443 for https), resolve ``.`` and ``..`` path segments, turn an empty path
    into ``/``, drop an empty query or fragment, and canonicalize percent
    escapes (upper-case hex, decode unreserved octets). Left untouched on
    purpose: userinfo case, the order of query parameters, and any trailing
    slash on a non-empty path. Raises ``ValueError`` for anything that is not a
    valid http or https URL.
    """
    if not is_valid_http_url(value):
        raise ValueError("not a valid http or https URL")

    parts = urlsplit(value)
    scheme = parts.scheme.lower()
    netloc = _normalize_authority(parts.netloc, scheme)
    path = _remove_dot_segments(normalize_percent(parts.path)) or "/"
    query = normalize_percent(parts.query)
    fragment = normalize_percent(parts.fragment)
    return urlunsplit((scheme, netloc, path, query, fragment))


def _normalize_authority(netloc: str, scheme: str) -> str:
    userinfo, host, port = split_authority(netloc)
    userinfo = normalize_percent(userinfo)
    host = normalize_percent(host).lower()
    if port:
        port = str(int(port))
        if port == _DEFAULT_PORT[scheme]:
            port = ""
    prefix = f"{userinfo}@" if userinfo else ""
    suffix = f":{port}" if port else ""
    return f"{prefix}{host}{suffix}"


def _remove_dot_segments(path: str) -> str:
    """Resolve ``.`` and ``..`` segments per RFC 3986 section 5.2.4."""
    output = ""
    while path:
        if path.startswith("../"):
            path = path[3:]
        elif path.startswith("./"):
            path = path[2:]
        elif path.startswith("/./"):
            path = "/" + path[3:]
        elif path == "/.":
            path = "/"
        elif path.startswith("/../"):
            path = "/" + path[4:]
            output = output[: output.rfind("/")] if "/" in output else ""
        elif path == "/..":
            path = "/"
            output = output[: output.rfind("/")] if "/" in output else ""
        elif path in (".", ".."):
            path = ""
        else:
            cut = path.find("/", 1) if path.startswith("/") else path.find("/")
            if cut == -1:
                output += path
                path = ""
            else:
                output += path[:cut]
                path = path[cut:]
    return output
