"""remove_dot_segments against a literal transcription of RFC 3986 section 5.2.4."""

from __future__ import annotations

import random
import time

from urlsyntax import is_valid_http_url, normalize, resolve
from urlsyntax._dots import remove_dot_segments


def _reference(path: str) -> str:
    # Written by hand, step for step from the two-buffer method of section 5.2.4.
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
        elif path.startswith("/../") or path == "/..":
            path = "/" + path[4:]
            output = output[: output.rfind("/")] if "/" in output else ""
        elif path in (".", ".."):
            path = ""
        else:
            cut = path.find("/", 1) if path.startswith("/") else path.find("/")
            cut = len(path) if cut == -1 else cut
            output, path = output + path[:cut], path[cut:]
    return output


def test_matches_the_two_buffer_method_on_generated_paths() -> None:
    rng = random.Random(5204)
    atoms = ["/", ".", "..", "a", "b.", ".c", "/./", "/../", "../", "./", "//"]
    for _ in range(20000):
        path = "".join(rng.choice(atoms) for _ in range(rng.randrange(9)))
        assert remove_dot_segments(path) == _reference(path), path


def test_long_paths_take_linear_time() -> None:
    # A quadratic walk needs minutes for these; a linear one well under a second each.
    n = 200_000
    started = time.perf_counter()
    assert normalize("http://h" + "/a" * n + "/.." * n) == "http://h/"
    assert normalize("http://h" + "/." * n + "/") == "http://h/"
    assert resolve("http://h/" + "a/" * n, "../" * n + "g") == "http://h/g"
    assert is_valid_http_url("http://h/" + "%41" * n)
    assert time.perf_counter() - started < 10
