import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { FormulaDisplay } from "@/components/valuation/FormulaDisplay";

const METHODS: Record<string, {
  slug: string; name: string; category: string; description: string;
  formulaTex?: string; textbookReference: string;
  parameters: { name: string; type: string; required: boolean; description: string }[];
  pythonCode: string; mcpTool: string;
}> = {
  "present-value": {
    slug: "present-value", name: "Present Value", category: "core",
    description: "The present value (PV) function discounts a future cash flow to its value today. This is the most fundamental concept in finance — a dollar today is worth more than a dollar tomorrow.",
    formulaTex: "PV = FV / (1 + r)^n",
    textbookReference: "Chapter 2, Section 2.1 — Time Value of Money",
    parameters: [
      { name: "future_value", type: "number", required: true, description: "The expected future cash flow amount" },
      { name: "discount_rate", type: "number", required: true, description: "Annual discount rate (0-1). For startups, typically 0.20-0.35. For mature companies, 0.06-0.12." },
      { name: "periods", type: "integer", required: true, description: "Number of periods until the cash flow occurs" },
    ],
    pythonCode: `from intangible_valuation.core.time_value import present_value

result = present_value(
    future_value=100000,
    discount_rate=0.10,
    periods=5
)
print(f"Present Value: \${result.value:,.2f}")`,
    mcpTool: "present_value",
  },
  "capm": {
    slug: "capm", name: "CAPM", category: "core",
    description: "The Capital Asset Pricing Model (CAPM) determines the required rate of return for an equity investment based on its systematic risk (beta). This is the most widely used model for estimating cost of equity in valuation.",
    formulaTex: "r = Rf + Beta * (Rm - Rf)",
    textbookReference: "Chapter 2, Section 2.3 — Discount Rate Construction",
    parameters: [
      { name: "risk_free_rate", type: "number", required: true, description: "Risk-free rate (typically 10-year treasury yield). Current US: ~0.04" },
      { name: "beta", type: "number", required: true, description: "Beta coefficient measuring systematic risk. >1 = more volatile than market, <1 = less volatile." },
      { name: "market_return", type: "number", required: true, description: "Expected market return (S&P 500 long-term avg: ~0.10)" },
    ],
    pythonCode: `from intangible_valuation.core.discount_rates import capm

result = capm(
    risk_free_rate=0.04,
    beta=1.2,
    market_return=0.10
)
print(f"Cost of Equity: {result.value:.4f} ({result.value*100:.1f}%)")`,
    mcpTool: "capm",
  },
  "wacc": {
    slug: "wacc", name: "WACC", category: "core",
    description: "Weighted Average Cost of Capital blends the cost of equity and after-tax cost of debt, weighted by their proportions in the capital structure. WACC is the primary discount rate for DCF valuation.",
    formulaTex: "WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)",
    textbookReference: "Chapter 2, Section 2.3 — Discount Rate Construction",
    parameters: [
      { name: "equity_value", type: "number", required: true, description: "Market value of equity" },
      { name: "debt_value", type: "number", required: true, description: "Market value of interest-bearing debt" },
      { name: "cost_of_equity", type: "number", required: true, description: "Cost of equity from CAPM or build-up" },
      { name: "cost_of_debt", type: "number", required: true, description: "Pre-tax cost of debt (yield on company's debt)" },
      { name: "tax_rate", type: "number", required: true, description: "Marginal corporate tax rate" },
    ],
    pythonCode: `from intangible_valuation.core.discount_rates import wacc

result = wacc(
    equity_value=1_000_000,
    debt_value=200_000,
    cost_of_equity=0.12,
    cost_of_debt=0.05,
    tax_rate=0.21
)
print(f"WACC: {result.value:.4f} ({result.value*100:.2f}%)")`,
    mcpTool: "wacc",
  },
  "relief-from-royalty": {
    slug: "relief-from-royalty", name: "Relief from Royalty", category: "income_methods",
    description: "The Relief from Royalty method values an intangible asset by estimating the hypothetical royalty payments the owner avoids by owning rather than licensing the asset. It is the most common method for IP valuation and is recommended by ASC 805/IFRS 3 for PPA.",
    formulaTex: "PV = SUM(Royalty_t * (1-T) / (1+r)^t) * TAB",
    textbookReference: "Chapter 4, Section 4.2 — Relief from Royalty Method",
    parameters: [
      { name: "revenue_projections", type: "number[]", required: true, description: "Projected revenues attributable to the asset for each period" },
      { name: "royalty_rate", type: "number", required: true, description: "Arm's length royalty rate. Typical: 1-8% of revenue depending on industry and asset type." },
      { name: "discount_rate", type: "number", required: true, description: "Annual discount rate reflecting the risk of the asset's cash flows" },
      { name: "tax_rate", type: "number", required: true, description: "Effective tax rate for the entity" },
      { name: "useful_life", type: "integer", required: true, description: "Remaining useful life of the asset in years" },
      { name: "tab_enabled", type: "boolean", required: false, description: "Apply Tax Amortization Benefit (default: true). TAB accounts for the PV of tax savings from amortizing the asset." },
    ],
    pythonCode: `from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

result = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_210_000, 1_331_000, 1_464_100],
    royalty_rate=0.05,
    discount_rate=0.15,
    tax_rate=0.21,
    useful_life=10,
    tab_enabled=True
)
print(f"Asset Value: \${result.value:,.2f}")
print(f"PV before TAB: \${result.pv_before_tab:,.2f}")
print(f"TAB Factor: {result.tab_factor:.4f}")`,
    mcpTool: "relief_from_royalty",
  },
};

export default async function MethodDocPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const method = METHODS[slug];
  if (!method) notFound();

  return (
    <div>
      <Breadcrumb items={[
        { label: "Home", href: "/" },
        { label: "Documentation", href: "/docs" },
        { label: method.name },
      ]} />

      <div className="container-narrow py-12">
        <p className="text-xs font-semibold text-primary-500 uppercase tracking-wide mb-2">{method.category}</p>
        <h1 className="text-display-sm text-primary-500 mb-4">{method.name}</h1>
        <p className="text-lg text-neutral-500 mb-8">{method.description}</p>

        <div className="mb-10">
          <FormulaDisplay
            formulaTex={method.formulaTex}
            formulaReference={method.textbookReference}
          />
        </div>

        <section className="mb-10">
          <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">Parameters</h2>
          <div className="card overflow-hidden">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-900">
                <tr>
                  <th className="text-left px-4 py-2.5 text-xs font-semibold text-neutral-400 uppercase">Parameter</th>
                  <th className="text-left px-4 py-2.5 text-xs font-semibold text-neutral-400 uppercase">Type</th>
                  <th className="text-left px-4 py-2.5 text-xs font-semibold text-neutral-400 uppercase">Required</th>
                  <th className="text-left px-4 py-2.5 text-xs font-semibold text-neutral-400 uppercase">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
                {method.parameters.map((p) => (
                  <tr key={p.name}>
                    <td className="px-4 py-2.5"><code className="text-sm font-mono text-neutral-900 dark:text-white">{p.name}</code></td>
                    <td className="px-4 py-2.5 text-sm text-neutral-500">{p.type}</td>
                    <td className="px-4 py-2.5 text-sm">
                      {p.required ? <span className="text-red-500">Required</span> : <span className="text-neutral-400">Optional</span>}
                    </td>
                    <td className="px-4 py-2.5 text-sm text-neutral-600 dark:text-neutral-400">{p.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">Python Example</h2>
          <div className="bg-neutral-950 rounded-xl p-4 overflow-x-auto">
            <pre className="text-green-400 text-sm font-mono">{method.pythonCode}</pre>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">MCP Tool</h2>
          <div className="card p-4">
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
              This method is available as an MCP tool for AI agents:
            </p>
            <code className="text-sm font-mono bg-neutral-100 dark:bg-neutral-800 px-2 py-1 rounded">{method.mcpTool}</code>
          </div>
        </section>

        <section className="card p-6">
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-3">Try it live</h2>
          <p className="text-sm text-neutral-500 mb-4">
            Use the interactive calculator to run this method with your own data and see the step-by-step proof.
          </p>
          <Link
            href={`/calculator/${method.slug}`}
            className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
          >
            Open Calculator
          </Link>
        </section>
      </div>
    </div>
  );
}
