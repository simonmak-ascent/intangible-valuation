import { Breadcrumb } from "@/components/layout/Breadcrumb";

export default function MCPPage() {
  return (
    <div className="container-narrow py-12">
      <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "MCP Gateway" }]} />

      <h1 className="text-display-sm text-primary-500 mt-6 mb-4">MCP Gateway</h1>
      <p className="text-lg text-neutral-500 mb-8">
        Connect any AI agent to 49 valuation tools via the Model Context Protocol.
        One <code>pip install</code> and your agent can perform any valuation calculation.
      </p>

      <div className="card-elevated p-6 mb-8">
        <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Quick Start
        </h2>
        <div className="bg-neutral-950 text-green-400 p-4 rounded-xl font-mono text-sm overflow-x-auto">
          <pre>{`# Install
pip install intangible-valuation[mcp]

# Add to your MCP config (mcp.json)
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/intangible-valuation"
    }
  }
}

# Or connect to the cloud endpoint
{
  "mcpServers": {
    "intangible-valuation-cloud": {
      "url": "https://intangible-valuation.simonmak.com/api/mcp"
    }
  }
}`}</pre>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          Available Tools
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            "Core: present_value, future_value, annuity_pv, perpetuity_pv, terminal_value",
            "Discount Rates: capm, wacc, build_up_discount_rate",
            "Income Methods: relief_from_royalty, mpeem, incremental_cashflow",
            "Cost Approach: reproduction_cost, replacement_cost, obsolescence",
            "Market Approach: comparable_transactions, royalty_capitalization",
            "Asset Types: patent, brand, technology, customer, human_capital",
            "Advanced: goodwill, ppa_waterfall, impairment_test, monte_carlo",
          ].map((group) => (
            <div key={group} className="p-3 rounded-lg bg-neutral-50 dark:bg-neutral-900 text-sm">
              <p className="font-medium text-neutral-700 dark:text-neutral-300">{group.split(":")[0]}</p>
              <p className="text-neutral-500 text-xs mt-1">{group.split(":")[1]}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
