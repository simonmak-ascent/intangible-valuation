"""Canonical MCP tool surface for the Intangible Valuation library.

Single source of truth for every MCP tool definition — descriptions,
parameter semantics, JSON Schemas, annotations, and dispatch. Both the
stdio server (``mcp_server/server.py``) and the hosted HTTP endpoint
(``api/index.py``) consume this module, so the two surfaces cannot drift.

Design notes (Glama / TDQS Tool Definition Quality Score):

* Tools are **folded by valuation family** (14 tools) rather than one tool
  per formula (49). TDQS scores *Tool Count Appropriateness* 5/5 only in
  the 3-15 band; a `method` enum selects the formula inside each tool.
* Every tool carries a ``title``, an ``outputSchema``, and MCP
  ``annotations``. All tools are pure calculators: read-only, idempotent,
  closed-world, non-destructive.
* Every parameter is documented here (name, type, meaning, units, default),
  which feeds the *Parameter Semantics* dimension.
* Purpose + when-to-use + a named alternative are written per tool, feeding
  *Purpose Clarity*, *Usage Guidelines*, and *Contextual Completeness*.
* The description omits a return-field enumeration (the output schema
  already documents it) to protect *Conciseness & Structure*.
"""

from __future__ import annotations

from typing import Any

# --------------------------------------------------------------------------
# Shared shape
# --------------------------------------------------------------------------

SERVER_NAME = "intangible-valuation"
SERVER_VERSION = "2.0.0"

#: Behaviour shared by every tool: pure arithmetic, no I/O.
COMMON_ANNOTATIONS: dict[str, Any] = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

#: Documented return shape so clients need not restate it.
OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "value": {"type": "number", "description": "Computed valuation, rate, or metric."},
        "method": {"type": "string", "description": "Formula / method name that produced the result."},
        "formula_reference": {"type": "string", "description": "Mathematical formula or reference applied."},
        "steps": {
            "type": "array",
            "items": {},
            "description": "Intermediate calculation steps for traceability (one string per step).",
        },
        "assumptions": {
            "description": "Modelling assumptions applied (list of strings or key/value object).",
        },
        "error": {"type": "string", "description": "Error message when the call fails."},
    },
    "required": ["value"],
}


# --------------------------------------------------------------------------
# Parameter vocabulary  (name -> json type + description + optional default).
# JSON types: number, integer, string, boolean, array:number, array:object, object.
# --------------------------------------------------------------------------

PARAMS: dict[str, dict[str, Any]] = {
    # time value
    "future_value": {"type": "number", "description": "Future cash amount to discount, in currency units."},
    "present_value": {"type": "number", "description": "Present amount to compound, in currency units."},
    "payment": {"type": "number", "description": "Recurring payment per period, in currency units."},
    "discount_rate": {"type": "number", "description": "Per-period discount rate as a decimal (0.10 = 10%)."},
    "periods": {"type": "integer", "description": "Number of periods n (non-negative)."},
    "growth_rate": {"type": "number", "description": "Per-period growth rate as a decimal (0.03 = 3%)."},
    "final_year_cashflow": {
        "type": "number",
        "description": "Final-year projected cash flow (FCF), in currency units.",
    },
    "perpetual_growth_rate": {
        "type": "number",
        "description": "Perpetual growth rate g as a decimal; must be below discount_rate for Gordon growth.",
    },
    "exit_multiple": {
        "type": "number",
        "description": "Exit multiple applied to the final-year cash flow (e.g. 8.0 for 8x).",
    },
    # discount rates
    "risk_free_rate": {"type": "number", "description": "Risk-free rate as a decimal (0.04 = 4%)."},
    "equity_risk_premium": {"type": "number", "description": "Equity risk premium as a decimal (0.06 = 6%)."},
    "size_premium": {"type": "number", "description": "Small-size premium as a decimal.", "default": 0.0},
    "industry_risk_premium": {"type": "number", "description": "Industry risk premium as a decimal.", "default": 0.0},
    "specific_risk_premium": {
        "type": "number",
        "description": "Company-specific risk premium as a decimal.",
        "default": 0.0,
    },
    "beta": {"type": "number", "description": "Systematic risk beta (market = 1.0)."},
    "market_return": {"type": "number", "description": "Expected market return as a decimal (0.10 = 10%)."},
    "equity_value": {"type": "number", "description": "Market value of equity E, in currency units."},
    "debt_value": {"type": "number", "description": "Market value of debt D, in currency units."},
    "cost_of_equity": {"type": "number", "description": "Cost of equity Re as a decimal."},
    "cost_of_debt": {"type": "number", "description": "Pre-tax cost of debt Rd as a decimal."},
    "tax_rate": {"type": "number", "description": "Marginal tax rate as a decimal (0.25 = 25%)."},
    "useful_life": {"type": "integer", "description": "Useful life in years n."},
    "asset_value": {
        "type": "number",
        "description": "Asset value the tax amortization benefit is computed on, in currency units.",
    },
    "minority_price": {
        "type": "number",
        "description": "Minority (pre-control) share price or value, in currency units.",
    },
    "control_price": {
        "type": "number",
        "description": "Controlling-interest share price or value, in currency units.",
    },
    "restricted_period": {"type": "number", "description": "Restricted / marketability period in years t."},
    "volatility": {"type": "number", "description": "Annualized volatility sigma as a decimal (0.30 = 30%)."},
    "base_rate": {
        "type": "number",
        "description": "Base discount rate before currency/country adjustment, as a decimal.",
    },
    "currency_risk_premium": {"type": "number", "description": "Currency risk premium as a decimal.", "default": 0.0},
    "country_risk_premium": {"type": "number", "description": "Country risk premium as a decimal.", "default": 0.0},
    # cost approach
    "development_costs": {
        "type": "object",
        "description": 'Cost breakdown by category, e.g. {"r_and_d": 1000000, "testing": 250000}, in currency units.',
    },
    "obsolescence_factors": {
        "type": "object",
        "description": 'Obsolescence factors, e.g. {"functional": 0.10, "technological": 0.15, "economic": 0.05}.',
    },
    "current_cost": {
        "type": "number",
        "description": "Current cost to replace the asset with equivalent utility, in currency units.",
    },
    # market approach
    "comparables": {
        "type": "array:object",
        "description": "Comparable transactions, each {revenue, multiple}.",
    },
    "subject_revenue": {"type": "number", "description": "Subject company revenue, in currency units."},
    "adjustments": {
        "type": "object",
        "description": 'Optional multiplicative adjustments, e.g. {"size": 0.9, "growth": 1.1}.',
    },
    "revenue": {"type": "number", "description": "Annual revenue attributable to the asset, in currency units."},
    "royalty_rate": {"type": "number", "description": "Royalty rate as a decimal (0.05 = 5% of revenue)."},
    # income methods
    "revenue_projections": {
        "type": "array:number",
        "description": "Projected revenue per period t=1..n, in currency units.",
    },
    "tab_enabled": {
        "type": "boolean",
        "description": "Whether to include the tax amortization benefit in the result.",
        "default": True,
    },
    "cash_flow_projections": {
        "type": "array:number",
        "description": "Projected after-tax cash flows per period t=1..n, in currency units.",
    },
    "contributory_asset_charges": {
        "type": "array:number",
        "description": "Contributory asset charge per period t=1..n, in currency units.",
    },
    "normalized_earnings": {"type": "number", "description": "Single-period normalized earnings, in currency units."},
    "capitalization_rate": {"type": "number", "description": "Capitalization rate as a decimal (0.15 = 15%)."},
    "cash_flows_with": {
        "type": "array:number",
        "description": "Cash flows per period with the asset, in currency units.",
    },
    "cash_flows_without": {
        "type": "array:number",
        "description": "Cash flows per period without the asset, in currency units.",
    },
    "assets": {
        "type": "array:object",
        "description": "Contributory assets, each {value, return_rate}.",
    },
    # IP
    "remaining_life": {"type": "integer", "description": "Remaining legal/economic life of the patent in years."},
    "probability_of_success": {
        "type": "number",
        "description": "Probability of technical and commercial success, in [0,1].",
    },
    "comparable_license_rates": {
        "type": "array:number",
        "description": "Comparable license royalty rates as decimals.",
    },
    "profit_margin": {"type": "number", "description": "Profit margin as a decimal (0.20 = 20%)."},
    "brand_strength_index": {
        "type": "number",
        "description": "Brand strength index on a 0-100 scale (75 = strong).",
    },
    "brand_method": {
        "type": "string",
        "description": (
            "Trademark method: relief_from_royalty adjusts the royalty rate by brand strength; "
            "excess_earnings capitalizes excess earnings."
        ),
        "enum": ["relief_from_royalty", "excess_earnings"],
    },
    "projected_revenue": {
        "type": "number",
        "description": "Projected annual revenue subject to the copyright royalty, in currency units.",
    },
    "development_cost": {"type": "number", "description": "Development or acquisition cost, in currency units."},
    "economic_life": {"type": "integer", "description": "Economic life in years."},
    "competitive_advantage_period": {
        "type": "integer",
        "description": "Years the competitive advantage is expected to persist.",
    },
    "secrecy_probability": {
        "type": "number",
        "description": "Probability the trade secret remains secret, in [0,1].",
    },
    # technology
    "rd_costs": {"type": "number", "description": "Cumulative research and development costs, in currency units."},
    "life_cycle_stage": {"type": "string", "description": 'Life-cycle stage, e.g. "growth", "mature", "decline".'},
    "competitive_advantage": {"type": "integer", "description": "Years of competitive advantage."},
    "maintenance_cost": {"type": "number", "description": "Annual maintenance cost, in currency units."},
    "user_base": {"type": "integer", "description": "Number of users."},
    "revenue_model": {
        "type": "object",
        "description": 'Revenue model, e.g. {"subscription_price": 20, "paying_users": 10000}.',
    },
    "acquisition_cost": {"type": "number", "description": "Cost to acquire the data, in currency units."},
    "quality_score": {"type": "number", "description": "Data quality score, in [0,1]."},
    "revenue_contribution": {"type": "number", "description": "Annual revenue contribution, in currency units."},
    "network_size": {"type": "integer", "description": "Number of network participants."},
    "network_effects_coefficient": {
        "type": "number",
        "description": "Network-effects coefficient scaling revenue with network size.",
    },
    "revenue_per_user": {"type": "number", "description": "Revenue per user, in currency units."},
    # customer
    "customer_count": {"type": "integer", "description": "Number of customers."},
    "avg_revenue_per_customer": {
        "type": "number",
        "description": "Average annual revenue per customer, in currency units.",
    },
    "retention_rate": {"type": "number", "description": "Annual customer retention rate, in [0,1]."},
    "projection_period": {"type": "integer", "description": "Projection horizon in years."},
    "channel_count": {"type": "integer", "description": "Number of distribution channels."},
    "revenue_per_channel": {"type": "number", "description": "Annual revenue per channel, in currency units."},
    "channel_margin": {"type": "number", "description": "Channel profit margin as a decimal."},
    "protected_revenue": {
        "type": "number",
        "description": "Annual revenue protected by the non-compete, in currency units.",
    },
    "term": {"type": "integer", "description": "Non-compete term in years."},
    "enforcement_probability": {
        "type": "number",
        "description": "Probability the non-compete is enforceable, in [0,1].",
    },
    # human capital
    "employee_count": {"type": "integer", "description": "Number of employees."},
    "avg_replacement_cost": {
        "type": "number",
        "description": "Average cost to replace one employee, in currency units.",
    },
    "training_cost": {"type": "number", "description": "Training cost per employee, in currency units."},
    "productivity_factor": {"type": "number", "description": "Productivity factor on replacement cost (1.0 = parity)."},
    "attrition_rate": {"type": "number", "description": "Annual attrition rate, in [0,1]."},
    "replacement_cost": {"type": "number", "description": "Cost to replace the key person, in currency units."},
    "departure_probability": {
        "type": "number",
        "description": "Annual probability the key person departs, in [0,1].",
    },
    # goodwill & PPA
    "purchase_price": {"type": "number", "description": "Total consideration / purchase price, in currency units."},
    "fair_value_net_identifiable_assets": {
        "type": "number",
        "description": "Fair value of net identifiable assets, in currency units.",
    },
    "tangible_assets_fv": {"type": "number", "description": "Fair value of tangible assets, in currency units."},
    "identified_intangibles": {
        "type": "array:object",
        "description": "Identified intangibles, each {name, value} or {name, fair_value}.",
    },
    "liabilities_fv": {
        "type": "number",
        "description": "Fair value of assumed liabilities, in currency units.",
        "default": 0,
    },
    "asset_type": {
        "type": "string",
        "description": 'Asset type, e.g. "patent", "trademark", "software", "customer_list".',
    },
    "legal_life": {
        "type": "number",
        "description": "Legal protection period in years (overrides the asset-type default).",
    },
    "economic_factors": {
        "type": "object",
        "description": 'Economic adjustment factors, e.g. {"market_growth": 0.05, "competition": 0.4, "tech_change": 0.1}.',
    },
    "obsolescence_rate": {
        "type": "number",
        "description": "Annual obsolescence rate as a decimal.",
        "default": 0.05,
    },
    # impairment
    "carrying_value": {
        "type": "number",
        "description": "Carrying value of the reporting unit or asset, in currency units.",
    },
    "fair_value": {"type": "number", "description": "Fair value of the reporting unit or asset, in currency units."},
    "reporting_unit": {"type": "string", "description": "Reporting unit name (goodwill only)."},
    "standard": {
        "type": "string",
        "description": "Accounting standard: ASC350 for US GAAP, IAS36 for IFRS.",
        "enum": ["ASC350", "IAS36"],
    },
    "recoverable_amount": {"type": "number", "description": "Recoverable amount (IAS 36), in currency units."},
    # royalty analysis
    "ip_type": {
        "type": "string",
        "description": 'Intellectual-property type, e.g. "patent", "trademark", "copyright", "trade_secret".',
    },
    "industry": {"type": "string", "description": 'Industry, e.g. "software", "pharmaceutical".'},
    "comparable_database": {
        "type": "array:object",
        "description": "Optional comparable licenses, each {rate} or {royalty_rate}.",
    },
    "base_royalty_rate": {
        "type": "number",
        "description": "Base royalty rate before adjustment, as a decimal (0.05 = 5%).",
    },
    "adjustment_factors": {
        "type": "object",
        "description": 'Multiplicative adjustment factors, e.g. {"profitability": 1.1, "market": 0.9}.',
    },
    "licensee_expected_profit": {"type": "number", "description": "Licensee expected profit, in currency units."},
    "profit_attribution_to_ip": {
        "type": "number",
        "description": "Fraction of profit attributable to the IP, in [0,1].",
        "default": 1.0,
    },
    # compliance
    "controlled_price": {"type": "number", "description": "Intercompany (controlled) price, in currency units."},
    "uncontrolled_prices": {
        "type": "array:number",
        "description": "Comparable uncontrolled prices, in currency units.",
    },
    "lost_profits_or_royalty": {
        "type": "number",
        "description": "Annual lost profits or reasonable royalty, in currency units.",
    },
    "infringement_period": {"type": "integer", "description": "Infringement period in years."},
    "prejudgment_interest_rate": {"type": "number", "description": "Pre-judgment interest rate as a decimal."},
    # simulation
    "input_distributions": {
        "type": "array:object",
        "description": (
            "Inputs to simulate, each {name, distribution, params}; distribution is "
            "normal (mean, std), uniform (low, high) or triangular (low, high, mode)."
        ),
    },
    "iterations": {
        "type": "integer",
        "description": "Simulation iterations; monte_carlo_sensitivity requires 1000-100000.",
        "default": 10000,
    },
    "seed": {"type": "integer", "description": "Random seed for reproducible simulations."},
    "base_params": {
        "type": "object",
        "description": "Base values for all parameters, including those held fixed.",
    },
    "distributions": {
        "type": "object",
        "description": "Map of parameter name to {distribution, params} for the simulated inputs.",
    },
    "tree": {
        "type": "object",
        "description": 'Decision tree {"nodes": [...], "edges": [...]}; node types decision, chance, terminal.',
    },
    "function_name": {
        "type": "string",
        "description": 'Core function to vary, e.g. "present_value", "capm_discount_rate", "wacc".',
    },
    "parameter_name": {"type": "string", "description": "Name of the parameter to vary."},
    "parameter_range": {"type": "array:number", "description": "Values to test for the varied parameter."},
    "fixed_parameters": {"type": "object", "description": "Values for all other parameters, held constant."},
}


# --------------------------------------------------------------------------
# Tool families  (49 formulas folded into 14 method-switched tools)
# --------------------------------------------------------------------------


def _method(
    key: str,
    summary: str,
    module: str,
    function: str,
    args: dict[str, str] | None = None,
    opt: dict[str, str] | None = None,
    inject: dict[str, Any] | None = None,
    adapter: str | None = None,
) -> dict[str, Any]:
    m: dict[str, Any] = {
        "key": key,
        "summary": summary,
        "module": module,
        "function": function,
        "args": args or {},
        "opt": opt or {},
    }
    if inject:
        m["inject"] = inject
    if adapter:
        m["adapter"] = adapter
    return m


TOOLS: list[dict[str, Any]] = [
    {
        "name": "valuation_time_value",
        "title": "Time Value of Money",
        "tags": ["time-value", "dcf", "terminal-value"],
        "purpose": (
            "Time value of money: discount or compound a single sum, value level and growing annuities "
            "and perpetuities, and compute a terminal value by Gordon growth or exit multiple."
        ),
        "use": (
            "Use to move cash flows through time or to value a terminal value in a DCF; combine with a "
            "rate from valuation_discount_rate."
        ),
        "alt": (
            "For uneven multi-period cash flows use valuation_income_methods; for rate construction use "
            "valuation_discount_rate."
        ),
        "constraints": (
            "Rates and growth are decimals (0.10 = 10%); for terminal_value_gordon_growth the discount rate must "
            "exceed the perpetual growth rate."
        ),
        "methods": [
            _method(
                "present_value",
                "PV = FV / (1 + r)^n.",
                "intangible_valuation.core.time_value",
                "present_value",
                {"future_value": "future_value", "discount_rate": "discount_rate", "periods": "periods"},
            ),
            _method(
                "future_value",
                "FV = PV * (1 + r)^n.",
                "intangible_valuation.core.time_value",
                "future_value",
                {"present_value": "present_value", "discount_rate": "discount_rate", "periods": "periods"},
            ),
            _method(
                "annuity_pv",
                "PV = PMT * [1 - (1 + r)^-n] / r.",
                "intangible_valuation.core.time_value",
                "annuity_pv",
                {"payment": "payment", "discount_rate": "discount_rate", "periods": "periods"},
            ),
            _method(
                "perpetuity_pv",
                "PV = PMT / r.",
                "intangible_valuation.core.time_value",
                "perpetuity_pv",
                {"payment": "payment", "discount_rate": "discount_rate"},
            ),
            _method(
                "growing_annuity_pv",
                "PV of a constant-growth annuity.",
                "intangible_valuation.core.time_value",
                "growing_annuity_pv",
                {
                    "payment": "payment",
                    "discount_rate": "discount_rate",
                    "growth_rate": "growth_rate",
                    "periods": "periods",
                },
            ),
            _method(
                "terminal_value_gordon_growth",
                "TV = FCF * (1 + g) / (r - g).",
                "intangible_valuation.core.time_value",
                "terminal_value",
                {
                    "final_year_cashflow": "final_year_cashflow",
                    "perpetual_growth_rate": "perpetual_growth_rate",
                    "discount_rate": "discount_rate",
                },
                inject={"method": "gordon_growth"},
            ),
            _method(
                "terminal_value_exit_multiple",
                "TV = FCF * exit multiple.",
                "intangible_valuation.core.time_value",
                "terminal_value",
                {"final_year_cashflow": "final_year_cashflow", "exit_multiple": "exit_multiple"},
                inject={"method": "exit_multiple", "perpetual_growth_rate": 0.0, "discount_rate": 0.0},
            ),
        ],
    },
    {
        "name": "valuation_discount_rate",
        "title": "Discount & Capitalization Rates",
        "tags": ["discount-rate", "capm", "wacc", "dlom"],
        "purpose": (
            "Construct discount and capitalization rates: build-up, CAPM, WACC, tax-amortization benefit, "
            "control premium, Finnerty DLOM, and currency/country-risk adjustment."
        ),
        "use": (
            "Use to derive the rate that feeds every income-based method; build_up and capm estimate cost of "
            "equity, wacc blends debt and equity."
        ),
        "alt": (
            "For a cross-border rate with currency and country premia use method currency_adjusted; for the "
            "cash flows the rate discounts use valuation_time_value."
        ),
        "constraints": (
            "All rates and premiums are decimals; wacc requires both equity_value and debt_value, and "
            "dlom_finnerty volatility is an annualized decimal."
        ),
        "methods": [
            _method(
                "build_up",
                "r = Rf + ERP + size + industry + specific premiums.",
                "intangible_valuation.core.discount_rates",
                "build_up_discount_rate",
                {"risk_free_rate": "risk_free_rate", "equity_risk_premium": "equity_risk_premium"},
                {
                    "size_premium": "size_premium",
                    "industry_risk_premium": "industry_risk_premium",
                    "specific_risk_premium": "specific_risk_premium",
                },
            ),
            _method(
                "capm",
                "r = Rf + beta * (Rm - Rf).",
                "intangible_valuation.core.discount_rates",
                "capm_discount_rate",
                {"risk_free_rate": "risk_free_rate", "beta": "beta", "market_return": "market_return"},
            ),
            _method(
                "wacc",
                "WACC = (E/V) Re + (D/V) Rd (1 - Tc).",
                "intangible_valuation.core.discount_rates",
                "wacc",
                {
                    "equity_value": "equity_value",
                    "debt_value": "debt_value",
                    "cost_of_equity": "cost_of_equity",
                    "cost_of_debt": "cost_of_debt",
                    "tax_rate": "tax_rate",
                },
            ),
            _method(
                "tax_amortization_benefit",
                "PV of the tax shield from amortizing the asset.",
                "intangible_valuation.core.discount_rates",
                "tax_amortization_benefit",
                {
                    "discount_rate": "discount_rate",
                    "useful_life": "useful_life",
                    "tax_rate": "tax_rate",
                    "asset_value": "asset_value",
                },
            ),
            _method(
                "control_premium",
                "(Control price - minority price) / minority price.",
                "intangible_valuation.core.discount_rates",
                "control_premium",
                {"minority_price": "minority_price", "control_price": "control_price"},
            ),
            _method(
                "dlom_finnerty",
                "Finnerty average-strike put option DLOM.",
                "intangible_valuation.core.discount_rates",
                "dlom_finnerty",
                {
                    "restricted_period": "restricted_period",
                    "volatility": "volatility",
                    "risk_free_rate": "risk_free_rate",
                },
            ),
            _method(
                "currency_adjusted",
                "r = base rate + currency premium + country premium.",
                "intangible_valuation.core.discount_rates",
                "currency_adjusted_discount_rate",
                {"base_rate": "base_rate"},
                {"currency_risk_premium": "currency_risk_premium", "country_risk_premium": "country_risk_premium"},
            ),
        ],
    },
    {
        "name": "valuation_cost_approach",
        "title": "Cost Approach",
        "tags": ["cost-approach", "reproduction", "replacement"],
        "purpose": (
            "Cost approach: depreciated reproduction cost from a cost breakdown and depreciated replacement "
            "cost with equivalent utility, both reduced by obsolescence."
        ),
        "use": (
            "Use when no income or market evidence exists, or to corroborate income and market indications for "
            "internally developed intangibles."
        ),
        "alt": (
            "For income-based indications use valuation_income_methods; for market evidence use "
            "valuation_market_approach."
        ),
        "methods": [
            _method(
                "reproduction_cost",
                "Sum of cost categories less total obsolescence.",
                "intangible_valuation.approaches.cost_approach",
                "reproduction_cost",
                {"development_costs": "development_costs"},
                {"obsolescence_factors": "obsolescence_factors"},
            ),
            _method(
                "replacement_cost",
                "Current cost of equivalent utility less obsolescence.",
                "intangible_valuation.approaches.cost_approach",
                "replacement_cost",
                {"current_cost": "current_cost"},
                {"obsolescence_factors": "obsolescence_factors"},
            ),
        ],
        "constraints": (
            "obsolescence_factors values are decimals that are summed and applied to the cost base; omit them "
            "for no obsolescence."
        ),
    },
    {
        "name": "valuation_market_approach",
        "title": "Market Approach",
        "tags": ["market-approach", "comparables", "royalty-capitalization"],
        "purpose": (
            "Market approach: value from comparable transaction revenue multiples or capitalize a royalty "
            "stream into a perpetuity value."
        ),
        "use": "Use when reliable comparable transactions or royalty rates exist for the subject asset.",
        "alt": (
            "For income-based excess earnings use valuation_income_methods; for royalty-rate selection and "
            "adjustment use valuation_royalty_analysis."
        ),
        "constraints": (
            "Each comparable is {revenue, multiple}; comparable_transactions applies the comparable multiple to "
            "subject_revenue."
        ),
        "methods": [
            _method(
                "comparable_transactions",
                "Subject revenue times the median comparable multiple.",
                "intangible_valuation.approaches.market_approach",
                "market_approach_comparables",
                {"comparables": "comparables", "subject_revenue": "subject_revenue"},
                {"adjustments": "adjustments"},
            ),
            _method(
                "royalty_capitalization",
                "Value = (revenue * royalty rate) / discount rate.",
                "intangible_valuation.approaches.market_approach",
                "royalty_capitalization",
                {"revenue": "revenue", "royalty_rate": "royalty_rate", "discount_rate": "discount_rate"},
            ),
        ],
    },
    {
        "name": "valuation_income_methods",
        "title": "Income Methods",
        "tags": ["income-approach", "relief-from-royalty", "mpeem", "excess-earnings"],
        "purpose": (
            "Income approach: relief from royalty, multi-period and single-period excess earnings, incremental "
            "cash flow, and contributory asset charges."
        ),
        "use": (
            "Use for the income-approach arithmetic: relief_from_royalty for IP with observable royalty rates, "
            "and excess earnings (mpeem or single_period_excess_earnings) for the residual intangible. For a "
            "complete asset-specific valuation of customer, technology, IP or workforce assets, prefer the "
            "dedicated valuation_customer, valuation_technology, valuation_ip and valuation_human_capital tools."
        ),
        "alt": (
            "For royalty-rate inputs use valuation_royalty_analysis; for asset-specific income valuations use "
            "valuation_customer, valuation_technology, valuation_ip or valuation_human_capital; for cost or "
            "market indications use valuation_cost_approach and valuation_market_approach."
        ),
        "methods": [
            _method(
                "relief_from_royalty",
                "PV of after-tax royalties avoided by ownership.",
                "intangible_valuation.income_methods.relief_from_royalty",
                "relief_from_royalty",
                {
                    "revenue_projections": "revenue_projections",
                    "royalty_rate": "royalty_rate",
                    "discount_rate": "discount_rate",
                    "tax_rate": "tax_rate",
                    "useful_life": "useful_life",
                },
                {"tab_enabled": "tab_enabled"},
            ),
            _method(
                "mpeem",
                "PV of excess earnings after contributory asset charges.",
                "intangible_valuation.income_methods.excess_earnings",
                "mpeem",
                {
                    "cash_flow_projections": "cash_flow_projections",
                    "contributory_asset_charges": "contributory_asset_charges",
                    "discount_rate": "discount_rate",
                    "tax_rate": "tax_rate",
                },
                {"tab_enabled": "tab_enabled"},
            ),
            _method(
                "single_period_excess_earnings",
                "Capitalize one period of excess earnings.",
                "intangible_valuation.income_methods.excess_earnings",
                "single_period_excess_earnings",
                {
                    "normalized_earnings": "normalized_earnings",
                    "contributory_asset_charges": "contributory_asset_charges",
                    "capitalization_rate": "capitalization_rate",
                },
            ),
            _method(
                "incremental_cashflow",
                "PV of cash flows with the asset minus without it.",
                "intangible_valuation.income_methods.incremental_cashflow",
                "incremental_cashflow",
                {
                    "cash_flows_with": "cash_flows_with",
                    "cash_flows_without": "cash_flows_without",
                    "discount_rate": "discount_rate",
                },
            ),
            _method(
                "contributory_asset_charges",
                "Total contributory asset charges.",
                "intangible_valuation.income_methods.excess_earnings",
                "contributory_asset_charges",
                {"assets": "assets"},
            ),
        ],
        "constraints": (
            "cash_flow_projections and contributory_asset_charges must be period-aligned; cash_flows_with and "
            "cash_flows_without must be equal length."
        ),
    },
    {
        "name": "valuation_ip",
        "title": "Intellectual Property",
        "tags": ["ip", "patent", "trademark", "copyright", "trade-secret"],
        "purpose": (
            "Intellectual property: risk-adjusted patent value, trademark/brand value, copyright income value, "
            "and trade-secret value under secrecy risk."
        ),
        "use": (
            "Use to value a specific IP right; patent weights projected cash flows by probability of success, "
            "trademark uses brand strength to set the royalty."
        ),
        "alt": (
            "For technology, software, data, and platform assets use valuation_technology; for customer and "
            "workforce assets use valuation_customer and valuation_human_capital."
        ),
        "methods": [
            _method(
                "patent",
                "Risk-adjusted DCF over the patent's remaining life.",
                "intangible_valuation.asset_types.ip_valuation",
                "patent_valuation",
                {
                    "remaining_life": "remaining_life",
                    "cash_flow_projections": "cash_flow_projections",
                    "probability_of_success": "probability_of_success",
                    "discount_rate": "discount_rate",
                },
                {"comparable_license_rates": "comparable_license_rates"},
            ),
            _method(
                "trademark",
                "Brand value by relief-from-royalty or excess earnings.",
                "intangible_valuation.asset_types.brand_valuation",
                "trademark_valuation",
                {
                    "revenue": "revenue",
                    "profit_margin": "profit_margin",
                    "brand_strength_index": "brand_strength_index",
                    "discount_rate": "discount_rate",
                    "useful_life": "useful_life",
                },
                {"method": "brand_method"},
            ),
            _method(
                "copyright",
                "PV of expected copyright royalty income.",
                "intangible_valuation.asset_types.ip_valuation",
                "copyright_valuation",
                {
                    "projected_revenue": "projected_revenue",
                    "useful_life": "useful_life",
                    "discount_rate": "discount_rate",
                    "royalty_rate": "royalty_rate",
                },
            ),
            _method(
                "trade_secret",
                "Value under secrecy risk over the economic life.",
                "intangible_valuation.asset_types.ip_valuation",
                "trade_secret_valuation",
                {
                    "development_cost": "development_cost",
                    "economic_life": "economic_life",
                    "competitive_advantage_period": "competitive_advantage_period",
                    "discount_rate": "discount_rate",
                    "secrecy_probability": "secrecy_probability",
                },
            ),
        ],
        "constraints": "cash_flow_projections for patent run over remaining_life.",
    },
    {
        "name": "valuation_technology",
        "title": "Technology Assets",
        "tags": ["technology", "software", "data", "platform"],
        "purpose": (
            "Technology assets: developed technology under life-cycle risk, software under cost and income, "
            "data assets with a quality adjustment, and platforms with network effects."
        ),
        "use": (
            "Use for developed technology, software, data, and platform intangibles; developed_technology and "
            "software blend cost and income evidence."
        ),
        "alt": (
            "For patents, trademarks, copyrights, and trade secrets use valuation_ip; for customer "
            "relationships use valuation_customer."
        ),
        "methods": [
            _method(
                "developed_technology",
                "Cost and income value adjusted for life-cycle stage.",
                "intangible_valuation.asset_types.technology_valuation",
                "developed_technology_valuation",
                {
                    "rd_costs": "rd_costs",
                    "life_cycle_stage": "life_cycle_stage",
                    "competitive_advantage": "competitive_advantage",
                    "discount_rate": "discount_rate",
                    "cash_flow_projections": "cash_flow_projections",
                },
            ),
            _method(
                "software",
                "Software value from development, maintenance, and revenue.",
                "intangible_valuation.asset_types.technology_valuation",
                "software_valuation",
                {
                    "development_cost": "development_cost",
                    "maintenance_cost": "maintenance_cost",
                    "user_base": "user_base",
                    "revenue_model": "revenue_model",
                    "useful_life": "useful_life",
                    "discount_rate": "discount_rate",
                },
            ),
            _method(
                "data_asset",
                "Quality-adjusted revenue contribution plus acquisition cost.",
                "intangible_valuation.asset_types.technology_valuation",
                "data_asset_valuation",
                {
                    "acquisition_cost": "acquisition_cost",
                    "quality_score": "quality_score",
                    "revenue_contribution": "revenue_contribution",
                    "useful_life": "useful_life",
                    "discount_rate": "discount_rate",
                },
            ),
            _method(
                "platform",
                "Network-effect revenue grown and discounted.",
                "intangible_valuation.asset_types.technology_valuation",
                "platform_valuation",
                {
                    "network_size": "network_size",
                    "network_effects_coefficient": "network_effects_coefficient",
                    "revenue_per_user": "revenue_per_user",
                    "growth_rate": "growth_rate",
                    "discount_rate": "discount_rate",
                },
            ),
        ],
        "constraints": "cash_flow_projections for developed_technology run over the remaining useful life.",
    },
    {
        "name": "valuation_customer",
        "title": "Customer-Related Assets",
        "tags": ["customer", "distribution", "non-compete"],
        "purpose": (
            "Customer-related intangibles: customer relationships with attrition, distribution networks by "
            "channel profitability, and non-compete agreements on protected profits."
        ),
        "use": (
            "Use for customer relationships, distribution networks, and non-compete assets; "
            "customer_relationships projects multi-period revenue with a retention rate."
        ),
        "alt": (
            "For the workforce and key-person assets use valuation_human_capital; for technology assets use "
            "valuation_technology."
        ),
        "constraints": (
            "retention_rate and enforcement_probability are in [0,1]; projection_period sets the number of "
            "discounted periods."
        ),
        "methods": [
            _method(
                "customer_relationships",
                "Multi-period revenue net of attrition, discounted.",
                "intangible_valuation.asset_types.customer_valuation",
                "customer_relationship_valuation",
                {
                    "customer_count": "customer_count",
                    "avg_revenue_per_customer": "avg_revenue_per_customer",
                    "retention_rate": "retention_rate",
                    "profit_margin": "profit_margin",
                    "discount_rate": "discount_rate",
                    "projection_period": "projection_period",
                },
            ),
            _method(
                "distribution_network",
                "Channel revenue times margin over the useful life.",
                "intangible_valuation.asset_types.customer_valuation",
                "distribution_network_valuation",
                {
                    "channel_count": "channel_count",
                    "revenue_per_channel": "revenue_per_channel",
                    "channel_margin": "channel_margin",
                    "useful_life": "useful_life",
                    "discount_rate": "discount_rate",
                },
            ),
            _method(
                "non_compete",
                "Protected profit under an enforcement probability, discounted.",
                "intangible_valuation.asset_types.customer_valuation",
                "non_compete_valuation",
                {
                    "protected_revenue": "protected_revenue",
                    "profit_margin": "profit_margin",
                    "term": "term",
                    "enforcement_probability": "enforcement_probability",
                    "discount_rate": "discount_rate",
                },
            ),
        ],
    },
    {
        "name": "valuation_human_capital",
        "title": "Human Capital",
        "tags": ["human-capital", "assembled-workforce", "key-person"],
        "purpose": (
            "Human capital: assembled-workforce value by replacement cost and key-person value from revenue "
            "contribution and departure risk."
        ),
        "use": (
            "Use for assembled workforce and key-person intangibles; assembled_workforce nets training and "
            "attrition into a replacement cost."
        ),
        "alt": ("For customer-related assets use valuation_customer; for technology assets use valuation_technology."),
        "constraints": ("attrition_rate is in [0,1]; productivity_factor scales the replacement cost (1.0 = parity)."),
        "methods": [
            _method(
                "assembled_workforce",
                "Replacement cost including training, net of attrition.",
                "intangible_valuation.asset_types.human_capital",
                "assembled_workforce_valuation",
                {
                    "employee_count": "employee_count",
                    "avg_replacement_cost": "avg_replacement_cost",
                    "training_cost": "training_cost",
                    "productivity_factor": "productivity_factor",
                    "attrition_rate": "attrition_rate",
                },
            ),
            _method(
                "key_person",
                "Revenue contribution and replacement cost under departure risk.",
                "intangible_valuation.asset_types.human_capital",
                "key_person_value",
                {
                    "revenue_contribution": "revenue_contribution",
                    "replacement_cost": "replacement_cost",
                    "departure_probability": "departure_probability",
                    "discount_rate": "discount_rate",
                },
            ),
        ],
    },
    {
        "name": "valuation_goodwill_ppa",
        "title": "Goodwill & Purchase Price Allocation",
        "tags": ["goodwill", "ppa", "asc-805", "ifrs-3", "useful-life"],
        "purpose": (
            "Goodwill and purchase price allocation: goodwill as the residual, a full PPA waterfall across "
            "identified intangibles, and useful-life estimation."
        ),
        "use": (
            "Use for ASC 805 / IFRS 3 business combinations; purchase_price_allocation allocates consideration "
            "to identified intangibles with the remainder to goodwill."
        ),
        "alt": (
            "For subsequent goodwill and intangible impairment testing use valuation_impairment; for individual "
            "intangible fair values feed valuation_ip, valuation_technology or valuation_customer into the "
            "allocation."
        ),
        "methods": [
            _method(
                "goodwill",
                "Goodwill = purchase price - fair value of net identifiable assets.",
                "intangible_valuation.advanced.goodwill",
                "goodwill",
                {
                    "purchase_price": "purchase_price",
                    "fair_value_net_identifiable_assets": "fair_value_net_identifiable_assets",
                },
            ),
            _method(
                "purchase_price_allocation",
                "Allocate consideration across identified intangibles.",
                "intangible_valuation.advanced.purchase_price_alloc",
                "purchase_price_allocation",
                {
                    "purchase_price": "purchase_price",
                    "tangible_assets_fv": "tangible_assets_fv",
                    "identified_intangibles": "identified_intangibles",
                },
                {"liabilities_fv": "liabilities_fv"},
            ),
            _method(
                "useful_life",
                "Estimate economic/legal useful life of an intangible.",
                "intangible_valuation.utils.formulas",
                "estimate_useful_life",
                {"asset_type": "asset_type"},
                {
                    "legal_life": "legal_life",
                    "economic_factors": "economic_factors",
                    "obsolescence_rate": "obsolescence_rate",
                },
            ),
        ],
        "constraints": (
            "identified_intangibles values are summed before goodwill is taken as the residual; liabilities_fv "
            "reduces net identifiable assets."
        ),
    },
    {
        "name": "valuation_impairment",
        "title": "Impairment Testing",
        "tags": ["impairment", "asc-350", "ias-36", "goodwill"],
        "purpose": (
            "Impairment testing: goodwill impairment and intangible impairment under US GAAP (ASC 350) or IFRS "
            "(IAS 36)."
        ),
        "use": (
            "Use for annual or triggering-event impairment testing; goodwill_impairment compares a reporting "
            "unit's carrying value with its fair value."
        ),
        "alt": (
            "To compute the initial goodwill or allocation use valuation_goodwill_ppa; for the underlying asset "
            "fair values use the relevant asset-type tool."
        ),
        "methods": [
            _method(
                "goodwill_impairment",
                "Impairment = carrying value - fair value (if positive).",
                "intangible_valuation.advanced.impairment_testing",
                "goodwill_impairment_test",
                {"carrying_value": "carrying_value", "fair_value": "fair_value"},
                {"reporting_unit": "reporting_unit", "standard": "standard"},
            ),
            _method(
                "intangible_impairment",
                "Impairment of an intangible under ASC 350 or IAS 36.",
                "intangible_valuation.advanced.impairment_testing",
                "intangible_impairment_test",
                {"carrying_value": "carrying_value"},
                {"fair_value": "fair_value", "recoverable_amount": "recoverable_amount", "standard": "standard"},
            ),
        ],
        "constraints": "fair_value is required for ASC350; recoverable_amount is required for IAS36.",
    },
    {
        "name": "valuation_royalty_analysis",
        "title": "Royalty Rate Analysis",
        "tags": ["royalty", "benchmark", "25-percent-rule"],
        "purpose": (
            "Royalty analysis: benchmark royalty-rate ranges by IP type and industry, adjust a base rate for "
            "deal factors, and apply the 25% rule of thumb."
        ),
        "use": (
            "Use to select and support a royalty rate before a relief-from-royalty or royalty-capitalization valuation."
        ),
        "alt": (
            "To apply the chosen rate in a valuation use valuation_income_methods (relief_from_royalty) or "
            "valuation_market_approach (royalty_capitalization); for transfer-pricing pricing use "
            "valuation_compliance."
        ),
        "methods": [
            _method(
                "benchmark",
                "Benchmark royalty-rate range by IP type and industry.",
                "intangible_valuation.advanced.royalty_benchmark",
                "royalty_rate_benchmark",
                {"ip_type": "ip_type", "industry": "industry"},
                {"comparable_database": "comparable_database"},
            ),
            _method(
                "adjust",
                "Adjusted rate = base rate * product of factors.",
                "intangible_valuation.advanced.royalty_benchmark",
                "adjust_royalty_rate",
                {"base_rate": "base_royalty_rate", "adjustment_factors": "adjustment_factors"},
            ),
            _method(
                "twenty_five_percent_rule",
                "Royalty = licensee profit * IP attribution * 25%.",
                "intangible_valuation.advanced.royalty_benchmark",
                "twenty_five_percent_rule",
                {"licensee_expected_profit": "licensee_expected_profit"},
                {"profit_attribution_to_ip": "profit_attribution_to_ip"},
            ),
        ],
        "constraints": "adjustment_factors multiply the base rate, so values above 1.0 raise the rate.",
    },
    {
        "name": "valuation_simulation",
        "title": "Uncertainty & Sensitivity",
        "tags": ["monte-carlo", "sensitivity", "decision-tree", "uncertainty"],
        "purpose": (
            "Uncertainty analysis: Monte Carlo valuation, Monte Carlo sensitivity ranking, decision-tree "
            "expected values, and one-at-a-time sensitivity analysis."
        ),
        "use": (
            "Use to quantify and stress the uncertainty around a point valuation; monte_carlo simulates all "
            "listed inputs, monte_carlo_sensitivity ranks the drivers."
        ),
        "alt": (
            "For a single deterministic point value use the relevant valuation tool; sensitivity_analysis "
            "varies one parameter of a core function only."
        ),
        "methods": [
            _method(
                "monte_carlo",
                "Simulate all listed inputs, sum-based valuation.",
                "intangible_valuation.core.statistics",
                "monte_carlo_valuation",
                {"input_distributions": "input_distributions"},
                {"iterations": "iterations", "seed": "seed"},
                adapter="mc_valuation",
            ),
            _method(
                "monte_carlo_sensitivity",
                "Rank parameters by their impact on the valuation.",
                "intangible_valuation.advanced.monte_carlo",
                "monte_carlo_sensitivity",
                {"base_params": "base_params", "distributions": "distributions"},
                {"iterations": "iterations", "seed": "seed"},
                adapter="mc_sensitivity",
            ),
            _method(
                "decision_tree",
                "Backward induction over a decision tree.",
                "intangible_valuation.core.statistics",
                "decision_tree_valuation",
                {"tree": "tree"},
            ),
            _method(
                "sensitivity_analysis",
                "One-at-a-time sensitivity of a core function.",
                "intangible_valuation.utils.formulas",
                "sensitivity_analysis",
                {
                    "function_name": "function_name",
                    "parameter_name": "parameter_name",
                    "parameter_range": "parameter_range",
                    "fixed_parameters": "fixed_parameters",
                },
            ),
        ],
        "constraints": "monte_carlo_sensitivity requires iterations between 1000 and 100000.",
    },
    {
        "name": "valuation_compliance",
        "title": "Transfer Pricing & Litigation",
        "tags": ["transfer-pricing", "litigation", "cup", "damages"],
        "purpose": (
            "Transfer pricing and litigation: the Comparable Uncontrolled Price arm's-length range and patent "
            "infringement damages with pre-judgment interest."
        ),
        "use": (
            "Use for OECD transfer-pricing pricing of intercompany intangibles and for patent infringement "
            "damages awards."
        ),
        "alt": (
            "For royalty-rate benchmarking to set a rate use valuation_royalty_analysis; for the substantive "
            "asset valuation use valuation_ip or valuation_income_methods."
        ),
        "constraints": "uncontrolled_prices must contain at least one comparable price for the arm's-length range.",
        "methods": [
            _method(
                "cup_transfer_price",
                "Arm's-length range from comparable uncontrolled prices.",
                "intangible_valuation.advanced.transfer_pricing",
                "cup_transfer_price",
                {"controlled_price": "controlled_price", "uncontrolled_prices": "uncontrolled_prices"},
            ),
            _method(
                "patent_infringement_damages",
                "Lost profits or reasonable royalty plus prejudgment interest.",
                "intangible_valuation.advanced.litigation",
                "patent_infringement_damages",
                {
                    "lost_profits_or_royalty": "lost_profits_or_royalty",
                    "infringement_period": "infringement_period",
                    "discount_rate": "discount_rate",
                    "prejudgment_interest_rate": "prejudgment_interest_rate",
                },
            ),
        ],
    },
]


# --------------------------------------------------------------------------
# Derivation helpers
# --------------------------------------------------------------------------


def _tool_param_names(tool: dict[str, Any]) -> list[str]:
    """Return every MCP parameter name used by any method of the tool, in stable order."""
    names: list[str] = []
    for method in tool.get("methods", []):
        for mapping in ("args", "opt"):
            for mcp_name in method.get(mapping, {}).values():
                if mcp_name not in names:
                    names.append(mcp_name)
    return names


def _method_parameter_map(tool: dict[str, Any]) -> str:
    """Build the per-method parameter map sentence fragment (declaration order)."""
    parts: list[str] = []
    for method in tool["methods"]:
        required = list(method["args"].values())
        optional = list(method["opt"].values())
        if required:
            fragment = f"{method['key']} needs " + " + ".join(required)
        else:
            fragment = f"{method['key']} takes only method"
        if optional:
            fragment += " (optional: " + ", ".join(optional) + ")"
        parts.append(fragment)
    return "; ".join(parts) + "."


def describe(tool: dict[str, Any]) -> str:
    """Assemble the TDQS-optimized description for a tool."""
    lines = [tool["purpose"], "Method selects the formula."]
    if tool.get("use"):
        lines.append(tool["use"])
    if tool.get("alt"):
        lines.append(tool["alt"])
    lines.append("Per method: " + _method_parameter_map(tool))
    if tool.get("constraints"):
        lines.append(tool["constraints"])
    lines.append(
        "Only method is required; all other parameters are method-dependent — supply those the selected method "
        "names and omit the rest (defaults apply where defined). Rates and premiums are decimals (0.10 = 10%)."
    )
    lines.append(
        "Pure arithmetic: no I/O and no external calls, rounded to 2 decimals; parameters belonging to other "
        "methods are accepted and ignored."
    )
    lines.append("An unknown method, or a missing method-required parameter, returns an error instead of a value.")
    return " ".join(lines)


def _type_schema(spec: dict[str, Any]) -> dict[str, Any]:
    t = spec["type"]
    if t == "array:number":
        return {"type": "array", "items": {"type": "number"}}
    if t == "array:object":
        return {"type": "array", "items": {"type": "object"}}
    if t == "object":
        return {"type": "object"}
    return {"type": t}


def _param_schema(name: str) -> dict[str, Any]:
    spec = PARAMS[name]
    schema = _type_schema(spec)
    schema["description"] = spec["description"]
    if "enum" in spec:
        schema["enum"] = spec["enum"]
    if "default" in spec:
        schema["default"] = spec["default"]
    return schema


def _all_param_names() -> set[str]:
    found: set[str] = set()
    for tool in TOOLS:
        found.update(_tool_param_names(tool))
    return found


def input_schema(tool: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON Schema advertised for a tool."""
    enum = [m["key"] for m in tool["methods"]]
    props: dict[str, Any] = {
        "method": {
            "type": "string",
            "enum": enum,
            "description": "Formula to apply. Options: "
            + "; ".join(f"{m['key']} = {m['summary']}" for m in tool["methods"]),
        }
    }
    for name in _tool_param_names(tool):
        props[name] = _param_schema(name)
    return {"type": "object", "properties": props, "required": ["method"]}


def tool_definition(tool: dict[str, Any]) -> dict[str, Any]:
    """Full tools/list entry (name, title, description, schemas, annotations, tags)."""
    return {
        "name": tool["name"],
        "title": tool["title"],
        "description": describe(tool),
        "inputSchema": input_schema(tool),
        "outputSchema": OUTPUT_SCHEMA,
        "annotations": COMMON_ANNOTATIONS,
        "tags": tool["tags"],
    }


def list_tools() -> list[dict[str, Any]]:
    """Return every tool definition, in stable order."""
    return [tool_definition(t) for t in TOOLS]


def tool_count() -> int:
    return len(TOOLS)


# --------------------------------------------------------------------------
# Dispatch
# --------------------------------------------------------------------------


def _simple_sum_valuation(**params: float) -> float:
    """Sum-based valuation used by the Monte Carlo MCP adapters."""
    return float(sum(v for v in params.values() if isinstance(v, (int, float))))


class _SumResult:
    """Minimal ValuationResult-shaped object for the sensitivity adapter."""

    def __init__(self, value: float) -> None:
        self.value = value
        self.method = "Sum"
        self.formula_reference = "sum"
        self.steps: list[str] = []
        self.assumptions: list[str] = []


def _sum_valuation(params: dict[str, float]) -> _SumResult:
    return _SumResult(_simple_sum_valuation(**params))


def _resolve(module_name: str, function_name: str) -> Any:
    import importlib

    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def _json_safe(obj: Any) -> Any:
    """Recursively coerce a result to JSON-serializable primitives.

    Monte Carlo results carry NumPy scalars; convert them via ``.item()`` and
    fall back to ``str`` for anything else exotic so the payload always
    serializes.
    """
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if obj is None or isinstance(obj, (str, bool, int, float)):
        return obj
    item = getattr(obj, "item", None)
    if callable(item):
        try:
            return item()
        except Exception:  # noqa: BLE001 — fall through to str()
            pass
    return str(obj)


def _unwrap(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return _json_safe(result)
    if hasattr(result, "model_dump"):
        try:
            return _json_safe(result.model_dump(mode="json"))
        except Exception:  # noqa: BLE001 — fall back to the python-mode dump
            return _json_safe(result.model_dump())
    return _json_safe(
        {
            "value": getattr(result, "value", result),
            "method": getattr(result, "method", ""),
            "formula_reference": getattr(result, "formula_reference", ""),
            "steps": getattr(result, "steps", []),
            "assumptions": getattr(result, "assumptions", []),
        }
    )


def _find_method(tool: dict[str, Any], method_key: str) -> dict[str, Any]:
    for method in tool.get("methods", []):
        if method["key"] == method_key:
            return method
    raise ValueError(f"Unknown method '{method_key}' for tool '{tool['name']}'")


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool by name. Raises ValueError for bad input."""
    tool = next((t for t in TOOLS if t["name"] == name), None)
    if tool is None:
        raise ValueError(f"Tool not found: {name}")

    method = _find_method(tool, arguments.get("method", ""))

    kwargs: dict[str, Any] = {}
    for fn_param, mcp_name in method.get("args", {}).items():
        if arguments.get(mcp_name) is None:
            raise ValueError(f"method '{method['key']}' requires parameter '{mcp_name}'")
        kwargs[fn_param] = arguments[mcp_name]
    for fn_param, mcp_name in method.get("opt", {}).items():
        value = arguments.get(mcp_name)
        if value is not None:
            kwargs[fn_param] = value
    kwargs.update(method.get("inject", {}))

    fn = _resolve(method["module"], method["function"])

    if method.get("adapter") == "mc_valuation":
        kwargs["valuation_fn"] = _simple_sum_valuation
    elif method.get("adapter") == "mc_sensitivity":
        kwargs["valuation_fn"] = _sum_valuation

    result = fn(**kwargs)
    return _unwrap(result)
