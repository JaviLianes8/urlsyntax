# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  (`http://2001::1`), and IPv6 zone identifiers.
- Hosts are refused when browsers would refuse them or read them as another address:
  `IPvFuture` literals, host escapes that do not stand for unreserved characters, and hosts
  ending in a number that are not dotted-decimal IPv4 (`127.1`, `0x7f.0.0.1`, `1.2.3.4.`).
- `normalize` keeps an empty `?` and `#`, as RFC 3986 section 6.2.3 requires (it used to
  drop them), writes IPv6 literals in RFC 5952 canonical form, and decodes escapes of
  unreserved characters in the host.
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
