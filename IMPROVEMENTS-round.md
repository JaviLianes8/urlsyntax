# urlsyntax improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Exact RFC 3986 grammar per component, own IPv6 parser
- [x] Browser agreement: refuse what the WHATWG parser refuses or reads as another host
- [x] `normalize` fixed against RFC 3986 section 6 and RFC 9110 section 4.2.3
- [x] Typed API: `parse_http_url`, `HttpURL`, `InvalidURLError` with reasons, `allow_userinfo`
- [x] `resolve(base, reference)` per RFC 3986 section 5.2
- [x] Contracts: pinned WPT corpus, RFC examples, grammar oracle, README, typing, installed wheel
- [x] Command line: `python -m urlsyntax`
- [x] Docs and packaging: README, CHANGELOG, docstrings, metadata
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [x] Independent review findings fixed with regression tests
- [x] Pull request opened (#2), guard clean

## Starting point

`0.1.0` gives `is_valid_http_url` and `normalize`. It checks that every character is in the
RFC 3986 set and splits with `urllib.parse.urlsplit`, then checks only the host and the port.
Run against the web-platform-tests corpus (below), 95 inputs it accepts are rejected by the
WHATWG URL parser, and 28 more are read by browsers as a different URL than `normalize`
produces. Reading the code against RFC 3986 explains them:

- The character check is global, not per component. `[`, `]` and a second `#` pass in the
  path, query and fragment, and `@` passes in the userinfo: `http://::@c@d:2` is accepted.
- The host check only looks for brackets, so `http://2001::1` is accepted with host `2001:`.
- IPv6 literals go through `ipaddress`, which accepts scope IDs: `http://[::%31]` passes.
- Hosts such as `0x7f.1`, `127.1`, `010.0.0.1` or `999999999` are accepted as names, while
  browsers read them as IPv4 addresses (`127.0.0.1`, `8.0.0.1`, ...). RFC 3986 section 7.4
  calls these "rare IP address formats" and warns they defeat address filters.
- Percent escapes in the host are accepted whatever they decode to (`ho%00st`, `%e2%98%83`),
  which browsers either reject or turn into another name.
- `normalize` drops an empty `?` and `#`. RFC 3986 section 6.2.3 says the opposite, with
  this exact example: "the URI "http://example.com/?" cannot be assumed to be equivalent".
- IPv6 literals are only lower-cased, so `[1:0::]` and `[1::]` stay different.
- There is no structured result (host, port, kind of host), no reason for a rejection, no
  way to refuse userinfo (RFC 9110 section 4.2.4), and no reference resolution.

## Sources (fetched 2026-10-12)

- RFC 3986, https://www.rfc-editor.org/rfc/rfc3986.txt
  (sha256 3102dae4b68cebe40337730312fcb612297b8928547267e8b3d1ee6002b2d683).
  Grammar (Appendix A), splitting regex (Appendix B), resolution (5.2) and its examples
  (5.4), normalization (6.2.2, 6.2.3), rare IP formats (7.4).
- RFC 9110, https://www.rfc-editor.org/rfc/rfc9110.txt
  (sha256 21c1cdce6ab0e5509b04d84a28000836c7a087cf786efe6f04877ebfff47232a).
  4.2.1 and 4.2.2: an http(s) URI with an empty host "MUST" be rejected; 4.2.3: http(s)
  normalization and the three equivalent URIs; 4.2.4: userinfo is deprecated.
- RFC 5952, https://www.rfc-editor.org/rfc/rfc5952.txt
  (sha256 c75e82c5f53bcec8148820fadf0d65935336ee2031fa6ce10504797ed4c1979d).
  Section 4: canonical IPv6 text (no leading zeros, longest then first run of two or more
  zero fields becomes `::`, lower case). Section 5 recommends mixed notation
  (`::ffff:192.0.2.1`) for addresses with a well-known IPv4 prefix; this library departs from
  that on purpose and writes every piece in hexadecimal, as the WHATWG IPv6 serializer does,
  so one address has one normal form whatever its prefix.
- WHATWG URL Standard source, whatwg/url commit
  `fde3f74f063341a28d437216f75735b8b40128f5` (2026-10-07),
  https://raw.githubusercontent.com/whatwg/url/fde3f74f063341a28d437216f75735b8b40128f5/url.bs
  (sha256 7f45ea5b6167f08a098619167254a99a3c8b5fd6514fff4963ede4a7c8e05818). Host parser,
  "ends in a number checker", forbidden domain code points, the domain parser returning an
  ASCII domain lower-cased as is, the IPv6 serializer, the userinfo and special-query
  percent-encode sets.
- web-platform-tests, commit `745b9bf3e485300a83b90c62b310ea02cc84e0d9`:
  `url/resources/urltestdata.json`
  (sha256 81e85fd3c199c08ef9c34cf651b3580eeedd080316493bfaf277a6b5ff8cf652, 896 cases) and
  `url/resources/toascii.json`
  (sha256 644eba9d5b593df8095cfa307222f3014542ff9cc02d555f8e5660059d80470f, 87 cases), from
  https://raw.githubusercontent.com/web-platform-tests/wpt/745b9bf3e485300a83b90c62b310ea02cc84e0d9/url/resources/
  Neither is committed: `scripts/fetch_upstream.py` fetches both into `tests/upstream/` and
  the tests check them against the hashes in `tests/upstream/MANIFEST.json`.

## Which spec each function follows

- `is_valid_http_url` and `parse_http_url`: the RFC 3986 grammar for an absolute URI, with
  the http(s) rules of RFC 9110 (authority required, host not empty). On top of that they
  refuse the few RFC-valid forms that browsers refuse or read differently: ports above 65535,
  `IPvFuture` literals, percent escapes in the host that do not decode to letters, digits,
  `-`, `.`, `_` or `~`, and hosts ending in a number that are not plain dotted-decimal IPv4.
  Non-ASCII input is refused, as in RFC 3986: an internationalized name must be given in its
  `xn--` form.
- `normalize`: RFC 3986 section 6.2.2 and 6.2.3 with the http(s) rules of RFC 9110 section
  4.2.3, plus RFC 5952 section 4 for IPv6 literals (all hexadecimal, not the mixed
  notation of section 5).
- `resolve`: RFC 3986 section 5.2 (strict parser), then the result must be a valid http(s)
  URL.

## Ranked improvements

1. **Exact grammar per component.** Split with the Appendix B regex, then check scheme,
   userinfo, host, port, path, query and fragment against their own ABNF rules. IPv6 with a
   parser written from the RFC 3986 rules (`h16`, `ls32`, `dec-octet`), so no zone IDs and
   no dependence on how `ipaddress` changes between Python versions.
2. **Browser agreement.** The restrictions listed above, each with its own reason. Proven
   on the WPT corpus: no input the WHATWG parser rejects is accepted.
3. **`normalize` that matches the RFCs.** Keep an empty `?` and `#`, write IPv6 literals in
   canonical form, drop an empty port. Proven with the RFC examples and on the WPT corpus:
   for every accepted input, `normalize(input)` and `normalize(browser href)` agree once the
   two documented serialization differences of WHATWG (it percent-encodes `'` in the query
   and some delimiters in the userinfo, and drops an empty password) are applied.
4. **Typed parse API.** `parse_http_url(value) -> HttpURL`, a frozen dataclass with the
   scheme, userinfo, host, host kind (`name`, `ipv4`, `ipv6`), port as `int | None`, path,
   query and fragment. Rejections raise `InvalidURLError`, a `ValueError` with a `reason`
   code. `allow_userinfo=False` refuses credentials in the URL, as RFC 9110 section 4.2.4
   recommends for untrusted input.
5. **`resolve(base, reference)`.** RFC 3986 section 5.2, checked against every example in
   section 5.4 and against the relative cases of the WPT corpus.
6. **Contracts.** Grammar oracle (a regular expression derived by hand from the Appendix A
   ABNF, labelled as such) compared with the parser on generated strings; the IPv6 parser
   compared with `ipaddress`; idempotence and "normal form stays valid" over the corpus;
   README examples executed; public types checked with mypy; installed-wheel end-to-end test.
7. **Command line.** `python -m urlsyntax URL...` (or lines on stdin) prints the normal form
   of each URL and exits 1 if any is invalid, with the reason on stderr. Useful to clean or
   deduplicate URL lists in shell pipelines.
8. **Docs and packaging.** Spec table per function in the README, CHANGELOG for 0.2.0,
   classifiers and keywords, sdist without planning notes, gate script over the whole tree.

## Out of scope

- Converting internationalized names (IRIs) to `xn--` form. Browsers use UTS #46, which
  needs the Unicode IDNA mapping tables; the standard library only has IDNA 2003, which
  gives different answers for some names. Shipping the tables or depending on a package is
  not what this library is for. Input must already be ASCII.
- The WHATWG lenient parser itself (stripping spaces and tabs, backslashes as slashes,
  percent-encoding of raw characters). This library judges URL strings that are already
  well formed; it does not repair them.
- Other schemes. Only http and https have the rules above.
- Refusing userinfo by default: that would break existing callers. It is one keyword away.

## Verification

- Gates on CPython 3.13.2: `ruff format --check .`, `ruff check .`, `mypy --strict src tests`
  and `pytest` (with `URLSYNTAX_E2E=1` the installed-wheel test runs too, including the
  `urlsyntax` console script).
- Web-platform-tests corpus: 0 accepted inputs that browsers reject (95 before), every
  accepted absolute input (85) and every resolvable relative case (34) normalizes like the
  browser `href`, every ASCII case of `toascii.json` gives the browser host or a refusal.
- Grammar oracle: 30,000 generated strings, every refusal of an RFC-valid URL is one of the
  four documented browser-agreement reasons, every acceptance is RFC-valid.
- Guarded logic was removed one piece at a time (62 mutations). The first run left six
  alive: two were unreachable checks (a second `]` in a bracketed host, non-ASCII digits in
  the port), now removed; three were real gaps (dot segments in a reference with an
  authority, illegal characters that vanish with a `..` segment, a lone `.` or `..` in
  `remove_dot_segments`), now tested. The suite now fails for 61 of 62. The survivor
  adds `:` to the host character set, which no input can reach: the port is split off at
  the first `:` before the host is checked.

## Review fixes

An independent review attacked the branch; every finding is fixed, each with a test that
fails when the fix is removed (checked one by one):

- A port of thousands of digits made `int()` raise its own `ValueError` (also in 0.1.0), so
  `is_valid_http_url` raised instead of answering. Leading zeros are now stripped and the
  length checked before converting: long ports are `port-out-of-range`, zero-padded ports
  read as their number.
- Dot-segment removal re-sliced the remaining path at every step, so a few hundred
  kilobytes of `/a/..` took seconds (also in 0.1.0). It now walks the path with an index
  and a segment stack, is compared with a literal transcription of the RFC method on
  20,000 generated paths, and 200,000-segment inputs are timed.
- `resolve` accepted a reference with `[` or `]` in a segment that a later `..` removes.
  The reference's own path, query and fragment are now checked before resolution.
- The command line echoed refused URLs as given: it now masks the userinfo and escapes
  control characters, and argument errors and help go to the streams passed to `main`.
- Docs: the IPv6 normal form departs on purpose from the mixed notation of RFC 5952
  section 5 (now said so), zone identifiers are refused by RFC 3986 itself (moved out of the
  browser-agreement list), and the CHANGELOG lists that an empty userinfo is now kept and no
  longer claims host escapes as new.
