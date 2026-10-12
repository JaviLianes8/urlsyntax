"""Dot-segment removal from RFC 3986 section 5.2.4."""

from __future__ import annotations


def remove_dot_segments(path: str) -> str:
    """Resolve ``.`` and ``..`` complete path segments as section 5.2.4 describes.

    Follows the steps of the RFC, but walks the input with an index and keeps the
    output as a list of segments, so the time stays linear in the length of the path.
    """
    out: list[str] = []
    i = 0
    n = len(path)
    while i < n:
        if path.startswith("../", i):
            i += 3
        elif path.startswith("./", i) or path.startswith("/./", i):
            i += 2
        elif i + 2 == n and path.endswith("/."):
            out.append("/")
            i = n
        elif path.startswith("/../", i):
            i += 3
            if out:
                out.pop()
        elif i + 3 == n and path.endswith("/.."):
            if out:
                out.pop()
            out.append("/")
            i = n
        elif path.startswith(".", i) and (i + 1 == n or (i + 2 == n and path[i + 1] == ".")):
            i = n
        else:
            cut = path.find("/", i + 1 if path[i] == "/" else i)
            end = n if cut == -1 else cut
            out.append(path[i:end])
            i = end
    return "".join(out)
