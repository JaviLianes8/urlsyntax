"""Reference resolution from RFC 3986 section 5.2."""

from __future__ import annotations

from ._chars import PATH, QUERY, only
from ._dots import remove_dot_segments
from ._errors import InvalidURLError
from ._parse import Parts, check_characters, parse_http_url, split_reference


def resolve(base: str, reference: str) -> str:
    """Resolve ``reference`` against the http or https URL ``base``.

    Runs the strict algorithm of RFC 3986 section 5.2 and returns the target as
    recomposed by section 5.3, not normalized. ``base`` must pass ``parse_http_url``,
    ``reference`` must be URI text, and the target must itself be a valid http or
    https URL, so ``"mailto:x"`` or ``"http:g"`` raise ``InvalidURLError``. An empty
    reference gives the base without its fragment.
    """
    if not isinstance(base, str) or not isinstance(reference, str):
        raise TypeError("base and reference must be str")
    parse_http_url(base)
    if reference:
        check_characters(reference)
    ref = split_reference(reference)
    # Check the reference itself: a segment that ".." removes must still be valid text.
    if not only(ref.path, PATH):
        raise InvalidURLError("bad-path")
    if ref.query is not None and not only(ref.query, QUERY):
        raise InvalidURLError("bad-query")
    if ref.fragment is not None and not only(ref.fragment, QUERY):
        raise InvalidURLError("bad-fragment")
    target = _transform(split_reference(base), ref)
    text = _recompose(target)
    parse_http_url(text)
    return text


def _transform(base: Parts, ref: Parts) -> Parts:
    if ref.scheme is not None:
        return Parts(
            ref.scheme, ref.authority, remove_dot_segments(ref.path), ref.query, ref.fragment
        )
    if ref.authority is not None:
        return Parts(
            base.scheme, ref.authority, remove_dot_segments(ref.path), ref.query, ref.fragment
        )
    if ref.path == "":
        query = ref.query if ref.query is not None else base.query
        return Parts(base.scheme, base.authority, base.path, query, ref.fragment)
    if ref.path.startswith("/"):
        path = remove_dot_segments(ref.path)
    else:
        path = remove_dot_segments(_merge(base, ref.path))
    return Parts(base.scheme, base.authority, path, ref.query, ref.fragment)


def _merge(base: Parts, path: str) -> str:
    if base.authority is not None and base.path == "":
        return "/" + path
    return base.path[: base.path.rfind("/") + 1] + path


def _recompose(parts: Parts) -> str:
    out = ""
    if parts.scheme is not None:
        out += parts.scheme + ":"
    if parts.authority is not None:
        out += "//" + parts.authority
    out += parts.path
    if parts.query is not None:
        out += "?" + parts.query
    if parts.fragment is not None:
        out += "#" + parts.fragment
    return out
