---
name: Impairment Testing
description: Goodwill and intangible asset impairment testing compliant with ASC 350/IAS 36.
category: compliance
tools: [valuation_impairment, valuation_market_approach, valuation_income_methods, valuation_time_value, valuation_cost_approach]
---

# Impairment Testing Skill

## When to Use

Use this skill when a user asks to:
- Test goodwill for impairment
- Test intangible assets for impairment under ASC 350 or IAS 36
- Perform annual impairment testing
- Assess whether carrying value exceeds fair value
- Determine impairment loss amount
- Compare ASC 350 vs IAS 36 methodologies

## ASC 350 vs IAS 36

| Feature | ASC 350 (US GAAP) | IAS 36 (IFRS) |
|---|---|---|
| Goodwill Test | One-step: Compare reporting unit FV to carrying value | Compare CGU carrying value to recoverable amount |
| Recoverable Amount | Not applicable | Higher of (FVLCTS, value in use) |
| Impairment Reversal | Not permitted | Permitted (except goodwill) |
| Reporting Unit | Operating segment or one level below | Cash-Generating Unit (CGU) |
| Frequency | Annual + triggering events | Annual + triggering events |

## Step-by-Step Workflow

### Step 1: Identify What to Test
- **Goodwill** — reporting unit (ASC 350) or CGU (IAS 36)
- **Indefinite-lived intangibles** — trademarks, brands, FCC licenses
- **Finite-lived intangibles** — only if triggering events exist

**Triggering Events:** market cap decline, key customer loss, regulatory changes, technology obsolescence, competition increase, performance deterioration

### Step 2: Gather Carrying Value
Obtain net book value from accounting records.

### Step 3: Estimate Fair Value
Use appropriate valuation approach:
- Market approach — `comparable_transactions`
- Income approach — `relief_from_royalty`, `mpeem`, `royalty_capitalization`
- Cost approach — `reproduction_cost`, `replacement_cost`

### Step 4: Run the Test

**Goodwill (ASC 350):**
```python
valuation_impairment(method="goodwill_impairment",
    carrying_value=15_000_000,
    fair_value=13_000_000,
    reporting_unit="Software Division",
    standard="ASC350",
)
# Impairment: $2,000,000
```

**Intangible Asset (ASC 350):**
```python
valuation_impairment(method="intangible_impairment",
    carrying_value=5_000_000,
    fair_value=4_200_000,
    standard="ASC350",
)
# Impairment: $800,000
```

**Intangible Asset (IAS 36):**
```python
valuation_impairment(method="intangible_impairment",
    carrying_value=5_000_000,
    recoverable_amount=4_500_000,  # Higher of FVLCTS and VIU
    standard="IAS36",
)
# Impairment: $500,000
```

### Step 5: Document & Report
- Record impairment loss in income statement
- Disclose key assumptions (discount rate, growth rate, cash flow projections)
- Update asset carrying value

## MCP Methods Reference

These are **methods**, called through the tools this skill's front matter names
(`valuation_impairment`, `valuation_market_approach`, `valuation_income_methods`, `valuation_time_value`,
`valuation_cost_approach`), as `{"method": "<name>", ...params}`.

| Method | Purpose |
|------|---------|
| `goodwill_impairment` | Test goodwill for impairment |
| `intangible_impairment` | Test intangible assets for impairment |
| `comparable_transactions` | Estimate fair value via market approach |
| `relief_from_royalty` | Estimate fair value for IP assets |
| `mpeem` | Estimate fair value for primary intangibles |
| `present_value` | Discount future cash flows |

## References
- Chapter 11: Impairment Testing
- ASC 350-20 — Goodwill
- ASC 350-30 — General Intangibles
- IAS 36 — Impairment of Assets
