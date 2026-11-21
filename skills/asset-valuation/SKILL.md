---
name: Asset Valuation
description: Comprehensive valuation workflow for any intangible asset type using all available methods.
category: valuation
tools: [valuation_time_value, valuation_discount_rate, valuation_cost_approach, valuation_market_approach, valuation_income_methods, valuation_ip, valuation_technology, valuation_customer, valuation_human_capital, valuation_royalty_analysis, valuation_simulation, valuation_goodwill_ppa]
---

# Asset Valuation Skill

## When to Use

Use this skill when a user asks to:
- Value any intangible asset (patent, trademark, brand, software, customer list, etc.)
- Calculate present value, discount rates, or terminal value
- Perform a valuation using any standard methodology (RFR, MPEEM, cost approach, market approach)
- Compare valuation results across multiple methods
- Benchmark royalty rates or estimate useful life

## Supported Asset Types

| Asset Type | Function | Common Methods |
|---|---|---|
| Patent | `patent_valuation` | Risk-adjusted income, Relief from royalty |
| Trademark/Brand | `trademark_valuation` | RFR, Excess earnings |
| Copyright | `copyright_valuation` | Relief from royalty |
| Trade Secret | `trade_secret_valuation` | Cost-income hybrid |
| Developed Technology | `developed_technology_valuation` | Cost-income with life-cycle risk |
| Software | `software_valuation` | Cost-income hybrid |
| Data Asset | `data_asset_valuation` | Quality-adjusted income |
| Platform | `platform_valuation` | Network effects income |
| Customer Relationship | `customer_relationship_valuation` | Multi-period with attrition |
| Distribution Network | `distribution_network_valuation` | Channel income approach |
| Non-Compete | `non_compete_valuation` | Income with enforcement risk |
| Assembled Workforce | `assembled_workforce_valuation` | Replacement cost |
| Key Person | `key_person_value` | Income + replacement cost |

## Supported Valuation Methods

### Core Math
- `present_value` — PV of single future cash flow: PV = FV / (1+r)^n
- `future_value` — FV of present amount: FV = PV * (1+r)^n
- `annuity_pv` — PV of equal periodic payments
- `perpetuity_pv` — PV of perpetual payments: PV = PMT / r
- `growing_annuity_pv` — PV of growing payments
- `terminal_value_gordon_growth` / `terminal_value_exit_multiple` — Terminal value via Gordon Growth or Exit Multiple
- `build_up` — Build-up method: r = Rf + ERP + premiums
- `capm` — CAPM: r = Rf + beta * (Rm - Rf)
- `wacc` — Weighted Average Cost of Capital
- `tax_amortization_benefit` — PV of tax savings from amortization
- `control_premium` — Control premium percentage
- `dlom_finnerty` — DLOM via Finnerty put option model
- `currency_adjusted` — Add currency/country risk premiums

### Approaches
- `reproduction_cost` — Cost to create exact replica, less obsolescence
- `replacement_cost` — Cost to create equivalent utility, less obsolescence
- `comparable_transactions` — Revenue multiples from comparable transactions
- `royalty_capitalization` — Capitalize perpetual royalty: V = (Rev * r) / d

### Income Methods
- `relief_from_royalty` — PV of avoided royalty payments (with TAB)
- `mpeem` — Multi-Period Excess Earnings Method (with CACs and TAB)
- `single_period_excess_earnings` — Capitalize single-period excess earnings
- `incremental_cashflow` — PV of cash flows with vs without asset
- `contributory_asset_charges` — Calculate CACs for supporting assets

### Advanced
- `benchmark` — Benchmark rates by IP type and industry
- `adjust` — Adjust base rate for deal factors
- `twenty_five_percent_rule` — 25% rule of thumb for royalties
- `monte_carlo` — Monte Carlo simulation for uncertainty
- `decision_tree` — Decision tree expected value analysis
- `sensitivity_analysis` — One-at-a-time parameter sensitivity
- `useful_life` — Estimate asset useful life

## Step-by-Step Workflow

### Step 1: Identify the Asset
Ask the user what type of intangible asset they want to value. Determine:
- Asset type (patent, trademark, software, customer relationship, etc.)
- Industry/sector context
- Purpose of valuation (financial reporting, litigation, M&A, licensing)

### Step 2: Select the Valuation Method
Match asset type to appropriate method:

| Situation | Recommended Method |
|---|---|
| Licensed IP with market royalties | Relief from Royalty |
| Primary revenue-generating intangible | MPEEM |
| Mature asset with stable cash flows | Royalty Capitalization |
| Newly developed asset | Cost Approach (Reproduction/Replacement) |
| Active market for similar assets | Market Approach (Comparables) |
| Asset with contingent outcomes | Decision Tree |
| High uncertainty in inputs | Monte Carlo |

### Step 3: Gather Inputs
Collect required parameters for the chosen method. Common inputs:
- **Revenue/cash flow projections** — annual amounts for each period
- **Discount rate** — from CAPM, build-up, or WACC
- **Royalty rate** — from benchmark or comparable licenses
- **Tax rate** — corporate tax rate (default 25%)
- **Useful life** — economic or legal life in years
- **Contributory asset charges** — for MPEEM

Use these methods, through the tools named in this file's front matter:
- `valuation_discount_rate` with `{"method": "build_up"}` or `{"method": "capm"}` — the discount rate
- `valuation_royalty_analysis` with `{"method": "benchmark"}` — market royalty rates
- `valuation_goodwill_ppa` with `{"method": "useful_life"}` — the projection period
- `valuation_income_methods` with `{"method": "contributory_asset_charges"}` — CACs

### Step 4: Calculate
Call the appropriate MCP tool with gathered inputs. The tool returns:
- `value` — the calculated valuation
- `method` — methodology used
- `formula_reference` — formula and book reference
- `steps` — step-by-step calculation breakdown
- `assumptions` — key assumptions made

### Step 5: Present Results
Format the result clearly:
1. State the asset type and valuation method used
2. Present the calculated value with currency formatting
3. Show key calculation steps
4. List critical assumptions
5. If applicable, cross-check with a second method

## Example Conversations

### Example 1: Patent Valuation

**User:** "Value a pharmaceutical patent with 12 years remaining. Projected cash flows are $2M, $2.5M, $3M, $3.2M, $3.5M, $3.5M, $3.2M, $2.8M, $2.5M, $2M, $1.5M, $1M. Probability of success is 70%. Use 15% discount rate."

**Agent:**
1. Identify: Patent valuation, pharmaceutical industry
2. Method: Risk-adjusted income approach — `valuation_ip` with `method="patent"`
3. Call tool:
```
valuation_ip(method="patent",
    remaining_life=12,
    cash_flow_projections=[2000000, 2500000, 3000000, 3200000, 3500000, 3500000, 3200000, 2800000, 2500000, 2000000, 1500000, 1000000],
    probability_of_success=0.70,
    discount_rate=0.15
)
```
4. Present: "The patent is valued at $X using the risk-adjusted income approach..."

### Example 2: Brand Valuation

**User:** "What's our brand worth? Annual revenue is $50M, profit margin 20%, brand strength index 0.75, discount rate 12%, useful life 15 years."

**Agent:**
1. Identify: Trademark/brand valuation
2. Method: Relief from Royalty — `valuation_ip` with `method="trademark"`; the library's own `method`
   argument is surfaced as `brand_method`, because `method` selects the tool's method key
3. Call tool:
```
valuation_ip(method="trademark",
    revenue=50000000,
    profit_margin=0.20,
    brand_strength_index=0.75,
    discount_rate=0.12,
    useful_life=15,
    brand_method="relief_from_royalty"
)
```

### Example 3: Discount Rate Construction

**User:** "What discount rate should I use for a small tech company? Risk-free rate 4%, equity risk premium 6%, size premium 4%, industry risk 2%, specific risk 3%."

**Agent:**
```
valuation_discount_rate(method="build_up",
    risk_free_rate=0.04,
    equity_risk_premium=0.06,
    size_premium=0.04,
    industry_risk_premium=0.02,
    specific_risk_premium=0.03
)
```
Result: 19% discount rate.
