# urlsyntax

Syntax-only validation, parsing, normalization and resolution of http and https URLs.
Follows RFC 3986 and RFC 9110, refuses what browsers would refuse or read differently,
zero dependencies, fully typed, no network or DNS.

## Install

```
pip install urlsyntax
```

## Usage

### Validate

```python
from urlsyntax import is_valid_http_url

print(is_valid_http_url("https://example.com/path?q=1"))  # True
print(is_valid_http_url("ftp://example.com"))  # False
print(is_valid_http_url("http://exa mple.com"))  # False
print(is_valid_http_url("http://0x7f.1/"))  # False
print(is_valid_http_url("http://user@example.com/", allow_userinfo=False))  # False
```

### Find out why

```python
from urlsyntax import InvalidURLError, parse_http_url


def reason(url: str) -> str:
    try:
        parse_http_url(url)
    except InvalidURLError as error:
        return error.reason
    return "valid"


print(reason("http://127.1/"))  # ambiguous-ipv4
print(reason("http://example.com:99999/"))  # port-out-of-range
print(reason("http://[::1%25eth0]/"))  # bad-ipv6
print(reason("http://example.com/"))  # valid
```

Every reason is listed under [Reasons](#reasons). `InvalidURLError` is a `ValueError`, and
its message never repeats the input, which may hold a password.

### Parse

```python
from urlsyntax import parse_http_url

url = parse_http_url("HTTPS://User@Example.COM:443/a/./b/%7euser?q=1#top")
print(url.scheme, url.host, url.host_kind)  # https example.com name
print(url.port, url.effective_port)  # None 443
print(url.userinfo, url.path, url.query, url.fragment)  # User /a/b/~user q=1 top
print(parse_http_url("http://[2001:DB8:0:0::1]:8080/").host)  # 2001:db8::1
print(str(url))  # https://User@example.com/a/b/~user?q=1#top
```

Every field of `HttpURL` is in normal form, and `str(url)` is the same text `normalize`
returns. `userinfo`, `query` and `fragment` are `None` when absent and `""` when present but
empty. `port` is `None` when it is absent, empty or the scheme default.

### Normalize

```python
from urlsyntax import normalize

print(normalize("HTTP://Example.COM:80/a/./b/../c"))  # http://example.com/a/c
print(normalize("http://EXAMPLE.com:/%7esmith/home.html"))  # http://example.com/~smith/home.html
print(normalize("http://example.com/?"))  # http://example.com/?
print(normalize("http://[2001:0db8:0:0:0:0:2:1]/"))  # http://[2001:db8::2:1]/
```

`normalize` is idempotent, `normalize(normalize(x)) == normalize(x)`, and raises
`InvalidURLError` for anything `parse_http_url` refuses.

### Resolve a link

```python
from urlsyntax import normalize, resolve

page = "http://a/b/c/d;p?q"
print(resolve(page, "../g"))  # http://a/b/g
print(resolve(page, "//g"))  # http://g
print(normalize(resolve(page, "g?y/../x#s")))  # http://a/b/c/g?y/../x#s
```

`resolve` returns the target as RFC 3986 section 5.3 recomposes it; pass it to `normalize`
for the canonical form. A target that is not an http or https URL with a host (such as
`mailto:x` or the strict reading of `http:g`) raises `InvalidURLError`.

### Command line

```
$ python -m urlsyntax "HTTP://Example.COM:80/a/../b" "http://127.1/"
http://example.com/b
invalid (ambiguous-ipv4): http://127.1/
```

With no arguments it reads one URL per line from standard input. `--check` only validates,
`--no-userinfo` refuses credentials. An invalid URL is echoed on standard error with its
userinfo replaced by `***` and control characters escaped. The exit status is 0 when every
URL is valid, 1 when any is invalid, 2 for a usage error. The same command is installed as
`urlsyntax`.

## API

| Name | What it does |
| --- | --- |
| `is_valid_http_url(value, *, allow_userinfo=True)` | `True` when `value` is a valid http or https URL string; `False` for anything else, non-strings included |
| `parse_http_url(value, *, allow_userinfo=True)` | `HttpURL` in normal form, or `InvalidURLError`; `TypeError` for a non-string |
| `normalize(value)` | the normal form as a string, `str(parse_http_url(value))` |
| `resolve(base, reference)` | the target of `reference` relative to the http(s) URL `base` |
| `HttpURL` | frozen dataclass: `scheme`, `userinfo`, `host`, `host_kind`, `port`, `path`, `query`, `fragment`, and `effective_port` |
| `InvalidURLError` | `ValueError` with a `reason` code |
| `Reason` | the `Literal` type of every reason code |
| `HostKind` | `Literal["name", "ipv4", "ipv6"]` |
| `Scheme` | `Literal["http", "https"]` |

## Which rules apply

| Function | Specification |
| --- | --- |
| `is_valid_http_url`, `parse_http_url` | RFC 3986 grammar for an absolute URI, per component; RFC 9110 sections 4.2.1 and 4.2.2 (authority required, host not empty); the browser-agreement rules below |
| `normalize`, `HttpURL` fields | RFC 3986 sections 6.2.2 and 6.2.3, RFC 9110 section 4.2.3, RFC 5952 section 4 for IPv6 (all hexadecimal, see below) |
| `resolve` | RFC 3986 section 5.2, strict parser |

IPv6 zone identifiers (`[fe80::1%25eth0]`, RFC 6874) are not part of the RFC 3986 grammar
and are refused. Input must already be a URI string: ASCII only, every character allowed in the component
it sits in, every `%` followed by two hexadecimal digits. An internationalized host must be
given in its `xn--` form; `xn--` labels are taken as written, as browsers do. Nothing is
looked up: no DNS, no connection.

### Browser agreement

RFC 3986 allows a few forms that the WHATWG URL Standard, which browsers follow, refuses or
reads as a different address. They are refused here too:

- A port above 65535.
- `IPvFuture` literals such as `[v1.x]`.
- A percent escape in the host that does not stand for a letter, digit, `-`, `.`, `_` or
  `~`. Browsers decode the host and reject or remap anything else.
- A host that ends in a number but is not a plain dotted-decimal IPv4 address, such as
  `127.1`, `0x7f.0.0.1`, `010.0.0.1`, `4294967295` or `1.2.3.4.`. Browsers and many
  resolvers read these as IPv4 addresses (RFC 3986 section 7.4 warns that they defeat
  address filters).

This is tested against the web-platform-tests URL corpus: no input that browsers refuse is
accepted, and every accepted input normalizes to what the browser's `href` normalizes to,
apart from two serialization habits of the WHATWG standard that RFC 3986 does not share:
browsers percent-encode `'` in the query and `;`, `=` and extra `:` in the userinfo, and
drop an empty password or userinfo.

### What is normalized

- Scheme and host are lower-cased; escapes in the host are decoded.
- The port is dropped when empty or the default (80 for http, 443 for https); leading zeros
  go.
- `.` and `..` segments are resolved, `%2E` counting as `.`.
- An empty path becomes `/`.
- Percent escapes are canonicalized: hex digits upper-cased, and escapes of unreserved
  characters decoded (`%7E` becomes `~`).
- IPv6 literals follow RFC 5952 section 4 (no leading zeros, longest run of zeros as `::`,
  lower case) and are written entirely in hexadecimal, as browsers write them. This departs
  on purpose from the mixed notation that RFC 5952 section 5 recommends for addresses such
  as `::ffff:192.0.2.1`, so one address always has one normal form.

### What is left alone, on purpose

Changing these could change what the URL addresses:

- An empty query or fragment: `http://example.com/?` is not `http://example.com/`
  (RFC 3986 section 6.2.3).
- The order of query parameters.
- The case of the userinfo, path, query and fragment, and an empty password.
- Any trailing slash on a non-empty path.
- Percent escapes of reserved characters (`%2F` stays `%2F`).

### Reasons

`empty`, `illegal-character`, `bad-percent-escape`, `unsupported-scheme`,
`missing-authority`, `bad-userinfo`, `userinfo-not-allowed`, `empty-host`, `bad-host`,
`bad-ipv6`, `unsupported-ip-literal`, `host-escape`, `ambiguous-ipv4`, `bad-port`,
`port-out-of-range`, `bad-path`, `bad-query`, `bad-fragment`.

## Why

Validation and normalization are usually two separate tools. `validators` checks a URL
with a regular expression but does not normalize. `url-normalize` normalizes but guesses
missing parts, such as filling in a scheme, which changes what the string addresses. The
standard library's `urllib.parse` splits and rebuilds a URL but makes no judgement about
whether it is a valid http URL, accepts hosts such as `0x7f.1` that reach a different
machine than they appear to, and applies none of these normalizations. `urlsyntax` does
all of it, conservatively, with full type hints and no third-party dependency, and it
never touches the network.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
