# urlsyntax 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. Base: `c4c977c` (0.2.1).
The live PyPI JSON endpoint lists 0.2.1 as the current and only published release.

Progress:
- [x] Inspect base, published release and stable API
- [x] Runnable API examples and safe diagnostics
- [x] Fetch RFCs, WHATWG and pinned browser corpora; verify existing extracts
- [x] Extend contracts, seeded properties and documentation
- [ ] Installed wheel, CLI, upgrade and artifact inspection
- [ ] Available interpreter matrix
- [ ] Mutation round and final gates
- [ ] Independent review and five QA lenses
- [ ] Pull request and final guard
- [ ] Merge and publication

## API review

The nine names, signatures, parameter names and defaults in `__all__` remain stable.
`HttpURL` remains a frozen dataclass with unchecked direct construction; the parser
provides normalized validated fields. Literal aliases remain typing values and have
runnable examples in the package docstring. Error codes are unchanged. CLI diagnostics
now omit invalid inputs and usage arguments; non-string parser errors no longer echo
arbitrary type names. The incidental `annotations` attribute is removed. All changes
are listed in CHANGELOG 1.0.0 and GUIDE.

## Ground truth

Fetched 2026-11-01. `tests/upstream/MANIFEST.json` records URLs, revisions, sizes,
SHA-256 hashes and licenses. `scripts/fetch_upstream.py` reproduces the downloads.
Set `URLSYNTAX_UPSTREAM` to their local directory; absent files skip cleanly and
modified files fail hash checks. Full texts and third-party corpora are not shipped.

- https://www.rfc-editor.org/rfc/rfc3986.txt: grammar, reference resolution and
  normalization. All 42 strict section 5.4 vectors are extracted from the fetched
  text during the test and checked against the existing short fixture values.
- https://www.rfc-editor.org/rfc/rfc9110.txt: HTTP URL requirements and equivalent URLs.
- https://www.rfc-editor.org/rfc/rfc5952.txt: IPv6 canonicalization examples.
- https://url.spec.whatwg.org/: host parsing and ends-in-a-number algorithm.
- The pinned web-platform-tests revision `745b9bf3e485300a83b90c62b310ea02cc84e0d9`:
  `urltestdata.json` and `toascii.json`, downloaded and hash-verified this session.
- Python `ipaddress` and `urllib.parse`, executed locally: 20,000 IPv6 candidates and
  5,000 generated reference-resolution cases over their shared domain. The independent
  hand-translated RFC grammar checks 30,000 generated URLs.

The earlier RFC fixture hashes match the freshly downloaded texts. Tests also confirm
that each existing normalization and IPv6 example occurs in its cited fetched source.
Hand-written browser cases and generated properties are identified as such.

## Verification status

Final results, mutation table and packaging evidence will be recorded after execution.
Independent review, five QA lenses, merge and publication remain pending.
