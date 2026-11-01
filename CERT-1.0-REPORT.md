# urlsyntax 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. Base: `c4c977c` (0.2.1).
The live PyPI JSON endpoint lists 0.2.1 as the current and only published release.

Progress:
- [x] Inspect base, published release and stable API
- [x] Runnable API examples and safe diagnostics
- [x] Fetch RFCs, WHATWG and pinned browser corpora; verify existing extracts
- [x] Extend contracts, seeded properties and documentation
- [x] Installed wheel, CLI, upgrade and artifact inspection
- [x] Available interpreter matrix
- [x] Mutation round and final gates
- [ ] Independent review and five QA lenses
- [x] Pull request #4 and guard CLEAN
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

## Scorecard

| Item | Result and evidence |
| --- | --- |
| 1. Stable API | PASS: nine exports, signatures/defaults/fields pinned, changes documented |
| 2. Exact exports | PASS: `__all__` and every non-private package attribute checked |
| 3. Runnable docstrings | PASS: 16 doctest examples; README and GUIDE output executed |
| 4. Typing | PASS: `mypy --strict src tests`; external consumer typing from installed wheel; `py.typed` |
| 5. Safe typed errors | PASS: all eighteen reasons reached; fixed bounded messages; CLI omits invalid inputs |
| 6. Complete contracts | PASS: constructors, fields, aliases, signatures, errors, CLI and boundary contracts |
| 7. Ground truth | PASS: live specifications, WPT and standard-library references described above |
| 8. Wheel and upgrade | PASS: isolated install, CLI subprocesses, live PyPI 0.2.1 upgrade |
| 9. Properties | PASS: 70,000 seeded grammar, IPv6, parse and resolution candidates; six scaling shapes |
| 10. Available Pythons | PASS: CPython 3.11.11 and 3.14.6; unavailable versions listed below |
| 11. README | PASS: executed examples, verified comparison, absolute links and strict twine check |
| 12. CHANGELOG | PASS: dated 2026-11-01, stable API and every change from 0.2.1 |
| 13. Metadata | PASS: 1.0.0, Production/Stable, MIT, Python >=3.10, URLs, no runtime requirements |
| 14. Archives | PASS: wheel and sdist lists inspected, LICENSE and typing marker included |
| 15. Gates | PASS: format, lint, strict source typing and pytest, each exits zero |
| 16. Independent reviewer | PENDING |
| 17. Merge and publication | PENDING; PR #4 open from `release/1.0.0`, guard CLEAN |
| 18. Mutation round | PASS: twenty deliberate bugs caught after two missing contracts were added |
| 19. Five QA lenses | Round 1 fixes and rounds 2-4 CLI coverage fixes below; independent approval pending |

## Packaging, compatibility and interpreter coverage

The live https://pypi.org/pypi/urlsyntax/json response was fetched on 2026-11-01.
Installing `urlsyntax==0.2.1` from PyPI confirmed its source matches `main` exactly.
A seed-20261101 differential check compared 5,003 candidates across both validator
options, parsing, normalization and resolution: 25,015 calls, no differing results
or error families. `HttpURL` and `InvalidURLError` pickles work in both directions
between the installed 0.2.1 release and the installed 1.0.0 wheel.

`URLSYNTAX_E2E=1 URLSYNTAX_E2E_PYPI=1`: both packaging tests pass. They build the
wheel, install 0.2.1 into a new venv, exercise it, upgrade in place to the wheel and
exercise the external consumer again using `-I` from an empty directory. Subprocess
checks cover the console script and module entry point, stdin, empty lines, mixed
valid/invalid arguments, userinfo policy, check-only mode, help and usage errors.
The documented old and new invalid-input stderr formats are asserted separately.

A separate sdist build produced the wheel from that sdist. Both archives passed
`twine check --strict`. The wheel contains twelve Python modules, `py.typed`, entry
point and distribution metadata, and the MIT LICENSE. The sdist contains source,
intentional contract tests, short RFC example values, the metadata-only upstream
manifest, fetch script, README, GUIDE, CHANGELOG and LICENSE. No caches, downloaded
corpora, full specifications, scratch files or release report are distributed.
Metadata was inspected directly for version, minimum Python, stable classifier,
license, required URLs and optional-only development dependencies.

The sdist was unpacked, its `src` directory moved outside the test tree, and its
suite run against the wheel installed into fresh venvs:

| Interpreter | Origin | Installed suite |
| --- | --- | --- |
| CPython 3.14.6 | System Python | 362 passed, 2 opt-in packaging tests skipped |
| CPython 3.11.11 | Blender 4.5 bundled Python | 362 passed, 2 opt-in packaging tests skipped |

The Python launcher lists additional 3.10 through 3.14/free-threaded installations,
but every corresponding executable path is absent. All six local versioned Python
shims fail because their target is missing. Existing application venvs use the same
3.14.6 base. Python 3.10, 3.12, 3.13 and free-threaded 3.14 were therefore unavailable
and are not claimed as runtime-tested here. The minimum-version syntax/type target
remains 3.10.

Without downloaded sources the suite reports 353 passed, 11 skipped (nine upstream
checks and two opt-in packaging checks). The fetch script successfully re-fetches all
six manifest entries. A deliberately changed RFC file is rejected by its manifest
check. Every pytest run uses a scratch basetemp and a 300-second per-test timeout.

## Mutation round

Each mutation was applied alone in a private source copy, with bytecode writing
disabled, and the contract suite run with `-x` and a 300-second test/process limit.
The original source was restored after each run. Eighteen were caught immediately;
M01 and M14 survived, so exact port-boundary and absolute-reference component contracts
were added. Both then failed on those contracts. No survivor remains. The untouched
suite passed before the round and the expanded installed suite passed afterward.

| ID | Mutation | Caught by |
| --- | --- | --- |
| M01 | reject maximum port | `test_parse.py::test_port_boundaries_are_inclusive` |
| M02 | wrong HTTP default port | `test_browser_cases.py::test_normal_form_matches_the_browser_href` |
| M03 | ignore no-userinfo policy | `test_cli.py::test_no_userinfo_refuses_credentials` |
| M04 | drop query | `test_browser_cases.py::test_normal_form_matches_the_browser_href` |
| M05 | drop fragment | `test_contract_stable.py::test_guide_examples_run` |
| M06 | wrong non-string error type | `test_contract_stable.py::test_non_string_errors_do_not_quote_arbitrary_type_names` |
| M07 | retain host case | `test_browser_cases.py::test_normal_form_matches_the_browser_href` |
| M08 | accept ambiguous IPv4 | `test_browser_cases.py::test_inputs_the_browser_refuses_are_refused` |
| M09 | decode reserved escapes | `test_browser_cases.py::test_inputs_the_browser_refuses_are_refused` |
| M10 | accept invalid second hex digit | `test_grammar_oracle.py::test_the_parser_matches_the_grammar_oracle` |
| M11 | compress last tied zero run | `test_fetched_specs.py::test_ipv6_examples_are_in_the_fetched_rfc` |
| M12 | allow zero-width compression | `test_ipv6.py::test_refuses_what_the_grammar_refuses` |
| M13 | lose inherited query | `test_fetched_specs.py::test_resolution_vectors_are_extracted_from_the_live_rfc` |
| M14 | swap resolved query and fragment | `test_resolve.py::test_absolute_references_keep_query_and_fragment` |
| M15 | accept non-string input | `test_contract_stable.py::test_public_docstrings_and_alias_examples_run` |
| M16 | invalid CLI input exits zero | `test_cli.py::test_reports_invalid_urls_and_exits_one` |
| M17 | echo invalid CLI input | `test_cli.py::test_reports_invalid_urls_and_exits_one` |
| M18 | treat explicit port zero as absent | `test_contract_stable.py::test_value_constructor_hash_copy_and_pickle` |
| M19 | retain parent directory | `test_browser_cases.py::test_normal_form_matches_the_browser_href` |
| M20 | skip normalization | `test_browser_cases.py::test_normal_form_matches_the_browser_href` |

## Gates and remaining stages

The four gates run independently: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `pytest`. The additional `mypy --strict src tests` check passes.
The full final run enables fetched sources, wheel builds and the PyPI upgrade test:
364 passed, no skips, in 39.23 seconds on CPython 3.14.6.

PR: https://github.com/JaviLianes8/urlsyntax/pull/4, from `release/1.0.0` to `main`.
Guard result: `CLEAN: urlsyntax #4`.

Independent review and final QA approval remain pending. Merge and PyPI publication
are outside this preparation stage.

## QA lenses: round 1 fixes

Reviewed base: `51a356e8e3bc00786b77de7ba8a5adcb14662f8c`, dated 2026-11-01.
Fix commit: `37bddaa02d35687e1e4fba0343badd92eef7a813`.
All eight reported findings are addressed; none is disputed. The original FAIL
verdicts remain pending independent re-verification. Lens D's verdict is not recorded here.

| Finding | Change and contract |
| --- | --- |
| A-01, B-01 | Reject literal colons in the first relative-path segment with `bad-path` before dot removal; seven negative cases and four valid colon forms in `test_resolve.py` |
| C-01 | Use built-in string contents before parsing or resolving; overridden indexing, iteration, length, truth testing and string conversion covered in `test_string_subclasses.py` |
| C-02 | Stop on stdin decoding failure with status 1 and a fixed diagnostic; strict UTF-8 subprocess tests cover malformed and mixed input, including `--check` |
| E-001 | Parser, validator and CLI contracts reject an empty userinfo delimiter when userinfo is disabled |
| E-002 | An invalid base is rejected even when a valid absolute reference replaces it |
| E-003 | CLI subprocess contracts reject leading/trailing spaces and tabs on stdin |
| E-004 | Inequality is checked independently for all eight stored `HttpURL` fields |

Before implementation, the focused contract run failed 19 cases and passed 91.
After the fixes it passed all 110; mixed-input and separate validator checks were
then added. The browser corpus now explicitly checks eight RFC-invalid colon-leading
references and retains 26 valid resolution comparisons. GUIDE and CHANGELOG describe
all three behavior corrections; public names, signatures and URL reason codes are unchanged.

The four surviving lens E mutations were reapplied individually in a scratch copy:
M16 failed all three empty-userinfo contracts, M34 failed the absolute-reference/base
contract, M42 failed all four whitespace cases, and M45 failed the host-kind case
while the other seven field cases passed. Each mutation was restored after its run.

Final verification: `ruff format --check .`, `ruff check .`, `mypy --strict src`,
and `pytest` each exit 0; `mypy --strict src tests` also passes. The full suite reports
416 passed, no skips, with fetched fixtures, installed-wheel checks and the PyPI 0.2.1
upgrade enabled. Every test uses a 300-second timeout and scratch basetemp.

## QA lenses: round 2 fixes

Reviewed base: `f7f438983aba2f22188c76813b3252a5a4513f9a`, dated 2026-11-01.
Fix commit: `2d6b2b3c4a3e1865c5d21ac18db798bc8d4c127f`.
The one reported finding, E-005 from lens E, is addressed; none is disputed.
Independent re-verification remains pending.

E-005 identified a missing CLI contract: eager stdin consumption could discard all
valid output before a decoding failure while the existing suite still passed.
Production behavior already satisfies the contract, so no source or API changes
were required. CHANGELOG records the additional regression coverage.

- `test_stdin_decoding_failure_retains_output_for_preceding_lines` supplies two
  valid lines through a controlled iterator, then raises `UnicodeDecodeError`.
  It asserts both complete normalized output lines, status 1 and the fixed stderr
  diagnostic, independently of decoder read-ahead.
- The existing strict UTF-8 subprocess test now supplies 2,000 valid lines before
  malformed input and requires a nonempty valid output prefix. Its check-only and
  malformed-first-input cases continue to require empty stdout.
- N20 (`urls = list(urls)` before the processing loop) was applied alone in a
  scratch source copy. Both contracts failed because stdout was empty: 2 failed,
  17 passed. The copied source was restored after the run.

Final verification on the unchanged production implementation: 417 passed, no
skips, with fetched fixtures, installed-wheel checks and the PyPI 0.2.1 upgrade
enabled. `ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`
each exit 0; `mypy --strict src tests` also passes. Every test uses a 300-second
timeout and scratch basetemp.

## QA lenses: round 3 fixes

Reviewed base: `88999dc4f5c67ee861565bda18e49b96efc6c2c1`, dated 2026-11-01.
Fix commit: `17aaec8738186cc2b3cc46c1bde1ae1ebafa4281`.
Both reported findings, E-006 and E-007 from lens E, are addressed; none is disputed.
Independent re-verification remains pending.

These findings identify missing contracts. The current implementation already
satisfies both behaviors, so production code and the public API are unchanged.
CHANGELOG records the additional coverage in `tests/test_cli.py`:

- E-006: `test_valid_url_after_invalid_url_retains_failure_status` requires status
  1 after an invalid URL followed by a valid URL, for arguments and stdin in normal
  and check-only modes. All four cases assert exact stdout and stderr as well.
- E-007: `test_repeated_stdin_lines_retain_output_multiplicity` requires exact
  output order and multiplicity for adjacent and separated repeated valid lines,
  plus repeated diagnostics for invalid lines. Four cases cover valid-only and
  mixed stdin in normal and check-only modes.

The expanded CLI suite passes all 27 cases on the unchanged implementation.
The reviewer's patches were then applied individually in scratch source copies,
with bytecode writing disabled; each copy was restored after its run.

| Mutation | Contract result |
| --- | --- |
| Lens E M05: reset status before processing a valid URL | All four E-006 cases fail because status becomes 0 |
| Lens E M08: suppress previously seen stdin lines | Three E-007 cases fail on missing output or diagnostics; valid-only check mode passes |

Final verification: 425 passed, no skips, with fetched fixtures, installed-wheel
checks and the PyPI 0.2.1 upgrade enabled. `ruff format --check .`, `ruff check .`,
`mypy --strict src` and `pytest` each exit 0; `mypy --strict src tests` also passes.
Every test uses a 300-second timeout and scratch basetemp.

## QA lenses: round 4 fixes

Reviewed base: `518b2fecd508ecf2c571ee96cb75457c189cac60`, dated 2026-11-01.
Fix commit: `5d0f84da554d9a13020de02efa40ebf45afb669e`.
Both reported findings, E-008 and E-009 from lens E, are addressed; none is disputed.
Independent re-verification remains pending.

Both findings identify missing regression contracts. The unchanged implementation
already satisfies these behaviors, so production code and the public API remain
unchanged. CHANGELOG records the additional coverage.

- E-008: `test_unterminated_stdin_line_is_processed` asserts exact status, stdout
  and stderr for valid and invalid final lines without a newline, in normal and
  check-only modes, both alone and after a complete valid line: eight cases.
- E-009: `test_stdin_preserves_case_outside_scheme_and_host` asserts exact output
  for mixed-case userinfo, path, query and fragment with LF and CRLF endings.
  Scheme and host are normalized to lowercase while the other components retain case.
- The installed-wheel subprocess test covers all four valid/invalid and normal/check
  combinations with unterminated input bytes, plus the mixed-case component example.

All ten new direct cases pass on the unchanged implementation. The two reviewer
mutations were then applied individually in scratch source copies, with bytecode
writing disabled. Each copy was restored byte-for-byte after its run.

| Mutation | Contract result |
| --- | --- |
| Lens E N02: drop unterminated final stdin lines | Six E-008 cases and the installed CLI check fail; the two valid check-only cases pass because their observable output and status are unchanged |
| Lens E N10: lowercase the entire stdin URL | Both E-009 cases and the installed CLI check fail on corrupted component case |

Final verification: 435 passed, no skips, with fetched fixtures, installed-wheel
checks and the PyPI 0.2.1 upgrade enabled. `ruff format --check .`, `ruff check .`,
`mypy --strict src` and `pytest` each exit 0; `mypy --strict src tests` also passes.
Every test uses a 300-second timeout and scratch basetemp.
