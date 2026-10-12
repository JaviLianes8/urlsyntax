"""Examples copied by script from RFC 3986 and RFC 9110 (see tests/data/rfc_examples.json)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from urlsyntax import InvalidURLError, normalize, resolve
from urlsyntax._dots import remove_dot_segments

DATA = json.loads((Path(__file__).parent / "data" / "rfc_examples.json").read_text("utf-8"))
BASE: str = DATA["rfc3986_5_4_base"]
RESOLUTION: list[list[str]] = DATA["rfc3986_5_4_resolution"]


def test_the_fixture_holds_every_section_5_4_example() -> None:
    assert BASE == "http://a/b/c/d;p?q"
    assert len(RESOLUTION) == 42


@pytest.mark.parametrize(("reference", "target"), RESOLUTION)
def test_resolve_matches_rfc_3986_section_5_4(reference: str, target: str) -> None:
    if target.startswith("http://"):
        assert resolve(BASE, reference) == target
    else:
        # "g:h" and the strict reading of "http:g" are not http URLs with a host.
        with pytest.raises(InvalidURLError):
            resolve(BASE, reference)


@pytest.mark.parametrize(("path", "expected"), DATA["rfc3986_5_2_4_remove_dot_segments"])
def test_remove_dot_segments_matches_section_5_2_4(path: str, expected: str) -> None:
    assert remove_dot_segments(path) == expected


@pytest.mark.parametrize(("raw", "expected"), DATA["rfc3986_6_2_2_1_case"])
def test_case_normalization_matches_section_6_2_2_1(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


def test_section_6_2_3_equivalent_uris_share_one_normal_form() -> None:
    forms = {normalize(url) for url in DATA["rfc3986_6_2_3_equivalent"]}
    # The RFC names the second URI as the normal form.
    assert forms == {DATA["rfc3986_6_2_3_equivalent"][1]}


def test_an_empty_query_is_not_normalized_away() -> None:
    (url,) = DATA["rfc3986_6_2_3_not_equivalent_to_those"]
    assert normalize(url) == url
    assert normalize(url) not in {normalize(u) for u in DATA["rfc3986_6_2_3_equivalent"]}


def test_rfc_9110_equivalent_uris_share_one_normal_form() -> None:
    forms = {normalize(url) for url in DATA["rfc9110_4_2_3_equivalent"]}
    assert forms == {"http://example.com/~smith/home.html"}
