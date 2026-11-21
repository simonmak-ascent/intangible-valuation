import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { FormulaDisplay } from "@/components/valuation/FormulaDisplay";
import { CATALOG_SLUGS, getCatalogMethod } from "@/lib/valuation/catalog";

/**
 * Runnable samples for the methods whose examples have been written and checked by hand.
 *
 * The other catalog methods are documented from the catalog itself — description, formula, textbook
 * reference, parameter table and the MCP path — and link to the calculator, which calls the same
 * library function through the API. A generated snippet would carry invented numbers into a page
 * whose whole purpose is to be copied from, which is worse than no snippet at all.
 */
const SAMPLES: Record<string, string> = {
  "present-value": `from intangible_valuation.core.time_value import present_value

result = present_value(
    future_value=100000,
    discount_rate=0.10,
    periods=5
)
print(f"Present Value: \${result.value:,.2f}")`,
  capm: `from intangible_valuation.core.discount_rates import capm_discount_rate

result = capm_discount_rate(
    risk_free_rate=0.04,
    beta=1.2,
    market_return=0.10
)
print(f"Cost of Equity: {result.value:.4f} ({result.value*100:.1f}%)")`,
  wacc: `from intangible_valuation.core.discount_rates import wacc

result = wacc(
    equity_value=1_000_000,
    debt_value=200_000,
    cost_of_equity=0.12,
    cost_of_debt=0.05,
    tax_rate=0.21
)
print(f"WACC: {result.value:.4f} ({result.value*100:.2f}%)")`,
  "relief-from-royalty": `from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

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
};

/**
 * Every catalog method, statically generated. `dynamicParams = false` makes anything else a real 404
 * at routing: without it `notFound()` runs after the group's `loading.tsx` has flushed a 200 shell,
 * so an unknown path answered 200 with a "Page not found" body.
 */
export function generateStaticParams() {
  return CATALOG_SLUGS.map((slug) => ({ slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const method = getCatalogMethod(slug);
  if (!method) return {};
  // No `alternates` here on purpose. A page-level `alternates` replaces the layout's wholesale, so
  // adding a canonical would drop the root's hreflang map (x-default, en-GB, zh-Hans, zh-Hant-HK) on
  // all 68 pages, and a relative canonical without `metadataBase` is emitted verbatim rather than
  // resolved. Setting `metadataBase` at the root is the right fix for both, and it is not this change.
  return {
    title: method.name,
    description: method.description,
  };
}

export default async function MethodDocPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const method = getCatalogMethod(slug);
  if (!method) notFound();

  // Read from the catalog, never repeated here: it is what `tests/test_catalog_alignment.py` proves
  // against the tool surface, and this page is where the old false claim was rendered.
  const mcp = method.mcp;
  const sample = SAMPLES[slug];

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

        {sample ? (
          <section className="mb-10">
            <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">Python Example</h2>
            <div className="bg-neutral-950 rounded-xl p-4 overflow-x-auto">
              <pre className="text-green-400 text-sm font-mono">{sample}</pre>
            </div>
          </section>
        ) : (
          <section className="mb-10">
            <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">Running it</h2>
            <div className="card p-4">
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Call <code className="font-mono">{method.pythonFunction}</code> with the parameters above, or use the
                calculator, which posts the same arguments to the API and shows the step-by-step result. No code sample
                is published here because this method has none that has been checked by hand.
              </p>
            </div>
          </section>
        )}

        <section className="mb-10">
          <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mb-4">MCP Tool</h2>
          <div className="card p-4">
            {mcp ? (
              <>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
                  This method is available to AI agents through the MCP tool:
                </p>
                <code className="text-sm font-mono bg-neutral-100 dark:bg-neutral-800 px-2 py-1 rounded">{mcp.tool}</code>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-3">
                  selected with <code className="font-mono">{mcp.methods.length === 1 ? `method: "${mcp.methods[0]}"` : `method: one of ${mcp.methods.map((m) => `"${m}"`).join(" | ")}`}</code>
                </p>
              </>
            ) : (
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                This method is served by the HTTP API only. No MCP tool dispatches to it.
              </p>
            )}
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
