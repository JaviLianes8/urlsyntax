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


@pytest.mark.parametrize(
    ("reference", "reason"),
    [
        ("mailto:x@y", "unsupported-scheme"),
        ("http:g", "missing-authority"),
        ("//", "empty-host"),
        ("a b", "illegal-character"),
        ("%zz", "bad-percent-escape"),
        ("[x]", "bad-path"),
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
