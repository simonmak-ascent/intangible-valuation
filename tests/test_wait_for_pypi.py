"""Unit tests for the PyPI readiness gate used by the MCP Registry publish workflow.

Guards the fix for the release race: ``publish-registry.yml`` must wait until the
PyPI package version exists **and** carries the ``mcp-name:`` ownership marker
before calling ``mcp-publisher publish``.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("wait_for_pypi", ROOT / "scripts" / "wait_for_pypi.py")
assert _spec is not None
assert _spec.loader is not None
wait_for_pypi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wait_for_pypi)

SERVER_NAME = "io.github.simonmak-ascent/intangible-valuation"


def _meta(version: str, marker: str | None) -> dict:
    body = f"# package\n\n<!-- {marker} -->\n" if marker else "# package\n"
    return {"info": {"version": version, "description": body}}


def test_ownership_marker_format() -> None:
    assert wait_for_pypi.ownership_marker(SERVER_NAME) == f"mcp-name: {SERVER_NAME}"


def test_manifest_metadata_from_real_server_json() -> None:
    manifest = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    resolved = wait_for_pypi.package_metadata_from_manifest(manifest)
    assert resolved == (manifest["name"], "intangible-valuation", manifest["packages"][0]["version"])


def test_manifest_without_pypi_package_returns_none() -> None:
    assert wait_for_pypi.package_metadata_from_manifest({"name": "x", "packages": []}) is None
    assert wait_for_pypi.package_metadata_from_manifest({"name": "x"}) is None


def test_check_metadata_accepts_marker() -> None:
    assert wait_for_pypi.check_metadata(_meta("2.0.1", f"mcp-name: {SERVER_NAME}"), SERVER_NAME) is None


def test_check_metadata_rejects_missing_marker() -> None:
    problem = wait_for_pypi.check_metadata(_meta("2.0.1", None), SERVER_NAME)
    assert problem is not None
    assert "ownership marker" in problem


def test_wait_for_package_returns_zero_when_ready() -> None:
    calls: list[str] = []

    def fetcher(url: str) -> dict:
        calls.append(url)
        return _meta("2.0.1", f"mcp-name: {SERVER_NAME}")

    rc = wait_for_pypi.wait_for_package(
        "intangible-valuation", "2.0.1", SERVER_NAME, attempts=3, interval=0, fetcher=fetcher
    )
    assert rc == 0
    assert len(calls) == 1


def test_wait_for_package_fails_when_marker_missing() -> None:
    rc = wait_for_pypi.wait_for_package(
        "intangible-valuation",
        "2.0.1",
        SERVER_NAME,
        attempts=3,
        interval=0,
        fetcher=lambda _url: _meta("2.0.1", None),
    )
    assert rc == 1


def test_wait_for_package_polls_until_available() -> None:
    state = {"n": 0}

    def fetcher(_url: str) -> dict | None:
        state["n"] += 1
        if state["n"] < 3:
            return None
        return _meta("2.0.1", f"mcp-name: {SERVER_NAME}")

    rc = wait_for_pypi.wait_for_package(
        "intangible-valuation", "2.0.1", SERVER_NAME, attempts=5, interval=0, fetcher=fetcher
    )
    assert rc == 0
    assert state["n"] == 3


def test_wait_for_package_times_out() -> None:
    rc = wait_for_pypi.wait_for_package(
        "intangible-valuation", "2.0.1", SERVER_NAME, attempts=2, interval=0, fetcher=lambda _url: None
    )
    assert rc == 1
