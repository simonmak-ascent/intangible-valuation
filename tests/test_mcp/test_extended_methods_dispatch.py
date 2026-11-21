"""Every MCP method that the catalog used to mark API-only must dispatch to the library's own value.

The static contract test proves the parameter mapping names real parameters; this proves the mapping
computes the same number. A method added with a wrong ``args`` map, a missing ``inject``, or a
required argument silently dropped would fail here while the contract test stayed green.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

import pytest

from mcp_server import tool_surface

# (tool, method key, kwargs, module, function) — the kwargs are the MCP parameter names, which match
# the library's own names for every method below (the contract test enforces that they must).
CASES: list[tuple[str, str, dict[str, Any], str, str]] = [
    (
        "valuation_ip",
        "patent_portfolio",
        {"patents": [{"value": 1000}], "diversification_factor": 0.1},
        "intangible_valuation.asset_types.ip_valuation",
        "patent_portfolio_valuation",
    ),
    (
        "valuation_ip",
        "option_pricing",
        {"exercise_cost": 100, "expected_value": 150, "volatility": 0.3, "time_to_expiry": 5, "risk_free_rate": 0.04},
        "intangible_valuation.asset_types.ip_valuation",
        "option_pricing_patent",
    ),
    (
        "valuation_market_approach",
        "brand_strength_index",
        {
            "revenue_stability": 0.8,
            "market_share": 0.7,
            "geographic_reach": 0.6,
            "customer_loyalty": 0.75,
            "investment_level": 0.65,
        },
        "intangible_valuation.asset_types.brand_valuation",
        "brand_strength_index",
    ),
    (
        "valuation_market_approach",
        "interbrand_brand",
        {"brand_earnings": 1000, "role_of_brand_index": 0.5, "brand_strength_score": 70, "discount_rate": 0.1},
        "intangible_valuation.asset_types.brand_valuation",
        "interbrand_brand_valuation",
    ),
    (
        "valuation_royalty_analysis",
        "brand_royalty_from_comparables",
        {"comparable_rates": [0.05, 0.06]},
        "intangible_valuation.asset_types.brand_valuation",
        "brand_royalty_rate_from_comparables",
    ),
    (
        "valuation_technology",
        "obsolescence_curve",
        {"initial_value": 1000, "obsolescence_rate": 0.1, "periods": 5},
        "intangible_valuation.asset_types.technology_valuation",
        "technology_obsolescence_curve",
    ),
    (
        "valuation_technology",
        "algorithm",
        {"computational_savings": 100, "deployment_scale": 1.5, "competitive_advantage_years": 5, "discount_rate": 0.1},
        "intangible_valuation.asset_types.technology_valuation",
        "algorithm_valuation",
    ),
    (
        "valuation_customer",
        "lifetime_value",
        {"revenue_per_period": 100, "retention_rate": 0.9, "discount_rate": 0.1, "margin": 0.2},
        "intangible_valuation.asset_types.customer_valuation",
        "customer_lifetime_value",
    ),
    (
        "valuation_customer",
        "backlog",
        {"contract_backlog": [{"value": 1000}], "probability_of_completion": 0.9, "discount_rate": 0.1},
        "intangible_valuation.asset_types.customer_valuation",
        "backlog_valuation",
    ),
    (
        "valuation_customer",
        "churn_impact",
        {
            "current_customers": 100,
            "churn_rate_before": 0.1,
            "churn_rate_after": 0.15,
            "revenue_per_customer": 100,
            "discount_rate": 0.1,
        },
        "intangible_valuation.asset_types.customer_valuation",
        "churn_impact_analysis",
    ),
    (
        "valuation_goodwill_ppa",
        "bargain_purchase",
        {"purchase_price": 800, "fair_value_net_assets": 1000},
        "intangible_valuation.advanced.purchase_price_alloc",
        "bargain_purchase_analysis",
    ),
    (
        "valuation_goodwill_ppa",
        "contingent_consideration",
        {
            "scenarios": [{"probability": 0.5, "payment": 100}, {"probability": 0.5, "payment": 200}],
            "discount_rate": 0.1,
        },
        "intangible_valuation.advanced.purchase_price_alloc",
        "contingent_consideration_valuation",
    ),
    (
        "valuation_goodwill_ppa",
        "deferred_tax_liability",
        {"identified_intangibles": [{"name": "x", "fair_value": 100}], "tax_basis": 0, "statutory_rate": 0.25},
        "intangible_valuation.advanced.purchase_price_alloc",
        "deferred_tax_liability_ppa",
    ),
    (
        "valuation_impairment",
        "value_in_use",
        {"cash_flow_projections": [100, 110, 120], "terminal_growth_rate": 0.02, "discount_rate": 0.1},
        "intangible_valuation.advanced.impairment_testing",
        "value_in_use",
    ),
    (
        "valuation_impairment",
        "fair_value_less_costs",
        {"fair_value": 1000, "disposal_costs": 50},
        "intangible_valuation.advanced.impairment_testing",
        "fair_value_less_costs_to_sell",
    ),
    (
        "valuation_impairment",
        "cgu_impairment",
        {
            "cgu_carrying_value": 1000,
            "cgu_recoverable_amount": 800,
            "goodwill_allocated": 100,
            "other_assets": [{"name": "y", "carrying_value": 100}],
        },
        "intangible_valuation.advanced.impairment_testing",
        "cash_generating_unit_impairment",
    ),
    (
        "valuation_simulation",
        "monte_carlo_correlated",
        {
            "valuation_fn": "capm_discount_rate",
            "correlated_distributions": [
                {"name": "risk_free_rate", "distribution": "uniform", "params": {"low": 0.03, "high": 0.05}},
                {"name": "beta", "distribution": "uniform", "params": {"low": 1.0, "high": 1.4}},
                {"name": "market_return", "distribution": "uniform", "params": {"low": 0.08, "high": 0.12}},
            ],
            "correlation_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            "iterations": 50,
            "seed": 7,
        },
        "intangible_valuation.core.statistics",
        "monte_carlo_with_correlation",
    ),
    (
        "valuation_simulation",
        "tornado",
        {
            "function_name": "present_value",
            "base_params": {"future_value": 1000, "discount_rate": 0.1, "periods": 5},
            "parameter_ranges": {"discount_rate": [0.05, 0.1, 0.15]},
        },
        "intangible_valuation.core.statistics",
        "sensitivity_tornado",
    ),
    (
        "valuation_simulation",
        "scenario",
        {
            "scenarios": [
                {
                    "name": "a",
                    "probability": 1.0,
                    "params": {"future_value": 1000, "discount_rate": 0.1, "periods": 5},
                    "function_name": "present_value",
                }
            ]
        },
        "intangible_valuation.core.statistics",
        "scenario_analysis",
    ),
    (
        "valuation_income_methods",
        "profit_split",
        {"licensor_contribution_pct": 0.6, "licensee_contribution_pct": 0.4, "total_profit": 1000},
        "intangible_valuation.advanced.royalty_benchmark",
        "profit_split_method",
    ),
    (
        "valuation_income_methods",
        "analytical_method",
        {"advantage_margin": 0.2, "volume": 1000, "discount_rate": 0.1, "economic_life": 5},
        "intangible_valuation.advanced.royalty_benchmark",
        "analytical_method_valuation",
    ),
]


@pytest.mark.parametrize("tool,key,kwargs,module,function", CASES, ids=[c[1] for c in CASES])
def test_dispatch_matches_the_library(tool: str, key: str, kwargs: dict[str, Any], module: str, function: str) -> None:
    dispatched = tool_surface.call_tool(tool, {"method": key, **kwargs})
    assert "value" in dispatched, f"{key}: dispatch returned no value: {dispatched}"

    # `monte_carlo_with_correlation` takes a callable, which JSON cannot carry: the adapter resolves
    # the name. The direct side mirrors that resolution, so the comparison is like for like.
    if function == "monte_carlo_with_correlation":
        from intangible_valuation.core.statistics import _call_function

        name = kwargs["valuation_fn"]
        direct_kwargs = {
            **{k: v for k, v in kwargs.items() if k != "correlated_distributions"},
            "distributions": kwargs["correlated_distributions"],
            "valuation_fn": lambda **p: _call_function(name, p),
        }
    else:
        direct_kwargs = kwargs

    direct = getattr(importlib.import_module(module), function)(**direct_kwargs)
    # No rounding on either side: the surface returns the library's value as it is, which matters for
    # rates (0.055 must not become 0.06).
    assert dispatched["value"] == pytest.approx(float(direct.value), rel=1e-12), (
        f"{key}: MCP {dispatched['value']} != library {direct.value}"
    )


def test_every_case_names_a_method_the_surface_actually_has() -> None:
    # A rename of a method key would otherwise turn the parametrised cases into tests of nothing.
    by_tool = {t["name"]: {m["key"] for m in t["methods"]} for t in tool_surface.TOOLS}
    for tool, key, _kw, _m, _f in CASES:
        assert key in by_tool[tool], f"{tool} has no method {key}"


def test_rates_are_not_rounded_to_two_decimals() -> None:
    """The tool description promises the library's own precision; a rate must never be rounded.

    0.055 rounded to 2 decimals is 0.06 — a 9% error on a royalty rate. This pins the claim the
    description makes, so the sentence and the code cannot drift apart again.
    """
    result = tool_surface.call_tool(
        "valuation_royalty_analysis",
        {"method": "brand_royalty_from_comparables", "comparable_rates": [0.05, 0.06]},
    )
    assert result["value"] == pytest.approx(0.055)


# Advertised type -> the shape the function's annotation must have, element included. Comparing only
# the container let `array:number` pass for `list[dict]`, which is how two wrong shapes survived.
def _kind(annotation: object) -> tuple[str, ...]:
    import types
    import typing
    from collections.abc import Iterable, Mapping, Sequence

    origin = typing.get_origin(annotation)
    if origin is typing.Union or origin is types.UnionType:
        # Optional[X] is X | None: the declared type describes X, and "not supplied" is what omitting
        # an optional parameter means.
        parts = [a for a in typing.get_args(annotation) if a is not type(None)]
        return _kind(parts[0]) if parts else ("any",)
    if origin is Mapping or origin is dict:
        return ("object",)
    if origin in (list, tuple, set) or origin is Sequence or origin is Iterable:
        args = typing.get_args(annotation)
        return ("array", _kind(args[0])) if args else ("array", ("any",))
    return _SCALAR.get(annotation, ("any",))


_SCALAR = {
    float: ("number",),
    int: ("number",),
    str: ("string",),
    bool: ("boolean",),
    list: ("array", ("any",)),
    dict: ("object",),
}

EXPECTED_KIND = {
    "number": ("number",),
    "integer": ("number",),
    "string": ("string",),
    "boolean": ("boolean",),
    "array:number": ("array", ("number",)),
    "array:object": ("array", ("object",)),
    "array:array": ("array", ("array", ("number",))),
    "object": ("object",),
}


def test_advertised_types_match_the_functions_annotations() -> None:
    import typing

    for tool in tool_surface.TOOLS:
        for method in tool["methods"]:
            fn = getattr(importlib.import_module(method["module"]), method["function"])
            hints = typing.get_type_hints(fn)
            for mapping in ("args", "opt"):
                for fn_param, mcp_name in method.get(mapping, {}).items():
                    # `mc_correlated` rewrites the function name into the callable the library wants;
                    # that is the adapter's whole purpose, so the string/callable pair is expected.
                    if method.get("adapter") == "mc_correlated" and fn_param == "valuation_fn":
                        continue
                    declared = tool_surface.PARAMS[mcp_name]["type"]
                    actual = _kind(hints[fn_param])
                    assert actual == EXPECTED_KIND[declared] or actual[0] == "any", (
                        f"{tool['name']}.{method['key']}: {mcp_name} is advertised as {declared} "
                        f"but {method['function']}({fn_param}) is {hints[fn_param]}"
                    )


CAPM_DISTRIBUTIONS = [
    {"name": "risk_free_rate", "distribution": "uniform", "params": {"low": 0.03, "high": 0.05}},
    {"name": "beta", "distribution": "uniform", "params": {"low": 1.0, "high": 1.4}},
    {"name": "market_return", "distribution": "uniform", "params": {"low": 0.08, "high": 0.12}},
]


def test_monte_carlo_honours_a_named_function() -> None:
    """The adapter used to replace `valuation_fn` unconditionally, so a caller who named one got a sum.

    The catalog documents `valuation_fn` for this method; before the adapter change the name was
    discarded and the result was the arithmetic sum of the sampled parameters.
    """
    from intangible_valuation.core.statistics import _call_function, monte_carlo_valuation

    dispatched = tool_surface.call_tool(
        "valuation_simulation",
        {"method": "monte_carlo", "valuation_fn": "capm_discount_rate",
         "input_distributions": CAPM_DISTRIBUTIONS, "iterations": 50, "seed": 3},
    )
    direct = monte_carlo_valuation(
        valuation_fn=lambda **p: _call_function("capm_discount_rate", p),
        input_distributions=CAPM_DISTRIBUTIONS, iterations=50, seed=3,
    )
    assert dispatched["value"] == pytest.approx(float(direct.value))


def test_monte_carlo_sensitivity_honours_a_named_function() -> None:
    from intangible_valuation.advanced.monte_carlo import monte_carlo_sensitivity
    from intangible_valuation.core.statistics import _call_function

    base = {"risk_free_rate": 0.04, "beta": 1.2, "market_return": 0.10}
    distributions = {"risk_free_rate": {"distribution": "uniform", "params": {"low": 0.03, "high": 0.05}}}

    dispatched = tool_surface.call_tool(
        "valuation_simulation",
        {"method": "monte_carlo_sensitivity", "valuation_fn": "capm_discount_rate",
         "base_params": base, "distributions": distributions, "iterations": 1000, "seed": 3},
    )
    direct = monte_carlo_sensitivity(
        valuation_fn=lambda p: _call_function("capm_discount_rate", p),
        base_params=base, distributions=distributions, iterations=1000, seed=3,
    )
    assert dispatched["value"] == pytest.approx(float(direct.value))


def test_the_type_guard_can_actually_fail() -> None:
    # A guard never observed failing is unproven; these are the two mismatches it exists to catch.
    assert _kind(list[float]) != EXPECTED_KIND["array:object"]
    assert _kind(list[dict]) != EXPECTED_KIND["array:number"]
    # Recorded rather than assumed: a Callable annotation collapses to "any", so the guard cannot
    # judge `valuation_fn` — the adapters are what make that parameter correct, and their tests do.
    assert _kind(Callable[..., float]) == ("any",)


@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("monte_carlo", {"input_distributions": [
            {"name": "risk_free_rate", "distribution": "uniform", "params": {"low": 0.03, "high": 0.05}}]}),
        ("monte_carlo_sensitivity", {"base_params": {"risk_free_rate": 0.04},
                                     "distributions": {"risk_free_rate": {"distribution": "uniform",
                                                                          "params": {"low": 0.03, "high": 0.05}}}}),
        ("monte_carlo_correlated", {"correlated_distributions": [
            {"name": "risk_free_rate", "distribution": "uniform", "params": {"low": 0.03, "high": 0.05}}],
            "correlation_matrix": [[1.0]]}),
    ],
)
def test_valuation_fn_must_be_a_name(method: str, kwargs: dict) -> None:
    """A list or number is refused, not silently ignored — the old adapters fell back to a sum."""
    for bad in (["wacc"], 123):
        with pytest.raises(ValueError, match="valuation_fn"):
            tool_surface.call_tool("valuation_simulation", {"method": method, "valuation_fn": bad, **kwargs})
