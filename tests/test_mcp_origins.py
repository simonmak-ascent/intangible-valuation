"""Origin policy for the MCP endpoint.

The MCP transport specification requires Origin validation and a 403 for a present-but-invalid
origin. These tests cover the policy itself — the allowlist and the CORS header it produces —
because that is where a wildcard would creep back in.
"""

from __future__ import annotations

from api.mcp import DEFAULT_ALLOWED_ORIGINS, _cors, allowed_origins


def test_default_allowlist_is_the_service_origin_and_loopback():
    assert "https://intangible-valuation.ascent-partners.com" in DEFAULT_ALLOWED_ORIGINS
    assert "http://localhost:3000" in DEFAULT_ALLOWED_ORIGINS


def test_env_overrides_the_defaults(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_ORIGINS", "https://example.test, http://localhost:7777")
    assert allowed_origins() == frozenset({"https://example.test", "http://localhost:7777"})
    # Replacement, not extension: one list, one place to reason about.
    assert "https://intangible-valuation.ascent-partners.com" not in allowed_origins()


def test_no_origin_means_no_cors_header():
    """A non-browser client gets no CORS header, and is still allowed to call."""
    assert "Access-Control-Allow-Origin" not in _cors(None)


def test_allowed_origin_is_echoed():
    origin = "https://intangible-valuation.ascent-partners.com"
    assert _cors(origin)["Access-Control-Allow-Origin"] == origin


def test_unapproved_origin_gets_no_wildcard():
    """The wildcard is gone: an unapproved origin gets no Access-Control-Allow-Origin at all."""
    headers = _cors("https://audit-origin.invalid")
    assert "Access-Control-Allow-Origin" not in headers
    assert headers.get("Vary") == "Origin"
