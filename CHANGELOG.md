# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release.
- `is_valid_http_url`: syntax-only validation of http and https URLs. ASCII and
  percent-escape checks, scheme and host requirements, port range. No network, no DNS.
- `normalize`: safe, semantics-preserving normalization. Lower-cases scheme and host,
  drops the default port, resolves dot-segments, turns an empty path into `/`, drops an
  empty query or fragment, and canonicalizes percent escapes. Idempotent. Raises
  `ValueError` for input that is not a valid http or https URL.
