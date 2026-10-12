"""The error raised for a string that is not a valid http or https URL."""

from __future__ import annotations

from typing import Literal

Reason = Literal[
    "empty",
    "illegal-character",
    "bad-percent-escape",
    "unsupported-scheme",
    "missing-authority",
    "bad-userinfo",
    "userinfo-not-allowed",
    "empty-host",
    "bad-host",
    "bad-ipv6",
    "unsupported-ip-literal",
    "host-escape",
    "ambiguous-ipv4",
    "bad-port",
    "port-out-of-range",
    "bad-path",
    "bad-query",
    "bad-fragment",
]

_MESSAGES: dict[Reason, str] = {
    "empty": "the URL is empty",
    "illegal-character": "the URL contains a character that is not allowed in a URI",
    "bad-percent-escape": "a '%' is not followed by two hexadecimal digits",
    "unsupported-scheme": "the scheme is not http or https",
    "missing-authority": "the URL has no '//' authority",
    "bad-userinfo": "the userinfo contains a character it may not contain",
    "userinfo-not-allowed": "the URL carries userinfo, which was not allowed",
    "empty-host": "the host is empty",
    "bad-host": "the host contains a character it may not contain",
    "bad-ipv6": "the bracketed host is not a valid IPv6 address",
    "unsupported-ip-literal": "IPvFuture literals cannot be used in http or https URLs",
    "host-escape": "a percent escape in the host does not stand for a letter, digit, '-', '.', "
    "'_' or '~'",
    "ambiguous-ipv4": "the host ends in a number but is not a dotted-decimal IPv4 address",
    "bad-port": "the port is not a decimal number",
    "port-out-of-range": "the port is above 65535",
    "bad-path": "the path contains a character it may not contain",
    "bad-query": "the query contains a character it may not contain",
    "bad-fragment": "the fragment contains a character it may not contain",
}


class InvalidURLError(ValueError):
    """Raised for a string that is not a valid http or https URL.

    ``reason`` is a short code naming the rule that failed, such as ``"bad-host"``.
    The message never repeats the input, which may carry credentials.
    """

    reason: Reason

    def __init__(self, reason: Reason) -> None:
        super().__init__(f"{_MESSAGES[reason]} ({reason})")
        self.reason = reason

    def __reduce__(self) -> tuple[type[InvalidURLError], tuple[Reason]]:
        return (type(self), (self.reason,))
