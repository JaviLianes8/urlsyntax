"""The parser against an independent oracle built from the RFC 3986 ABNF.

The regular expression below was translated by hand from RFC 3986 Appendix A (and the
non-empty host rule of RFC 9110 section 4.2.1). It shares no code with the library.
"""

from __future__ import annotations

import random
import re

from urlsyntax import InvalidURLError, parse_http_url

UNRES = r"[A-Za-z0-9\-._~]"
PCT = r"%[0-9A-Fa-f]{2}"
SUB = r"[!$&'()*+,;=]"
H16 = r"[0-9A-Fa-f]{1,4}"
DEC = r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])"
IPV4 = rf"{DEC}\.{DEC}\.{DEC}\.{DEC}"
LS32 = rf"(?:{H16}:{H16}|{IPV4})"


def _rep(n: int) -> str:
    return rf"(?:{H16}:){{{n}}}"


def _head(n: int) -> str:
    return rf"(?:(?:{H16}:){{0,{n}}}{H16})?"


IPV6 = "|".join(
    [
        rf"{_rep(6)}{LS32}",
        rf"::{_rep(5)}{LS32}",
        rf"(?:{H16})?::{_rep(4)}{LS32}",
        rf"{_head(1)}::{_rep(3)}{LS32}",
        rf"{_head(2)}::{_rep(2)}{LS32}",
        rf"{_head(3)}::{H16}:{LS32}",
        rf"{_head(4)}::{LS32}",
        rf"{_head(5)}::{H16}",
        rf"{_head(6)}::",
    ]
)
IPVFUTURE = rf"[vV][0-9A-Fa-f]+\.(?:{UNRES}|{SUB}|:)+"
HOST = rf"(?:\[(?:{IPV6}|{IPVFUTURE})\]|{IPV4}|(?:{UNRES}|{PCT}|{SUB})+)"
USERINFO = rf"(?:{UNRES}|{PCT}|{SUB}|:)*"
PCHAR = rf"(?:{UNRES}|{PCT}|{SUB}|[:@])"
ORACLE = re.compile(
    rf"[hH][tT][tT][pP][sS]?://(?:{USERINFO}@)?{HOST}(?::[0-9]*)?"
    rf"(?:/{PCHAR}*)*(?:\?(?:{PCHAR}|[/?])*)?(?:#(?:{PCHAR}|[/?])*)?"
)

# Reasons for refusing an RFC-valid URL, each a documented browser-agreement rule.
STRICTER = {"port-out-of-range", "unsupported-ip-literal", "host-escape", "ambiguous-ipv4"}

ATOMS = [*list("aZ09-._~!$&'()*+,;=:@/?#[] "), "%41", "%2F", "%2e", "%C3%BC", "%zz", "%", "é"]


def _text(rng: random.Random, atoms: list[str], most: int) -> str:
    return "".join(rng.choice(atoms) for _ in range(rng.randrange(most + 1)))


def _host(rng: random.Random) -> str:
    kind = rng.randrange(6)
    if kind == 0:
        return _text(rng, ATOMS, 6)
    if kind == 1:
        return ".".join(str(rng.choice([0, 1, 9, 10, 255, 256, 99, 7])) for _ in range(4))
    if kind == 2:
        return ".".join(rng.choice(["1", "0x1f", "08", "a", "", "0X", "255"]) for _ in range(3))
    if kind == 3:
        inner = _text(rng, [*list("0123:abf.:"), "::"], 14)
        return f"[{inner}]"
    if kind == 4:
        return rng.choice(["[v1.x]", "[V1f.a:b]", "[v.x]", "[vg.x]", "[::1]", "[::ffff:1.2.3.4]"])
    return _text(rng, [*list("abc.-_~"), "%41", "%7E", "%20", "%2E"], 8)


def _url(rng: random.Random) -> str:
    scheme = rng.choice(["http", "HTTPS", "https", "hTtP", "ftp", "http"])
    sep = rng.choice(["://", "://", "://", ":/", ":"])
    userinfo = _text(rng, ATOMS, 4) + "@" if rng.random() < 0.3 else ""
    port = ":" + rng.choice(["", "80", "0080", "65535", "65536", "99999", "8x", "1:2"])
    port = port if rng.random() < 0.4 else ""
    path = "".join("/" + _text(rng, ATOMS, 4) for _ in range(rng.randrange(3)))
    query = "?" + _text(rng, ATOMS, 5) if rng.random() < 0.3 else ""
    fragment = "#" + _text(rng, ATOMS, 5) if rng.random() < 0.3 else ""
    return f"{scheme}{sep}{userinfo}{_host(rng)}{port}{path}{query}{fragment}"


def test_the_parser_matches_the_grammar_oracle() -> None:
    rng = random.Random(9110)
    tally = {"both": 0, "neither": 0, **dict.fromkeys(STRICTER, 0)}
    for _ in range(30000):
        url = _url(rng)
        valid = ORACLE.fullmatch(url) is not None
        try:
            parse_http_url(url)
        except InvalidURLError as error:
            if valid:
                assert error.reason in STRICTER, (url, error.reason)
                tally[error.reason] += 1
            else:
                tally["neither"] += 1
            continue
        assert valid, url
        tally["both"] += 1
    # Every branch must be exercised often enough to mean something.
    assert all(count >= 50 for count in tally.values()), tally
