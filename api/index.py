"""Vercel serverless API for intangible valuation.

All 88 valuation methods accessible via POST /api/{method-slug}.
Imports the intangible_valuation Python package (must be in requirements.txt).
Falls back to hardcoded methods when package is not installed.
"""

import json, math
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# ---- Optional: import from Python library ---------------------------------
_LIB_FUNCTIONS: dict[str, callable] = {}

try:
    from intangible_valuation.core.time_value import (
        present_value as _pv,
        future_value as _fv,
        annuity_pv as _ann_pv,
        perpetuity_pv as _perp_pv,
        growing_annuity_pv as _grow_ann,
        terminal_value as _tv,
    )
    from intangible_valuation.core.discount_rates import (
        build_up_discount_rate as _build_up,
        capm_discount_rate as _capm,
        wacc as _wacc,
        tax_amortization_benefit as _tab,
        control_premium as _cp,
        dlom_finnerty as _dlom,
        currency_adjusted_discount_rate as _fx_rate,
    )
    from intangible_valuation.approaches.cost_approach import (
        reproduction_cost as _repro,
        replacement_cost as _replace,
    )
    from intangible_valuation.approaches.market_approach import (
        market_approach_comparables as _comps,
        royalty_capitalization as _royalty_cap,
    )
    from intangible_valuation.income_methods.relief_from_royalty import (
        relief_from_royalty as _rfr,
    )
    from intangible_valuation.income_methods.excess_earnings import (
        mpeem as _mpeem,
        single_period_excess_earnings as _spee,
        contributory_asset_charges as _cac,
    )
    from intangible_valuation.income_methods.incremental_cashflow import (
        incremental_cashflow as _icf,
    )
    from intangible_valuation.asset_types.ip_valuation import (
        patent_valuation as _patent,
        copyright_valuation as _copy,
        trade_secret_valuation as _ts,
        patent_portfolio_valuation as _patent_portfolio,
        option_pricing_patent as _opp,
    )
    from intangible_valuation.asset_types.brand_valuation import (
        trademark_valuation as _tm,
        brand_strength_index as _bsi,
        interbrand_brand_valuation as _ibv,
        brand_royalty_rate_from_comparables as _brrc,
    )
    from intangible_valuation.asset_types.technology_valuation import (
        developed_technology_valuation as _tech,
        software_valuation as _sw,
        data_asset_valuation as _data,
        platform_valuation as _platform,
        technology_obsolescence_curve as _tech_obs,
        algorithm_valuation as _algo,
    )
    from intangible_valuation.asset_types.customer_valuation import (
        customer_relationship_valuation as _cust,
        distribution_network_valuation as _dist,
        non_compete_valuation as _nc,
        customer_lifetime_value as _clv,
        backlog_valuation as _backlog,
        churn_impact_analysis as _churn,
    )
    from intangible_valuation.asset_types.human_capital import (
        assembled_workforce_valuation as _wf,
        key_person_value as _kpv,
    )
    from intangible_valuation.advanced.goodwill import (
        goodwill as _gw,
    )
    from intangible_valuation.advanced.purchase_price_alloc import (
        purchase_price_allocation as _ppa,
        bargain_purchase_analysis as _bpa,
        contingent_consideration_valuation as _ccv,
        deferred_tax_liability_ppa as _dtl_ppa,
    )
    from intangible_valuation.advanced.impairment_testing import (
        goodwill_impairment_test as _gw_impair,
        intangible_impairment_test as _ia_impair,
        value_in_use as _viu,
        fair_value_less_costs_to_sell as _fvlcs,
        cash_generating_unit_impairment as _cgu_impair,
    )
    from intangible_valuation.advanced.litigation import (
        patent_infringement_damages as _patent_dmg,
    )
    from intangible_valuation.advanced.monte_carlo import (
        monte_carlo_sensitivity as _mc_sens,
    )
    from intangible_valuation.advanced.transfer_pricing import (
        cup_transfer_price as _cup_tp,
    )
    from intangible_valuation.advanced.royalty_benchmark import (
        royalty_rate_benchmark as _rrb,
        adjust_royalty_rate as _adj_rr,
        twenty_five_percent_rule as _tfpr,
        profit_split_method as _psm,
        analytical_method_valuation as _amv,
    )
    from intangible_valuation.core.statistics import (
        monte_carlo_valuation as _mc_val,
        decision_tree_valuation as _dtv,
        monte_carlo_with_correlation as _mc_corr,
        sensitivity_tornado as _tornado,
        scenario_analysis as _scenario,
    )

    _LIB_FUNCTIONS = {
        # Core — Time Value of Money
        "present-value": _pv,
        "future-value": _fv,
        "annuity-pv": _ann_pv,
        "perpetuity-pv": _perp_pv,
        "growing-annuity-pv": _grow_ann,
        "terminal-value": _tv,
        # Core — Discount Rates
        "build-up-discount-rate": _build_up,
        "capm": _capm,
        "wacc": _wacc,
        "tax-amortization-benefit": _tab,
        "control-premium": _cp,
        "dlom-finnerty": _dlom,
        "currency-adjusted-discount-rate": _fx_rate,
        # Approaches — Cost
        "reproduction-cost": _repro,
        "replacement-cost": _replace,
        # Approaches — Market
        "market-approach-comparables": _comps,
        "royalty-capitalization": _royalty_cap,
        # Income Methods
        "relief-from-royalty": _rfr,
        "mpeem": _mpeem,
        "single-period-excess-earnings": _spee,
        "contributory-asset-charges": _cac,
        "incremental-cashflow": _icf,
        # Asset Types — IP
        "patent-valuation": _patent,
        "copyright-valuation": _copy,
        "trade-secret-valuation": _ts,
        "patent-portfolio-valuation": _patent_portfolio,
        "option-pricing-patent": _opp,
        # Asset Types — Brand
        "trademark-valuation": _tm,
        "brand-strength-index": _bsi,
        "interbrand-brand-valuation": _ibv,
        "brand-royalty-rate-from-comparables": _brrc,
        # Asset Types — Technology
        "developed-technology-valuation": _tech,
        "software-valuation": _sw,
        "data-asset-valuation": _data,
        "platform-valuation": _platform,
        "technology-obsolescence-curve": _tech_obs,
        "algorithm-valuation": _algo,
        # Asset Types — Customer
        "customer-relationship-valuation": _cust,
        "distribution-network-valuation": _dist,
        "non-compete-valuation": _nc,
        "customer-lifetime-value": _clv,
        "backlog-valuation": _backlog,
        "churn-impact-analysis": _churn,
        # Asset Types — Human Capital
        "assembled-workforce-valuation": _wf,
        "key-person-value": _kpv,
        # Advanced — Goodwill & PPA
        "goodwill": _gw,
        "purchase-price-allocation": _ppa,
        "bargain-purchase-analysis": _bpa,
        "contingent-consideration-valuation": _ccv,
        "deferred-tax-liability-ppa": _dtl_ppa,
        # Advanced — Impairment
        "goodwill-impairment-test": _gw_impair,
        "intangible-impairment-test": _ia_impair,
        "value-in-use": _viu,
        "fair-value-less-costs-to-sell": _fvlcs,
        "cash-generating-unit-impairment": _cgu_impair,
        # Advanced — Litigation & Damages
        "patent-infringement-damages": _patent_dmg,
        # Advanced — Monte Carlo & Statistics
        "monte-carlo-sensitivity": _mc_sens,
        "monte-carlo-valuation": _mc_val,
        "decision-tree-valuation": _dtv,
        "monte-carlo-with-correlation": _mc_corr,
        "sensitivity-tornado": _tornado,
        "scenario-analysis": _scenario,
        # Advanced — Transfer Pricing & Royalty
        "cup-transfer-price": _cup_tp,
        "royalty-rate-benchmark": _rrb,
        "adjust-royalty-rate": _adj_rr,
        "twenty-five-percent-rule": _tfpr,
        "profit-split-method": _psm,
        "analytical-method-valuation": _amv,
    }
except ImportError:
    pass


# ---- Hardcoded fallback methods -------------------------------------------
def _h_present_value(future_value, discount_rate, periods):
    pv = future_value / ((1 + discount_rate) ** periods)
    return {
        "value": round(pv, 2),
        "method": "Present Value",
        "formula_reference": "PV = FV / (1+r)^n",
        "steps": [f"PV = FV / (1 + r)^n", f"PV = {future_value} / (1 + {discount_rate})^{periods}", f"PV = ${pv:,.2f}"],
        "assumptions": ["Discount rate constant", "Single cash flow at period n"],
    }


def _h_future_value(present_value, discount_rate, periods):
    fv = present_value * ((1 + discount_rate) ** periods)
    return {"value": round(fv, 2), "method": "Future Value", "formula_reference": "FV = PV * (1+r)^n"}


def _h_annuity_pv(payment, discount_rate, periods):
    pv = payment * (1 - (1 + discount_rate) ** -periods) / discount_rate if discount_rate > 0 else payment * periods
    return {"value": round(pv, 2), "method": "Annuity PV", "formula_reference": "PV = PMT * [1-(1+r)^(-n)] / r"}


def _h_perpetuity_pv(payment, discount_rate):
    return {"value": round(payment / discount_rate, 2), "method": "Perpetuity PV", "formula_reference": "PV = PMT / r"}


def _h_terminal_value(final_year_cashflow, perpetual_growth_rate, discount_rate):
    tv = final_year_cashflow * (1 + perpetual_growth_rate) / (discount_rate - perpetual_growth_rate)
    return {
        "value": round(tv, 2),
        "method": "Terminal Value (Gordon Growth)",
        "formula_reference": "TV = FCF*(1+g)/(r-g)",
    }


def _h_build_up(risk_free_rate, equity_risk_premium, size_premium=0, industry_risk_premium=0, specific_risk_premium=0):
    rate = risk_free_rate + equity_risk_premium + size_premium + industry_risk_premium + specific_risk_premium
    return {
        "value": round(rate, 4),
        "method": "Build-Up Discount Rate",
        "formula_reference": "r = Rf + ERP + Size + Industry + Specific",
    }


def _h_capm(risk_free_rate, beta, market_return):
    rate = risk_free_rate + beta * (market_return - risk_free_rate)
    return {"value": round(rate, 4), "method": "CAPM", "formula_reference": "r = Rf + Beta*(Rm-Rf)"}


def _h_wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
    total = equity_value + debt_value
    rate = (equity_value / total) * cost_of_equity + (debt_value / total) * cost_of_debt * (1 - tax_rate)
    return {"value": round(rate, 4), "method": "WACC", "formula_reference": "WACC = (E/V)*Re + (D/V)*Rd*(1-Tc)"}


def _h_rfr(revenue_projections, royalty_rate, discount_rate, tax_rate, useful_life, tab_enabled=True):
    pv = 0.0
    steps = []
    for t, rev in enumerate(revenue_projections, 1):
        royalty = rev * royalty_rate
        after_tax = royalty * (1 - tax_rate)
        period_pv = after_tax / ((1 + discount_rate) ** t)
        pv += period_pv
        steps.append(
            f"Period {t}: revenue=${rev:,.0f}, royalty=${royalty:,.0f}, after-tax=${after_tax:,.0f}, PV=${period_pv:,.0f}"
        )
    tab = 1.0
    if tab_enabled and tax_rate > 0:
        af = sum(1 / ((1 + discount_rate) ** t) for t in range(1, useful_life + 1))
        tab = 1 / (1 - (tax_rate * af / useful_life))
    value = pv * tab
    steps.append(f"PV before TAB: ${pv:,.2f}, TAB factor: {tab:.4f}")
    return {
        "value": round(value, 2),
        "method": "Relief from Royalty",
        "formula_reference": "Ch 4: RFR with TAB",
        "steps": steps,
        "assumptions": ["Arm's length royalty rate", "Reasonable revenue projections"],
        "pv_before_tab": round(pv, 2),
        "tab_factor": round(tab, 4),
    }


def _h_growing_annuity_pv(payment, discount_rate, growth_rate, periods):
    if discount_rate == growth_rate:
        pv = payment * periods / (1 + discount_rate)
    else:
        pv = payment * (1 - ((1 + growth_rate) / (1 + discount_rate)) ** periods) / (discount_rate - growth_rate)
    return {
        "value": round(pv, 2),
        "method": "Growing Annuity PV",
        "formula_reference": "PV = PMT * [1-((1+g)/(1+r))^n]/(r-g)",
    }


def _h_mpeem(
    revenue, ebitda_margin, ebitda_growth, working_capital_pct, capex_pct, tax_rate, discount_rate, useful_life
):
    pv = 0.0
    steps = []
    rev = revenue
    for t in range(1, useful_life + 1):
        ebitda = rev * ebitda_margin
        wc_delta = rev * ebitda_margin * working_capital_pct
        capex = rev * capex_pct
        fcf = (ebitda - wc_delta - capex) * (1 - tax_rate)
        period_pv = fcf / ((1 + discount_rate) ** t)
        pv += period_pv
        steps.append(f"Period {t}: revenue=${rev:,.0f}, EBITDA=${ebitda:,.0f}, FCF=${fcf:,.0f}, PV=${period_pv:,.0f}")
        rev *= 1 + ebitda_growth
    return {
        "value": round(pv, 2),
        "method": "MPEEM",
        "formula_reference": "Ch 4: Multi-Period Excess Earnings Method",
        "steps": steps,
        "assumptions": ["Earnings attributable to the asset", "Contributory asset charges applied"],
    }


HARDCODED = {
    "present-value": _h_present_value,
    "future-value": _h_future_value,
    "annuity-pv": _h_annuity_pv,
    "perpetuity-pv": _h_perpetuity_pv,
    "terminal-value": _h_terminal_value,
    "build-up-discount-rate": _h_build_up,
    "capm": _h_capm,
    "wacc": _h_wacc,
    "relief-from-royalty": _h_rfr,
    "growing-annuity-pv": _h_growing_annuity_pv,
    "mpeem": _h_mpeem,
}


def _to_plain(result):
    """Convert ValuationResult (Pydantic model) to plain dict for JSON."""
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    if isinstance(result, dict):
        return result
    return {"value": result, "method": "unknown"}


ROUTES = {**HARDCODED, **_LIB_FUNCTIONS}


def _to_float_value(result) -> float:
    """Extract the numeric value from a ValuationResult or plain dict."""
    if hasattr(result, "value"):
        return result.value
    if isinstance(result, dict):
        return result.get("value")
    return result


def _resolve_valuation_fn(name):
    """Resolve a valuation function name to a callable returning a float.

    The Monte Carlo methods accept a ``valuation_fn`` callable that cannot be
    serialized over HTTP. Clients pass the function *name* (kebab-case slug or
    snake_case tool name) instead, and this resolver maps it to the registered
    engine function.
    """
    if callable(name):
        return name

    key = str(name).strip().replace("-", "_")
    func = ROUTES.get(key) or ROUTES.get(key.replace("_", "-"))
    if func is None:
        raise ValueError(f"Unsupported valuation function: {name}. Available: {sorted(ROUTES.keys())}")

    def _wrapper(*args, **kwargs):
        if args and isinstance(args[0], dict) and not kwargs:
            return _to_float_value(func(**args[0]))
        return _to_float_value(func(**kwargs))

    return _wrapper


def _mc_valuation_handler(**kwargs):
    from intangible_valuation.core.statistics import monte_carlo_valuation

    fn_name = kwargs.pop("valuation_fn")
    return monte_carlo_valuation(_resolve_valuation_fn(fn_name), **kwargs)


def _mc_sensitivity_handler(**kwargs):
    from intangible_valuation.advanced.monte_carlo import monte_carlo_sensitivity

    fn_name = kwargs.pop("valuation_fn")
    return monte_carlo_sensitivity(_resolve_valuation_fn(fn_name), **kwargs)


def _mc_correlation_handler(**kwargs):
    from intangible_valuation.core.statistics import monte_carlo_with_correlation

    fn_name = kwargs.pop("valuation_fn")
    return monte_carlo_with_correlation(_resolve_valuation_fn(fn_name), **kwargs)


# Monte Carlo methods take a callable ``valuation_fn`` that cannot be passed
# over JSON. Replace their route handlers with wrappers that accept a function
# *name* and resolve it server-side (only when the engine import succeeded).
for _slug, _handler in (
    ("monte-carlo-valuation", _mc_valuation_handler),
    ("monte-carlo-sensitivity", _mc_sensitivity_handler),
    ("monte-carlo-with-correlation", _mc_correlation_handler),
):
    if _slug in ROUTES:
        ROUTES[_slug] = _handler


def _normalize_slug(identifier: str) -> str:
    """Normalize a method identifier to its canonical kebab-case slug."""
    return identifier.strip().replace("_", "-")


def resolve_method(path: str, headers: dict, body: object | None = None) -> str | None:
    """Resolve the valuation method from header, body, then URL path.

    Precedence: ``X-Valuation-Method`` header -> ``body["method"]`` -> URL path.
    Identifiers are normalized snake_case -> kebab-case before lookup.
    Returns the normalized slug, or ``None`` when no method is determinable.
    """
    header_value = (headers.get("X-Valuation-Method") or "").strip()
    if header_value:
        return _normalize_slug(header_value)

    if isinstance(body, dict) and body.get("method"):
        return _normalize_slug(str(body["method"]))

    path_part = urlparse(path).path.rstrip("/")
    if "/api/" in path_part:
        path_part = path_part.split("/api/", 1)[1]
    path_part = path_part.lstrip("/")
    if path_part.startswith("valuation/"):
        path_part = path_part[len("valuation/") :]
    if path_part.endswith(".py"):
        path_part = path_part[:-3]
    if path_part in ("", "api", "index", "valuation"):
        return None
    return _normalize_slug(path_part)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode() if length else "{}"
            body = json.loads(raw_body) if raw_body else {}
        except (json.JSONDecodeError, ValueError):
            self._send(400, {"error": "Invalid JSON body"})
            return

        if not isinstance(body, dict):
            self._send(400, {"error": "Invalid JSON body: expected an object"})
            return

        method = resolve_method(self.path, self.headers, body)
        if not method:
            self._send(
                404,
                {"error": "No valuation method specified", "available": sorted(ROUTES.keys())},
            )
            return

        func = ROUTES.get(method)
        if not func:
            self._send(
                404,
                {
                    "error": f"Unknown method: '{method}'",
                    "available": sorted(ROUTES.keys()),
                    "library_methods": len(_LIB_FUNCTIONS),
                    "hardcoded_methods": len(HARDCODED),
                },
            )
            return

        kwargs = {k: v for k, v in body.items() if k != "method"}
        try:
            result = func(**kwargs)
            self._send(200, _to_plain(result))
        except TypeError as e:
            self._send(
                400,
                {
                    "error": f"Invalid parameters: {e}",
                    "expected_params": list(func.__code__.co_varnames[: func.__code__.co_argcount]),
                },
            )
        except Exception as e:
            self._send(400, {"error": str(e)})

    def do_GET(self):
        method = resolve_method(self.path, self.headers, None)
        if method:
            self._send(200, {"endpoint": method, "available": sorted(ROUTES.keys())})
        else:
            self._send(
                200,
                {
                    "status": "ok",
                    "endpoints": sorted(ROUTES.keys()),
                    "total_methods": len(ROUTES),
                    "library_methods": len(_LIB_FUNCTIONS),
                    "hardcoded_methods": len(HARDCODED),
                    "docs": "https://intangible-valuation.ascent-partners.com",
                },
            )

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
