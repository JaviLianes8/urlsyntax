"""Command line: print the normal form of each URL, exit 1 if any is invalid."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import TextIO

from ._errors import InvalidURLError
from ._parse import parse_http_url


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urlsyntax",
        description="Validate http and https URLs and print their normal form. "
        "Reads one URL per line from standard input when none are given.",
    )
    parser.add_argument("urls", nargs="*", metavar="URL")
    parser.add_argument("--check", action="store_true", help="validate only, print nothing")
    parser.add_argument("--no-userinfo", action="store_true", help="refuse user@ in URLs")
    return parser


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line and return its exit status (0 ok, 1 invalid, 2 usage)."""
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return int(stop.code or 0)
    urls: Iterable[str] = args.urls or _lines(stdin or sys.stdin)
    status = 0
    for url in urls:
        try:
            parsed = parse_http_url(url, allow_userinfo=not args.no_userinfo)
        except InvalidURLError as error:
            err.write(f"invalid ({error.reason}): {url}\n")
            status = 1
            continue
        if not args.check:
            out.write(f"{parsed}\n")
    return status


def _lines(stream: TextIO) -> Iterable[str]:
    for line in stream:
        text = line.rstrip("\r\n")
        if text:
            yield text
