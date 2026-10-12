"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with URLSYNTAX_E2E=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("URLSYNTAX_E2E") != "1", reason="set URLSYNTAX_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources, pickle
import urlsyntax
from urlsyntax import InvalidURLError, is_valid_http_url, normalize, parse_http_url, resolve

assert "site-packages" in urlsyntax.__file__, urlsyntax.__file__
assert importlib.metadata.version("urlsyntax") == urlsyntax.__version__
assert importlib.resources.files("urlsyntax").joinpath("py.typed").is_file()
assert normalize("HTTP://Example.COM:80/a/./b/../c?") == "http://example.com/a/c?"
assert normalize("http://[2001:0db8:0:0:0:0:2:1]/") == "http://[2001:db8::2:1]/"
url = parse_http_url("https://u@[::1]:8443/x#f")
assert (url.host, url.host_kind, url.port, url.userinfo) == ("::1", "ipv6", 8443, "u")
assert resolve("http://a/b/c/d;p?q", "../../g") == "http://a/g"
for bad in ("http://0x7f.1/", "http://2001::1", "http://[::%31]/", "http://a/#x#y"):
    assert not is_valid_http_url(bad), bad
assert not is_valid_http_url("http://u@a/", allow_userinfo=False)
try:
    normalize("http://ho%00st/")
except InvalidURLError as error:
    assert error.reason == "host-escape"
    assert pickle.loads(pickle.dumps(error)).reason == "host-escape"
else:
    raise AssertionError("escape in host accepted")
print("e2e ok")
"""


def _run(*cmd: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, check=False
    )


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--wheel", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("urlsyntax-*.whl")

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    result = _run(python, "-I", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "e2e ok"

    script = bindir / ("urlsyntax.exe" if sys.platform == "win32" else "urlsyntax")
    cli = _run(script, "HTTP://A:80/x/../y", "ftp://b/", cwd=work)
    assert cli.returncode == 1
    assert cli.stdout == "http://a/y\n"
    assert cli.stderr == "invalid (unsupported-scheme): ftp://b/\n"


def test_distributions_ship_no_third_party_corpus(tmp_path: Path) -> None:
    built = _run(sys.executable, "-m", "build", "--outdir", tmp_path, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = tmp_path.glob("urlsyntax-*.whl")
    (sdist,) = tmp_path.glob("urlsyntax-*.tar.gz")
    wheel_names = zipfile.ZipFile(wheel).namelist()
    assert all(n.startswith(("urlsyntax/", "urlsyntax-")) for n in wheel_names), wheel_names
    with tarfile.open(sdist) as archive:
        names = [n.split("/", 1)[1] for n in archive.getnames() if "/" in n]
    assert "tests/upstream/MANIFEST.json" in names
    assert "tests/test_wpt.py" in names
    assert not any(n.endswith(("urltestdata.json", "toascii.json")) for n in names), names
    assert not any(n.startswith((".github", "IMPROVEMENTS")) for n in names), names
