"""Check short existing extracts against specifications fetched in this run."""

from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import read_upstream

from urlsyntax import InvalidURLError, normalize, resolve


def test_resolution_vectors_are_extracted_from_the_live_rfc() -> None:
    text = read_upstream("rfc3986.txt").decode()
    section = text.rsplit("5.4.1.  Normal Examples", 1)[1].split("6.  Normalization", 1)[0]
    pairs = re.findall(r'"([^"\n]*)"\s*=\s*"([^"\n]*)"', section)
    pairs = [pair for pair in pairs if pair != ("http:g", "http://a/b/c/g")]
    data = json.loads((Path(__file__).parent / "data/rfc_examples.json").read_text())
    assert pairs == [tuple(pair) for pair in data["rfc3986_5_4_resolution"]]
    assert len(pairs) == 42
    for reference, expected in pairs:
        try:
            actual = resolve(data["rfc3986_5_4_base"], reference)
        except InvalidURLError:
            assert expected in ("g:h", "http:g")
        else:
            assert actual == expected


def test_other_rfc_extracts_occur_in_the_fetched_texts() -> None:
    data = json.loads((Path(__file__).parent / "data/rfc_examples.json").read_text())
    for name in ("rfc3986", "rfc9110"):
        text = read_upstream(name + ".txt").decode()
        for key, values in data.items():
            if not key.startswith(name) or key.endswith("resolution"):
                continue
            if isinstance(values, str):
                values = [values]
            for value in values:
                for atom in value if isinstance(value, list) else [value]:
                    assert atom in text, (key, atom)


def test_ipv6_examples_are_in_the_fetched_rfc() -> None:
    from test_ipv6 import RFC_5952

    text = read_upstream("rfc5952.txt").decode()
    for raw, expected in RFC_5952:
        assert raw in text and expected in text
        assert normalize("http://[" + raw + "]/") == "http://[" + expected + "]/"


def test_browser_host_rules_have_a_fetched_source() -> None:
    text = read_upstream("whatwg.html").decode()
    assert 'id="ends-in-a-number-checker"' in text
    assert 'id="concept-ipv4-parser"' in text
    assert 'id="concept-host-parser"' in text
