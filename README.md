# urlsyntax

Syntax-only HTTP and HTTPS URL validation and safe normalization, zero dependencies, no network or DNS.

## Install

```
pip install urlsyntax
```

## Usage

```python
from urlsyntax import is_valid_http_url, normalize

is_valid_http_url("https://example.com/path?q=1")   # True
is_valid_http_url("ftp://example.com")              # False (scheme)
is_valid_http_url("http://exa mple.com")            # False (illegal character)

normalize("HTTP://Example.COM:80/a/./b/../c?")      # "http://example.com/a/c"
normalize("https://example.com:443/%7euser/#")      # "https://example.com/~user/"
```

`normalize` raises `ValueError` for anything that is not a valid http or https URL,
so validation and normalization share the same rules.

### What is checked

Validation is purely textual. The input must already be a valid URI string: ASCII
only, every character drawn from the RFC 3986 set, and every `%` followed by two
hexadecimal digits. The scheme must be `http` or `https`, a host must be present,
and the port (if any) must be a 16-bit number. A reg-name host is accepted on its
syntax alone and a bracketed IPv6 literal is checked with the standard library. No
name resolution happens: there is no DNS, no connection, and no check that the host
exists.

### What is normalized

- Scheme and host are lower-cased.
- The default port is dropped (80 for http, 443 for https).
- `.` and `..` path segments are resolved.
- An empty path becomes `/`.
- An empty query or fragment is dropped.
- Percent escapes are canonicalized: hex digits upper-cased, and escapes that stand
  for unreserved characters decoded (`%7E` becomes `~`).

`normalize` is idempotent: `normalize(normalize(x)) == normalize(x)`.

### What is left alone, on purpose

These are intentionally untouched because changing them could change meaning:

- The order of query parameters.
- The case of the userinfo component.
- Any trailing slash on a non-empty path.
- Percent escapes for reserved characters (for example `%2F` stays `%2F`).

## Why

Validation and normalization are usually two separate tools. `validators` checks a
URL with a regular expression but does not normalize. `url-normalize` normalizes but
guesses missing parts, such as filling in a scheme, which changes what the string
addresses. The standard library's `urllib.parse` splits and rebuilds a URL but makes
no judgement about whether it is a valid http URL and applies none of these
normalizations. `urlsyntax` does both, conservatively, on top of `urllib.parse`, with
full type hints and no third-party dependency, and it never touches the network.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
