"""The IPv6 parser follows the RFC 3986 grammar; the writer follows RFC 5952 section 4."""

from __future__ import annotations

import ipaddress
import random

import pytest

from urlsyntax._ipv6 import format_ipv6, is_dec_octet, parse_ipv6

# Quoted from RFC 5952 sections 4.1 to 4.2.3 as fetched from
# https://www.rfc-editor.org/rfc/rfc5952.txt on 2026-10-12.
RFC_5952 = [
    ("2001:0db8::0001", "2001:db8::1"),
    ("2001:db8:0:0:0:0:2:1", "2001:db8::2:1"),
    ("2001:db8::0:1", "2001:db8::1"),
    ("2001:db8:0:1:1:1:1:1", "2001:db8:0:1:1:1:1:1"),
    ("2001:db8:0:0:1:0:0:1", "2001:db8::1:0:0:1"),
]
# Written by hand from the rules of sections 4.2.3 (longest run) and 4.3 (lower case).
HAND_WRITTEN = [
    ("2001:0:0:1:0:0:0:1", "2001:0:0:1::1"),
    ("2001:DB8::ABCD", "2001:db8::abcd"),
]


@pytest.mark.parametrize(("raw", "canonical"), RFC_5952 + HAND_WRITTEN)
def test_rfc_5952_examples(raw: str, canonical: str) -> None:
    pieces = parse_ipv6(raw)
    assert pieces is not None
    assert format_ipv6(pieces) == canonical


@pytest.mark.parametrize(
    "text",
    ["::", "::1", "1::", "1:2:3:4:5:6:7::", "::2:3:4:5:6:7:8", "1:2:3:4:5:6:1.2.3.4", "::1.2.3.4"],
)
def test_accepts_every_rfc_3986_shape(text: str) -> None:
    assert parse_ipv6(text) is not None


@pytest.mark.parametrize(
    "text",
    [
        "",
        ":",
        ":::",
        "1:2:3:4:5:6:7:8:9",
        "1:2:3:4:5:6:7",
        "1:2:3:4:5:6:7:8::",
        "::1:2:3:4:5:6:7:8",
        "1::2::3",
        "12345::",
        "g::",
        "::1.2.3",
        "::1.2.3.04",
        "::256.1.1.1",
        "1.2.3.4::",
        "::1.2.3.4:1",
        "fe80::1%25eth0",
        "fe80::1%eth0",
        ":1::",
        "1::2:",
        "\u0661::",
    ],
)
def test_refuses_what_the_grammar_refuses(text: str) -> None:
    assert parse_ipv6(text) is None


def test_dec_octet_has_no_leading_zero() -> None:
    assert [is_dec_octet(t) for t in ("0", "9", "10", "255", "256", "01", "", "1a")] == [
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
    ]


def _random_candidate(rng: random.Random) -> str:
    if rng.random() < 0.5:
        groups = [format(rng.choice([0, 0, 0, 1, rng.randrange(65536)]), "x") for _ in range(8)]
        if rng.random() < 0.3:
            groups[-2:] = [".".join(str(rng.randrange(260)) for _ in range(4))]
        text = ":".join(groups)
        if rng.random() < 0.6:
            start = rng.randrange(len(text))
            end = rng.randrange(start, len(text) + 1)
            text = text[:start] + "::" + text[end:]
        return text
    return "".join(rng.choice("0123:abf.:") for _ in range(rng.randrange(1, 20)))


def test_agrees_with_the_standard_library_on_generated_addresses() -> None:
    rng = random.Random(3986)
    accepted = 0
    for _ in range(20000):
        text = _random_candidate(rng)
        try:
            expected: ipaddress.IPv6Address | None = ipaddress.IPv6Address(text)
        except ValueError:
            expected = None
        pieces = parse_ipv6(text)
        if expected is None:
            assert pieces is None, text
            continue
        assert pieces is not None, text
        assert int.from_bytes(bytes(b for p in pieces for b in p.to_bytes(2, "big")), "big") == int(
            expected
        )
        assert ipaddress.IPv6Address(format_ipv6(pieces)) == expected
        accepted += 1
    assert accepted > 3000
