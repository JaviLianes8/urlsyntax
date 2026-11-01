# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The nine exported names, parsing and normalization rules, reference resolution,
  immutable `HttpURL` fields and the eighteen `Reason` codes are stable.
- Python 3.10 and later, no runtime dependencies, and inline type information.

### Changed

- CLI invalid-input diagnostics now print only the reason code, without the URL.
  Usage errors print a fixed message without arguments. This avoids exposing secrets
  outside userinfo and bounds diagnostics even for very long or malformed inputs.
- Non-string parser and normalizer arguments now raise `TypeError("value must be str")`
  without echoing the type name, whose length or content is uncontrolled.
- The incidental top-level `annotations` attribute is removed; it was not in `__all__`.

### Fixed

- `resolve` rejects a literal colon in the first segment of a scheme-less relative
  path with `bad-path`, even when dot-segment removal would erase that segment.
  Explicit `./:x`, absolute `/:x`, later-segment colons and encoded `%3Ax` remain valid.
- String subclasses are validated using their stored string contents across parsing,
  validation, normalization and both resolution arguments. Overridden string methods
  can no longer bypass checks or cause undocumented exceptions.
- The CLI stops on stdin decoding failures with status 1 and the fixed diagnostic
  `invalid (stdin-decoding-error)`, without a traceback or input contents.

### Added

- Runnable API examples, a stable-contract guide, freshly verified specification
  fixtures, seeded property tests and installed-wheel upgrade checks from 0.2.1.
- CLI regression contracts require output from valid lines processed before a stdin
  decoding failure to be retained, including a deterministic incremental-input check.
- CLI regression contracts require status 1 after invalid-then-valid arguments or
  stdin in normal and check-only modes, and preserve repeated stdin output and diagnostics.
- CLI regression contracts cover unterminated final stdin lines in normal and check-only
  modes and preserve mixed-case userinfo, path, query and fragment, including installed CLI checks.


## [0.2.1] - 2026-10-13

### Changed

- The web-platform-tests URL corpus is no longer committed or shipped in the sdist: it is
  fetched on demand by `scripts/fetch_upstream.py` at a pinned revision, checked against
  `tests/upstream/MANIFEST.json`, and hand-written browser cases keep the default suite
  meaningful without it.

## [0.2.0] - 2026-10-12

### Added

- `parse_http_url` returns an `HttpURL`: scheme, userinfo, host, host kind (`name`,
  `ipv4`, `ipv6`), port, path, query and fragment, all in normal form, plus
  `effective_port`. `str(url)` equals `normalize`.
- `InvalidURLError`, a `ValueError` with a `reason` code naming the rule that failed, and
  the `Reason`, `HostKind` and `Scheme` types.
- `resolve(base, reference)`: RFC 3986 section 5.2 reference resolution.
- `allow_userinfo=False` on `is_valid_http_url` and `parse_http_url` refuses credentials in
  the URL (RFC 9110 section 4.2.4).
- Command line: `python -m urlsyntax` and the `urlsyntax` script.
- Tests against the RFC 3986 and RFC 9110 examples, the web-platform-tests URL corpus and
  an oracle built from the RFC 3986 grammar.

### Changed

- Every component is checked against its own RFC 3986 rule. Now refused: `[`, `]` and a
  second `#` in the path, query or fragment, `@` in the userinfo, `:` in a host
  (`http://2001::1`), and IPv6 zone identifiers (not part of RFC 3986).
- Hosts are refused when browsers would refuse them or read them as another address:
  `IPvFuture` literals, host escapes that do not stand for unreserved characters, and hosts
  ending in a number that are not dotted-decimal IPv4 (`127.1`, `0x7f.0.0.1`, `1.2.3.4.`).
- `normalize` keeps an empty `?`, `#` and userinfo (`http://@h/` stays as it is), as RFC
  3986 section 6.2.3 requires; it used to drop them, so stored 0.1.0 normal forms of such
  URLs differ. IPv6 literals are written in RFC 5952 section 4 form, all in hexadecimal.
- A port with many leading zeros is read as its number, and a very long port is refused as
  `port-out-of-range`; 0.1.0 raised an internal `ValueError` from `int()` for ports over
  4300 digits.
- Dot-segment removal runs in linear time; 0.1.0 took seconds on paths of a few hundred
  kilobytes.
- `normalize` raises `InvalidURLError` (still a `ValueError`) for invalid input and
  `TypeError` for a non-string. `is_valid_http_url` accepts any object and returns `False`
  for non-strings, as before.

## [0.1.0]

- First release.
- `is_valid_http_url`: syntax-only validation of http and https URLs. ASCII and
  percent-escape checks, scheme and host requirements, port range. No network, no DNS.
- `normalize`: safe, semantics-preserving normalization. Lower-cases scheme and host,
  drops the default port, resolves dot-segments, turns an empty path into `/`, drops an
  empty query or fragment, and canonicalizes percent escapes. Idempotent. Raises
  `ValueError` for input that is not a valid http or https URL.
