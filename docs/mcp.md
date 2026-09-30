# MCP Server

The Intangible Valuation MCP (Model Context Protocol) server exposes the full
valuation library to AI agents as **14 tools**, each folding a family of
formulas behind a `method` argument.

## Overview

- **14 tools** covering 124+ formulas across time value, discount rates, cost /
  market / income approaches, asset types, goodwill & PPA, impairment, royalty
  analysis, uncertainty, and transfer-pricing / litigation.
- **Single source of truth:** `mcp_server/tool_surface.py` defines every tool
  once; the stdio server (`mcp_server/server.py`) is generated from it and the
  hosted endpoint (`api/mcp.py`) consumes it at runtime, so the two surfaces
  cannot drift.
- **Structured results:** every tool returns `value`, `method`,
  `formula_reference`, `steps`, and `assumptions`.
- **Read-only & deterministic:** no files, network, auth, or rate limits.

## Setup

### Installation

```bash
pip install intangible-valuation[mcp]
```

### Configuration (stdio)

Add the MCP server to your AI agent configuration:

```json
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "python",
      "args": ["mcp_server/server.py"]
    }
  }
}
```

The installed console script is equivalent:

```bash
intangible-valuation-mcp
```

### Configuration (hosted)

No install, no API key — point the client at the Streamable HTTP endpoint:

```
https://intangible-valuation.simonmak.com/api/mcp
```

## Available Tools

Each tool takes a required `method` and that method's parameters. Only `method`
is required; supply just the parameters named for the selected method.

### `valuation_time_value`

Time value of money: single sums, annuities, perpetuities, and terminal value.

| Method | Formula |
|--------|---------|
| `present_value` | PV = FV / (1 + r)^n |
| `future_value` | FV = PV * (1 + r)^n |
| `annuity_pv` | PV = PMT * [1 - (1 + r)^-n] / r |
| `perpetuity_pv` | PV = PMT / r |
| `growing_annuity_pv` | PV of a constant-growth annuity |
| `terminal_value_gordon_growth` | TV = FCF * (1 + g) / (r - g) |
| `terminal_value_exit_multiple` | TV = FCF * exit multiple |

### `valuation_discount_rate`

Build-up, CAPM, WACC, tax-amortization benefit, control premium, Finnerty DLOM,
and currency/country adjustment.

### `valuation_cost_approach`

Depreciated reproduction cost and depreciated replacement cost.

### `valuation_market_approach`

Comparable transaction multiples and royalty capitalization.

### `valuation_income_methods`

Relief from royalty, MPEEM, single-period excess earnings, incremental cash
flow, and contributory asset charges.

### `valuation_ip`

Patent, trademark, copyright, and trade-secret valuation.

### `valuation_technology`

Developed technology, software, data assets, and platforms.

### `valuation_customer`

Customer relationships, distribution networks, and non-compete agreements.

### `valuation_human_capital`

Assembled workforce and key-person value.

### `valuation_goodwill_ppa`

Goodwill as a residual, the full purchase price allocation waterfall, and
useful-life estimation.

### `valuation_impairment`

Goodwill and intangible impairment under ASC 350 or IAS 36.

### `valuation_royalty_analysis`

Royalty-rate benchmarking, adjustment, and the 25% rule.

### `valuation_simulation`

Monte Carlo valuation, Monte Carlo sensitivity, decision trees, and
one-at-a-time sensitivity analysis.

### `valuation_compliance`

Comparable Uncontrolled Price (transfer pricing) and patent infringement
damages.

## Example Usage

```jsonc
// tools/call
{
  "method": "relief_from_royalty",
  "revenue_projections": [1000000, 1100000, 1200000, 1300000, 1400000],
  "royalty_rate": 0.05,
  "discount_rate": 0.12,
  "tax_rate": 0.25,
  "useful_life": 5
}
```

Result:

```json
{
  "value": 194163.77,
  "method": "Relief from Royalty",
  "formula_reference": "...",
  "steps": ["..."],
  "assumptions": ["..."]
}
```

## Architecture

Every tool is a pure calculator built with FastMCP and shared with the hosted
endpoint:

- Parameter validation via Pydantic
- `outputSchema` + MCP `annotations` on every tool
- Structured JSON responses with calculation steps
- Error handling that returns an error instead of a value

## Development

```bash
# Run the server in development mode
python -m mcp_server.server

# Regenerate the stdio server from the canonical surface
python scripts/generate_mcp.py

# Lint the tool surface (Glama TDQS)
npx --yes mcp-tdqs@0.2.0 lint --command "python mcp_server/server.py" --fail-on error
```
