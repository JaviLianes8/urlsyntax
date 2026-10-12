"""Dot-segment removal from RFC 3986 section 5.2.4."""

from __future__ import annotations


def remove_dot_segments(path: str) -> str:
    """Resolve ``.`` and ``..`` complete path segments, step by step as in the RFC."""
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
