"""Tests for the Vercel API calculation gateway (``api/index.py``).

Validates method resolution precedence (header → body → path),
snake_case/kebab-case normalization, and catalog traceability —
every frontend catalogued method must map to an executable route.

The MCP half of that invariant was retired with ``app/v1/mcp``: the hosted MCP
now dispatches through ``mcp_server.tool_surface.call_tool``, not through these
routes, and its surface is guarded by ``tests/test_agent_guides.py`` and
``tests/test_mcp/test_server.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from api.index import HARDCODED, ROUTES, _normalize_slug, _resolve_valuation_fn, resolve_method

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "lib" / "valuation" / "catalog.ts"


def _catalog_slugs() -> list[str]:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    return re.findall(r'slug:\s*"([a-z0-9-]+)"', text)


class TestResolveMethod:
    def test_resolve_via_header(self) -> None:
        headers = {"X-Valuation-Method": "relief-from-royalty"}
        assert resolve_method("/api/index.py", headers, {}) == "relief-from-royalty"

    def test_resolve_via_body(self) -> None:
        body = {"method": "capm", "risk_free_rate": 0.03}
        assert resolve_method("/api/index.py", {}, body) == "capm"

    def test_header_beats_body(self) -> None:
        headers = {"X-Valuation-Method": "wacc"}
        body = {"method": "capm"}
        assert resolve_method("/api/index.py", headers, body) == "wacc"

    def test_resolve_via_path_prefix(self) -> None:
        assert resolve_method("/api/valuation/relief-from-royalty", {}, {}) == "relief-from-royalty"

    def test_resolve_index_path_is_none(self) -> None:
        assert resolve_method("/api/index.py", {}, {}) is None

    def test_resolve_no_method_is_none(self) -> None:
        assert resolve_method("/api/", {}, {}) is None

    def test_resolve_catalog_root_is_none(self) -> None:
        assert resolve_method("/api/valuation", {}, {}) is None

    def test_body_list_is_ignored(self) -> None:
        assert resolve_method("/api/index.py", {}, [1, 2, 3]) is None


class TestNormalizeSlug:
    def test_snake_case_to_kebab(self) -> None:
        assert _normalize_slug("relief_from_royalty") == "relief-from-royalty"

    def test_kebab_case_unchanged(self) -> None:
        assert _normalize_slug("relief-from-royalty") == "relief-from-royalty"

    def test_strips_whitespace(self) -> None:
        assert _normalize_slug("  capm  ") == "capm"


class TestCatalogTraceability:
    def test_catalog_slugs_are_executable(self) -> None:
        slugs = _catalog_slugs()
        assert len(slugs) >= 68, f"Expected at least 68 catalogued methods, found {len(slugs)}"
        orphans = [s for s in slugs if s not in ROUTES]
        assert orphans == [], f"Catalogued methods without a route: {orphans}"

    def test_no_duplicate_catalog_slugs(self) -> None:
        slugs = _catalog_slugs()
        assert len(slugs) == len(set(slugs)), "Duplicate catalogued slugs detected"

    def test_hardcoded_fallbacks_present(self) -> None:
        assert len(HARDCODED) >= 11, "Expected at least 11 hardcoded fallback methods"


class TestMonteCarloResolver:
    def test_resolves_slug_to_float_callable(self) -> None:
        fn = _resolve_valuation_fn("present-value")
        assert callable(fn)
        assert fn(future_value=1000.0, discount_rate=0.1, periods=1) == pytest.approx(909.09, abs=0.01)

    def test_resolves_snake_case(self) -> None:
        fn = _resolve_valuation_fn("present_value")
        assert callable(fn)

    def test_resolves_single_dict_argument(self) -> None:
        fn = _resolve_valuation_fn("present-value")
        assert fn({"future_value": 1000.0, "discount_rate": 0.1, "periods": 1}) == pytest.approx(909.09, abs=0.01)

    def test_unknown_name_raises(self) -> None:
        with pytest.raises(ValueError):
            _resolve_valuation_fn("not-a-real-function")

    def test_mc_routes_wrapped_with_handlers(self) -> None:
        # When the engine is installed, the callable-taking Monte Carlo methods
        # are swapped for name-resolving handler wrappers.
        expected = {
            "monte-carlo-valuation": "_mc_valuation_handler",
            "monte-carlo-sensitivity": "_mc_sensitivity_handler",
            "monte-carlo-with-correlation": "_mc_correlation_handler",
        }
        for slug, handler_name in expected.items():
            if slug in ROUTES:
                assert ROUTES[slug].__name__ == handler_name, f"{slug} should be wrapped by {handler_name}"
