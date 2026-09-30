"""Packaging manifest verification (Glama + Official MCP Registry).

Guards the VDD spec ``vdd/specs/glama-packaging/spec.md``:

* AC-1 — ``glama.json`` is a complete Glama manifest.
* AC-2 — ``server.json`` declares a streamable-http remote *and* a PyPI stdio package.
* AC-3 — one version across ``pyproject.toml``, ``mcp_server/pyproject.toml``,
  ``server.json`` and a ``CHANGELOG.md`` heading.
* AC-E1 — a ``server.json`` without ``packages`` is rejected.

No network access: everything is read from the repository.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER_JSON = ROOT / "server.json"
GLAMA_JSON = ROOT / "glama.json"
PYPROJECT = ROOT / "pyproject.toml"
MCP_PYPROJECT = ROOT / "mcp_server" / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"

REMOTE_URL = "https://intangible-valuation.simonmak.com/api/mcp"
PACKAGE_NAME = "intangible-valuation"
CONSOLE_SCRIPT = "intangible-valuation-mcp"

GLAMA_REQUIRED_KEYS = {
    "$schema",
    "maintainers",
    "name",
    "description",
    "repository",
    "license",
    "runtime",
    "installInstructions",
    "categories",
    "keywords",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_server_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return a list of problems with an MCP registry ``server.json``.

    An empty list means the manifest is valid. Missing ``packages`` is the
    AC-E1 failure mode.
    """
    problems: list[str] = []

    if manifest.get("name") != f"io.github.simonplmak-cloud/{PACKAGE_NAME}":
        problems.append("name must be io.github.simonplmak-cloud/intangible-valuation")

    description = manifest.get("description", "")
    if not description or len(description) > 100:
        problems.append("description must be present and <= 100 characters")

    remotes = manifest.get("remotes") or []
    if not any(r.get("type") == "streamable-http" and r.get("url") == REMOTE_URL for r in remotes):
        problems.append(f"remotes must include a streamable-http entry at {REMOTE_URL}")

    packages = manifest.get("packages")
    if not packages:
        problems.append("packages must declare at least one installable package")
        return problems

    pypi = [p for p in packages if p.get("registryType") == "pypi"]
    if not pypi:
        problems.append("packages must include a pypi (registryType) entry")
        return problems

    entry = pypi[0]
    if entry.get("identifier") != PACKAGE_NAME:
        problems.append(f"package identifier must be {PACKAGE_NAME}")
    if entry.get("runtimeHint") != "uvx":
        problems.append("package runtimeHint must be uvx")
    if (entry.get("transport") or {}).get("type") != "stdio":
        problems.append("package transport.type must be stdio")
    if not entry.get("version"):
        problems.append("package must pin a version")

    return problems


# --- AC-1: Glama manifest ---------------------------------------------------


def test_glama_manifest_is_complete() -> None:
    manifest = _load_json(GLAMA_JSON)
    missing = GLAMA_REQUIRED_KEYS - manifest.keys()
    assert not missing, f"glama.json is missing keys: {sorted(missing)}"
    assert manifest["$schema"] == "https://glama.ai/mcp/schemas/server.json"
    assert manifest["runtime"] == "python"
    assert manifest["license"] == "MIT"
    assert manifest["repository"].endswith("/intangible-valuation")
    assert manifest["name"] == PACKAGE_NAME
    assert CONSOLE_SCRIPT in manifest["installInstructions"]["pip"]
    assert "uvx" in manifest["installInstructions"]["uvx"]
    assert manifest["categories"], "categories must not be empty"
    assert manifest["keywords"], "keywords must not be empty"


# --- AC-2: Registry manifest declares package + remote ----------------------


def test_server_manifest_is_valid() -> None:
    manifest = _load_json(SERVER_JSON)
    assert validate_server_manifest(manifest) == []


def test_server_manifest_declares_remote_and_package() -> None:
    manifest = _load_json(SERVER_JSON)
    assert any(r.get("url") == REMOTE_URL for r in manifest["remotes"])
    package = next(p for p in manifest["packages"] if p["registryType"] == "pypi")
    assert package["identifier"] == PACKAGE_NAME
    assert package["transport"]["type"] == "stdio"


# --- AC-3: single version source of truth -----------------------------------


def _versions() -> tuple[str, str, str]:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    mcp_pyproject = tomllib.loads(MCP_PYPROJECT.read_text(encoding="utf-8"))
    manifest = _load_json(SERVER_JSON)
    return pyproject["project"]["version"], mcp_pyproject["project"]["version"], manifest["version"]


def test_versions_are_aligned() -> None:
    root, mcp_pkg, manifest = _versions()
    assert root == mcp_pkg == manifest, f"version drift: {root=} {mcp_pkg=} {manifest=}"


def test_changelog_documents_version() -> None:
    (version, _, _) = _versions()
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert re.search(rf"^## \[{re.escape(version)}\]", changelog, re.MULTILINE), (
        f"CHANGELOG.md has no '## [{version}]' heading"
    )


# --- AC-E1: a manifest without packages is rejected -------------------------


@pytest.mark.parametrize("mutate", ["drop_packages", "drop_remote", "bad_transport"])
def test_invalid_server_manifest_is_rejected(mutate: str) -> None:
    manifest = _load_json(SERVER_JSON)
    if mutate == "drop_packages":
        manifest.pop("packages")
    elif mutate == "drop_remote":
        manifest["remotes"] = []
    elif mutate == "bad_transport":
        manifest["packages"][0]["transport"] = {"type": "sse"}
    assert validate_server_manifest(manifest), f"invalid manifest ({mutate}) was accepted"


# --- AC-5: stdio server answers tools/list with 14 tools ---------------------

EXPECTED_TOOL_COUNT = 14


def _read_rpc(proc: subprocess.Popen[str], want_id: int, timeout: float = 30.0) -> dict[str, Any]:
    """Read NDJSON lines from the server until the response with ``want_id`` arrives."""
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        line = proc.stdout.readline()  # type: ignore[union-attr]
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue  # FastMCP may log non-JSON noise; ignore it
        if message.get("id") == want_id:
            return message
    raise AssertionError(f"no JSON-RPC response with id={want_id} within {timeout}s")


def test_stdio_server_lists_14_tools() -> None:
    pytest.importorskip("fastmcp", reason="the [mcp] extra is required for the stdio server")

    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, str(ROOT / "mcp_server" / "server.py")],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        assert proc.stdin is not None
        assert proc.stdout is not None
        requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "packaging-test", "version": "0"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
        for request in requests:
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()

        init = _read_rpc(proc, want_id=1)
        assert "result" in init, f"initialize failed: {init}"
        listing = _read_rpc(proc, want_id=2)
        tools = listing["result"]["tools"]
        assert len(tools) == EXPECTED_TOOL_COUNT, (
            f"expected {EXPECTED_TOOL_COUNT} tools, got {len(tools)}: {[t['name'] for t in tools]}"
        )
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive
            proc.kill()
