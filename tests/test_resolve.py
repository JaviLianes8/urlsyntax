import pytest

from urlsyntax import InvalidURLError, resolve

BASE = "http://example.com/a/b?q#f"


@pytest.mark.parametrize(
    ("reference", "target"),
    [
        ("", "http://example.com/a/b?q"),
        ("#g", "http://example.com/a/b?q#g"),
        ("c", "http://example.com/a/c"),
        ("//other.org", "http://other.org"),
        ("//other.org/a/./../b", "http://other.org/b"),
        ("https://x.org/../y", "https://x.org/y"),
        ("HTTP://x.org/p", "HTTP://x.org/p"),
        ("%7e", "http://example.com/a/%7e"),
        ("../../../c?x#y", "http://example.com/c?x#y"),
    ],
)
def test_resolves_references(reference: str, target: str) -> None:
    assert resolve(BASE, reference) == target


def test_merges_with_an_empty_base_path() -> None:
    assert resolve("http://example.com", "c") == "http://example.com/c"


@pytest.mark.parametrize("prefix", ["https:", "http:", ""])
@pytest.mark.parametrize("suffix", ["?x=1#f", "?#f", "?x=1#", "?#", "#f", "?x=1"])
def test_absolute_references_keep_query_and_fragment(prefix: str, suffix: str) -> None:
    expected_scheme = prefix or "http:"
    assert resolve(BASE, prefix + "//other/a/../b" + suffix) == (
        expected_scheme + "//other/b" + suffix
    )


@pytest.mark.parametrize(
    ("reference", "reason"),
    [
        ("mailto:x@y", "unsupported-scheme"),
        ("http:g", "missing-authority"),
        ("//", "empty-host"),
        ("a b", "illegal-character"),
        ("x y/../c", "illegal-character"),
        ("%zz/../c", "bad-percent-escape"),
        ("%zz", "bad-percent-escape"),
        ("[x]", "bad-path"),
        ("[x]/../g", "bad-path"),
        ("a]b/../g", "bad-path"),
        ("g?a[", "bad-query"),
        ("g#a#b", "bad-fragment"),
        ("//0x7f.1/", "ambiguous-ipv4"),
    ],
)
def test_refuses_targets_that_are_not_valid_http_urls(reference: str, reason: str) -> None:
    with pytest.raises(InvalidURLError) as caught:
        resolve(BASE, reference)
    assert caught.value.reason == reason


def test_refuses_an_invalid_base() -> None:
    with pytest.raises(InvalidURLError) as caught:
        resolve("ftp://example.com/", "a")
    assert caught.value.reason == "unsupported-scheme"


def test_refuses_non_string_arguments() -> None:
    with pytest.raises(TypeError):
        resolve(BASE, None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        resolve(None, "a")  # type: ignore[arg-type]


@pytest.mark.parametrize("reference", [":", ":x", "::", ":x/bar", ":x/../ok", ":?q", ":#f"])
def test_relative_first_segment_refuses_literal_colons(reference: str) -> None:
    # Hand-written path-noscheme cases, including a segment removed by resolution.
    with pytest.raises(InvalidURLError) as caught:
        resolve(BASE, reference)
    assert caught.value.reason == "bad-path"


@pytest.mark.parametrize(
    ("reference", "target"),
    [("./:x", "/a/:x"), ("/:x", "/:x"), ("%3Ax", "/a/%3Ax"), ("a/:x", "/a/a/:x")],
)
def test_relative_colons_outside_the_first_segment_are_valid(reference: str, target: str) -> None:
    assert resolve(BASE, reference) == "http://example.com" + target


def test_absolute_reference_still_requires_a_valid_base() -> None:
    with pytest.raises(InvalidURLError) as caught:
        resolve("ftp://a/", "https://b/")
    assert caught.value.reason == "unsupported-scheme"
