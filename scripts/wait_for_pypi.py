#!/usr/bin/env python3
"""Block until a PyPI package version is available and carries the MCP ownership marker.

The Official MCP Registry validates that the PyPI package version declared in
``server.json`` exists on PyPI and that the server name appears in the package
README as ``mcp-name: <server-name>``. A GitHub release fires the PyPI publish
and the registry publish at the same time, so the registry run can race ahead of
PyPI and fail with an opaque ``400``.

This gate polls the PyPI JSON API until the declared version is served and the
ownership marker is present, then exits 0. It exits non-zero with a clear
message on timeout or a missing marker, so a real packaging defect fails fast
instead of looking like a transient race.

Used by ``.github/workflows/publish-registry.yml``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PYPI_JSON = "https://pypi.org/pypi/{package}/{version}/json"


def ownership_marker(server_name: str) -> str:
    """The literal string the MCP Registry looks for in the package README."""
    return f"mcp-name: {server_name}"


def package_metadata_from_manifest(
    manifest: dict[str, Any],
) -> tuple[str, str, str] | None:
    """Return ``(server_name, package_identifier, version)`` for the PyPI package.

    Returns ``None`` when the manifest declares no PyPI package (nothing to wait
    for).
    """
    pypi_packages = [p for p in manifest.get("packages", []) if p.get("registryType") == "pypi"]
    if not pypi_packages:
        return None
    package = pypi_packages[0]
    return str(manifest.get("name", "")), str(package["identifier"]), str(package["version"])


def check_metadata(data: dict[str, Any], server_name: str) -> str | None:
    """Return ``None`` when the PyPI metadata is acceptable, else the problem."""
    description = data.get("info", {}).get("description") or ""
    marker = ownership_marker(server_name)
    if marker not in description:
        return (
            f"PyPI README is missing the ownership marker '{marker}'; "
            "the MCP Registry ownership check will reject this package version."
        )
    return None


def fetch_json(url: str, timeout: float = 30.0) -> dict[str, Any] | None:
    """Fetch JSON from ``url``; return ``None`` when it is not ready yet.

    A 404 (version not published yet) or a connection error is treated as
    "not ready"; any other HTTP error is also swallowed to ``None`` so the poll
    loop keeps trying until its deadline.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ConnectionError, ValueError):
        return None


def wait_for_package(
    package: str,
    version: str,
    server_name: str,
    *,
    attempts: int,
    interval: float,
    fetcher: Any = fetch_json,
) -> int:
    """Poll PyPI until ``package==version`` is served with the marker; return an exit code."""
    url = PYPI_JSON.format(package=package, version=version)
    for attempt in range(1, attempts + 1):
        data = fetcher(url)
        if data is not None:
            problem = check_metadata(data, server_name)
            if problem is None:
                print(f"PyPI has {package} {version} with ownership marker — ready to publish.")
                return 0
            print(f"::error::{problem}")
            return 1
        print(f"attempt {attempt}/{attempts}: {package} {version} not on PyPI yet — waiting {interval:g}s")
        if attempt < attempts:
            time.sleep(interval)
    print(f"::error::Timed out after {attempts} attempts waiting for {package} {version} on PyPI.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="server.json",
        help="MCP registry manifest to read (default: server.json)",
    )
    parser.add_argument("--attempts", type=int, default=40, help="poll attempts (default: 40)")
    parser.add_argument("--interval", type=float, default=15.0, help="seconds between polls (default: 15)")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    resolved = package_metadata_from_manifest(manifest)
    if resolved is None:
        print("No PyPI package declared in the manifest — nothing to wait for.")
        return 0
    server_name, package, version = resolved
    return wait_for_package(package, version, server_name, attempts=args.attempts, interval=args.interval)


if __name__ == "__main__":
    sys.exit(main())
