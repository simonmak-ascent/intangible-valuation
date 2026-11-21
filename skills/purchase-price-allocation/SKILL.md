---
name: Purchase Price Allocation
description: Complete PPA workflow following ASC 805/IFRS 3 with full waterfall calculation.
category: workflow
tools: [valuation_goodwill_ppa, valuation_income_methods, valuation_technology, valuation_customer, valuation_ip, valuation_human_capital, valuation_discount_rate, valuation_royalty_analysis]
---

# Purchase Price Allocation (PPA) Workflow Skill

## When to Use

Use this skill when a user asks to:
- Perform a Purchase Price Allocation for an acquisition
- Allocate purchase price to tangible and intangible assets
- Calculate goodwill from an M&A transaction
- Prepare PPA for ASC 805 / IFRS 3 compliance
- Value individual intangible assets identified in an acquisition

## Full PPA Process

### Step 1: Gather Deal Information
Collect:
- **Purchase price** — total acquisition consideration (cash, stock, contingent consideration)
- **Acquisition date** — for fair value measurement
- **Target company** — name, industry, business description
- **Accounting standard** — ASC 805 (US GAAP) or IFRS 3

MCP Tool: None (information gathering)

### Step 2: Identify and Value Tangible Assets
List all tangible assets at fair value:
- Cash and cash equivalents
- Accounts receivable (net of allowance)
- Inventory (raw materials, WIP, finished goods)
- Property, plant, and equipment
- Other tangible assets

Also identify liabilities assumed:
- Accounts payable
- Debt
- Deferred tax liabilities
- Other liabilities

MCP Tool: None (use external appraisals or book values adjusted to fair value)

### Step 3: Identify Intangible Assets
Identify all separable intangible assets using the contractual-legal and separability criteria:

| Asset Category | Common Types | Typical Valuation Method |
|---|---|---|
| Marketing-related | Trademarks, brand names, trade dress | Relief from Royalty |
| Customer-related | Customer lists, relationships, contracts | MPEEM, Multi-period attrition |
| Artistic-related | Copyrights, literary works, music | Relief from Royalty |
| Contract-based | Licenses, franchise agreements, non-competes | Incremental Cash Flow, RFR |
| Technology-based | Patents, software, trade secrets, developed tech | RFR, Cost-Income Hybrid |

For each identified intangible:
1. Determine useful life (finite vs indefinite)
2. Select appropriate valuation method
3. Gather inputs (revenue, royalty rates, discount rates, CACs)
4. Calculate fair value

MCP methods, as `{"method": "<key>", ...params}` on the tool named beside each:
- `valuation_ip` with `trademark` — brands/trademarks
- `valuation_ip` with `patent` — patents
- `valuation_ip` with `copyright` — copyrights
- `valuation_ip` with `trade_secret` — trade secrets
- `valuation_technology` with `developed_technology` — developed technology
- `valuation_technology` with `software` — software
- `valuation_customer` with `customer_relationships` — customer relationships
- `valuation_customer` with `non_compete` — non-compete agreements
- `valuation_customer` with `distribution_network` — distribution networks
- `valuation_human_capital` with `assembled_workforce` — assembled workforce (note: not separately recognized under ASC 805, subsumed into goodwill)
- `valuation_income_methods` with `relief_from_royalty` — any asset with comparable royalty rates
- `valuation_income_methods` with `mpeem` — primary revenue-generating intangibles
- `valuation_royalty_analysis` with `benchmark` — market royalty rates
- `valuation_goodwill_ppa` with `useful_life` — amortisation periods
- `valuation_discount_rate` with `build_up` or `capm` — discount rates

### Step 4: Calculate Goodwill
Goodwill = Purchase Price - Fair Value of Net Identifiable Assets

Where:
Net Identifiable Assets = Tangible Assets (FV) + Identified Intangibles (FV) - Liabilities (FV)

MCP Tool: `valuation_goodwill_ppa` with `{"method": "goodwill", "purchase_price": ..., "fair_value_net_identifiable_assets": ...}`

Or use the full waterfall:
```
valuation_goodwill_ppa(method="purchase_price_allocation",
    purchase_price=...,
    tangible_assets_fv=...,
    identified_intangibles=[
        {"name": "Trademark", "value": ..., "method": "relief_from_royalty"},
        {"name": "Customer Relationships", "value": ..., "method": "mpeem"},
        {"name": "Developed Technology", "value": ..., "method": "relief_from_royalty"},
    ],
    liabilities_fv=...
)
```

### Step 5: Prepare PPA Report
Create a waterfall table:

| Item | Fair Value | % of Purchase Price |
|---|---|---|
| Purchase Price | $X | 100.0% |
| Tangible Assets | $A | A/X% |
| Identified Intangibles | $B | B/X% |
| Liabilities Assumed | ($C) | C/X% |
| Net Identifiable Assets | $A+B-C | (A+B-C)/X% |
| **Goodwill** | **$G** | **G/X%** |

For each intangible, document:
- Asset description
- Valuation method and rationale
- Key inputs and assumptions
- Useful life and amortization method

## IFRS 3 / ASC 805 Compliance Checklist

- [ ] Purchase price determination (cash, stock, contingent consideration at fair value)
- [ ] Acquisition date established
- [ ] All tangible assets identified and valued at fair value
- [ ] All liabilities identified and valued at fair value
- [ ] Intangible assets identified using contractual-legal criterion
- [ ] Intangible assets identified using separability criterion
- [ ] Each intangible valued using appropriate method
- [ ] Useful lives determined for each finite-lived intangible
- [ ] Indefinite-lived intangibles identified (not amortized, tested for impairment)
- [ ] Goodwill calculated as residual
- [ ] Bargain purchase considered (if negative goodwill, reassess before recognizing gain)
- [ ] Contingent consideration measured at fair value
- [ ] Deferred taxes calculated on fair value adjustments
- [ ] Measurement period considerations (up to 12 months from acquisition date)

## Example PPA Scenario

**Deal:** TechCorp acquires SaaS Startup for $100M

**Step 1: Deal Info**
- Purchase price: $100,000,000
- Standard: ASC 805

**Step 2: Tangible Assets**
- Cash: $5M
- Accounts Receivable: $3M
- Equipment: $2M
- Total Tangibles: $10M
- Liabilities: $0

**Step 3: Identify and Value Intangibles**

1. **Developed Technology** (RFR method)
   - Revenue projections: $8M, $9M, $10M, $10.5M, $11M (5 years)
   - Royalty rate: 5% (from `valuation_royalty_analysis` with `benchmark` for technology/software)
   - Discount rate: 15% (from `valuation_discount_rate` with `build_up`)
   - Tax rate: 25%
   - `valuation_income_methods` with `relief_from_royalty` → $25M

2. **Customer Relationships** (MPEEM)
   - 500 customers, $20K avg revenue, 85% retention, 30% margin
   - CACs: working capital $2M at 8%, equipment $1M at 10%
   - Discount rate: 18%
   - `valuation_income_methods` with `mpeem` → $20M

3. **Trademark** (RFR method)
   - Revenue: $15M, brand strength 0.7, discount rate 14%, useful life 10 years
   - `valuation_ip` with `trademark` → $10M

4. **Non-Compete** (4-year term)
   - Protected revenue: $5M, margin 25%, enforcement 90%, discount 15%
   - `valuation_customer` with `non_compete` → $5M

**Total Identified Intangibles: $60M**

**Step 4: Calculate Goodwill**
```
valuation_goodwill_ppa(method="goodwill",
    purchase_price=100000000,
    fair_value_net_identifiable_assets=70000000  # 10M tangibles + 60M intangibles - 0 liabilities
)
```
Goodwill = $30M

**Step 5: PPA Waterfall**
```
valuation_goodwill_ppa(method="purchase_price_allocation",
    purchase_price=100000000,
    tangible_assets_fv=10000000,
    identified_intangibles=[
        {"name": "Developed Technology", "value": 25000000, "method": "relief_from_royalty"},
        {"name": "Customer Relationships", "value": 20000000, "method": "mpeem"},
        {"name": "Trademark", "value": 10000000, "method": "relief_from_royalty"},
        {"name": "Non-Compete", "value": 5000000, "method": "income_approach"},
    ],
    liabilities_fv=0
)
```

| Item | Fair Value | % |
|---|---|---|
| Purchase Price | $100M | 100.0% |
| Tangible Assets | $10M | 10.0% |
| Developed Technology | $25M | 25.0% |
| Customer Relationships | $20M | 20.0% |
| Trademark | $10M | 10.0% |
| Non-Compete | $5M | 5.0% |
| Goodwill | $30M | 30.0% |
