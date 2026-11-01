"""Seeded independent-reference checks and hostile input properties."""

from __future__ import annotations

import random
import time
from urllib.parse import urljoin, urlsplit

import pytest

from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve


@pytest.mark.parametrize("seed", [3986, 9110, 5952])
def test_seeded_parse_normalize_and_validation_properties(seed: int) -> None:
    rng = random.Random(seed)
    atoms = [*"aA09/:?#[]@!$&'()*+,;=._~-% ", "\x00", "\n", "\ud800", "\U0001f600"]
    for _ in range(5000):
        candidate = rng.choice(["", "http://", "https://example.com/"])
        candidate += "".join(rng.choice(atoms) for _ in range(rng.randrange(80)))
        try:
            parsed = parse_http_url(candidate)
        except InvalidURLError as error:
            assert not is_valid_http_url(candidate)
            assert len(str(error)) < 150
        else:
            normal = normalize(candidate)
            assert normal == str(parsed) == normalize(normal)
            assert parse_http_url(normal) == parsed
            assert is_valid_http_url(candidate)


def test_resolution_matches_urllib_on_shared_nonempty_components() -> None:
    rng = random.Random(20261101)
    for _ in range(5000):
        base = "https://example.com/" + "/".join(rng.choices(["a", "b", "c"], k=5))
        ref = "/".join(rng.choices(["d", "e", ".", ".."], k=6)) + "?x=1#f"
        assert resolve(base, ref) == urljoin(base, ref)


def test_readme_comparison_with_urllib_is_observable() -> None:
    parts = urlsplit("HTTP://0x7f.1:80/a/../b")
    assert (parts.hostname, parts.port, parts.path) == ("0x7f.1", 80, "/a/../b")
    assert not is_valid_http_url(parts.geturl())


@pytest.mark.parametrize("shape", ["dots", "escape", "port", "host", "ipv6", "query"])
def test_long_input_is_bounded_or_scales_linearly(shape: str) -> None:
    timings = []
    for size in (20000, 80000):
        candidate = {
            "dots": "http://a/" + "x/../" * size,
            "escape": "http://a/" + "%41" * size,
            "port": "http://a:" + "0" * size + "80",
            "host": "http://" + "a." * size + "com/",
            "ipv6": "http://[" + "1:" * size + "]",
            "query": "http://a/?" + "x&" * size,
        }[shape]
        start = time.perf_counter()
        for _ in range(3):
            try:
                normal = normalize(candidate)
            except InvalidURLError as error:
                assert len(str(error)) < 150
            else:
                assert normalize(normal) == normal
        timings.append(time.perf_counter() - start)
    assert timings[1] < timings[0] * 12 + 0.3, (shape, timings)
