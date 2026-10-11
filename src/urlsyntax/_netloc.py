"""Split and inspect the authority component of a URL."""

from __future__ import annotations

import ipaddress
from typing import NamedTuple


class Authority(NamedTuple):
    userinfo: str  # without the trailing "@"
    host: str  # IPv6 literals keep their square brackets
    port: str  # digits only, or "" when absent


def split_authority(netloc: str) -> Authority:
    """Break ``userinfo@host:port`` into its parts without decoding anything."""
    userinfo = ""
    hostport = netloc
    if "@" in hostport:
        userinfo, hostport = hostport.rsplit("@", 1)
    if hostport.startswith("["):
        end = hostport.find("]")
        host = hostport[: end + 1] if end != -1 else hostport
        rest = hostport[end + 1 :] if end != -1 else ""
        port = rest[1:] if rest.startswith(":") else ""
    elif ":" in hostport:
        host, port = hostport.rsplit(":", 1)
    else:
        host, port = hostport, ""
    return Authority(userinfo, host, port)


def host_is_valid(host: str) -> bool:
    """True for a non-empty reg-name or a bracketed IPv6 literal."""
    if not host:
        return False
    if host.startswith("[") and host.endswith("]"):
        try:
            ipaddress.IPv6Address(host[1:-1])
        except ValueError:
            return False
        return True
    return "[" not in host and "]" not in host


def port_is_valid(port: str) -> bool:
    """True when the port is absent or a 16-bit decimal number."""
    if port == "":
        return True
    return port.isdigit() and 0 <= int(port) <= 65535
