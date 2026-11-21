---
name: Discount Rate Construction
description: Build appropriate discount rates using CAPM, WACC, build-up method, and DLOM.
category: valuation
tools: [valuation_discount_rate]
---

# Discount Rate Construction Skill

## When to Use

Use this skill when a user asks to:
- Build a discount rate for valuation (WACC, cost of equity, cost of debt)
- Calculate discount rate using build-up method, CAPM, or WACC
- Apply risk premiums (size, industry, company-specific, country, currency)
- Adjust for lack of marketability (DLOM) or control premium
- Calculate tax amortization benefit (TAB)
- Select the appropriate discount rate method for a given asset type

## Discount Rate Methods

| Method | Formula | Best For | Method key |
|--------|---------|----------|----------|
| Build-Up | r = Rf + ERP + Size + Industry + Specific | Private companies, no beta | `build_up` |
| CAPM | r = Rf + β × (Rm − Rf) | Public companies, available beta | `capm` |
| WACC | (E/V)×Re + (D/V)×Rd×(1−Tc) | Enterprise-level, debt financing | `wacc` |

## Step-by-Step Workflow

### Step 1: Identify the Valuation Context
Ask the user:
- What are you valuing? (company, patent, brand, customer list, etc.)
- Is the entity public or private?
- What is the jurisdiction? (US, international, emerging market)
- What is the purpose? (financial reporting, M&A, litigation, tax)

### Step 2: Select the Method

```
Is the entity publicly traded with available beta?
├── YES → Use CAPM or WACC
│   └── Does the entity use debt financing?
│       ├── YES → Use WACC
│       └── NO  → Use CAPM
└── NO  → Use Build-Up Method
```

### Step 3: Gather Inputs for Selected Method

**Build-Up Method:**
- `risk_free_rate` — 10-year or 20-year government bond yield (e.g., 0.04 for 4%)
- `equity_risk_premium` — Duff & Phelps/Ibbotson ERP (typically 5-7%)
- `size_premium` — CRSP Decile size premium (0-6% depending on market cap)
- `industry_risk_premium` — Industry-specific risk (0-5%)
- `specific_risk_premium` — Company-specific risk factors (0-5%)

```python
# Calculate
valuation_discount_rate(method="build_up",
    risk_free_rate=0.04, equity_risk_premium=0.06,
    size_premium=0.02, industry_risk_premium=0.01, specific_risk_premium=0.03,
)
# Result: 16.00%
```

**CAPM:**
- `risk_free_rate` — Government bond yield
- `beta` — Unlevered industry beta, relevered for company's capital structure
- `market_return` — Expected market return (typically Rf + ERP)

```python
valuation_discount_rate(method="capm", risk_free_rate=0.04, beta=1.2, market_return=0.10)
# Result: 11.20%
```

**WACC:**
- `equity_value` — Market cap of equity
- `debt_value` — Market value of debt
- `cost_of_equity` — From CAPM or Build-Up
- `cost_of_debt` — Yield on company's debt or borrowing rate
- `tax_rate` — Marginal tax rate

```python
valuation_discount_rate(method="wacc", equity_value=700, debt_value=300, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)
# Result: 9.75%
```

### Step 4: Apply Adjustments

**Tax Amortization Benefit (TAB):**
For intangible asset valuations, TAB adjusts the discount rate to account for tax savings from asset amortization.

```python
valuation_discount_rate(method="tax_amortization_benefit", discount_rate=0.16, useful_life=10, tax_rate=0.25, asset_value=1_000_000)
```

**Discount for Lack of Marketability (DLOM):**
Finnerty average-strike put option model for restricted stock.

```python
valuation_discount_rate(method="dlom_finnerty", restricted_period=1.0, volatility=0.35, risk_free_rate=0.04)
```

**Control Premium:**
Adjustment when valuing controlling vs minority interests.

```python
valuation_discount_rate(method="control_premium", minority_price=85, control_price=100)
# Result: 17.65%
```

**Currency & Country Risk:**
For cross-border valuations.

```python
valuation_discount_rate(method="currency_adjusted", base_rate=0.12, currency_risk_premium=0.02, country_risk_premium=0.03)
# Result: 17.00%
```

### Step 5: Validate the Rate

**Sanity Checks:**
- Discount rate should exceed risk-free rate (no negative risk premiums)
- Discount rate should exceed long-term GDP growth rate
- Discount rate for intangibles > WACC (intangibles are riskier than the enterprise)
- TAB-adjusted rate < unadjusted rate (tax benefit reduces effective cost)

**Typical Ranges by Asset Type:**

| Asset Type | Discount Rate Range | Notes |
|------------|-------------------|-------|
| Core deposit intangible | 8-12% | Lower risk, stable cash flows |
| Customer relationships | 12-18% | Attrition risk increases rate |
| Trademarks/Brands | 10-16% | Depends on brand strength |
| Patents | 14-25% | Higher technology/obsolescence risk |
| Software | 15-25% | Rapid obsolescence |
| In-process R&D | 18-30% | Highest risk, uncertain outcomes |
| Goodwill (WACC) | 8-15% | Enterprise-level rate |

## MCP Methods Reference

These are **methods**, called through the tool this skill's front matter names
(`valuation_discount_rate`), as `{"method": "<name>", ...params}`.

| Method | Category | Key Parameters |
|------|----------|---------------|
| `build_up` | Core | risk_free_rate, equity_risk_premium, size_premium, industry_risk_premium, specific_risk_premium |
| `capm` | Core | risk_free_rate, beta, market_return |
| `wacc` | Core | equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate |
| `tax_amortization_benefit` | Core | discount_rate, useful_life, tax_rate, asset_value |
| `dlom_finnerty` | Core | restricted_period, volatility, risk_free_rate |
| `control_premium` | Core | minority_price, control_price |
| `currency_adjusted` | Core | base_rate, currency_risk_premium, country_risk_premium |

## References
- Chapter 2: Core Mathematics — Discount Rates
- Duff & Phelps Valuation Handbook (size premiums)
- Ibbotson SBBI Yearbook (equity risk premiums)
- IRS Rev. Rul. 59-60 (valuation standards)
- Mandelbaum factors (DLOM considerations)
