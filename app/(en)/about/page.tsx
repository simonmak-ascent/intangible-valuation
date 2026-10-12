import { Breadcrumb } from "@/components/layout/Breadcrumb";

export default function AboutPage() {
  return (
    <div className="container-narrow py-12">
      <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "About" }]} />

      <h1 className="text-display-sm text-primary-500 mt-6 mb-6">About the Platform</h1>

      <div className="prose prose-neutral dark:prose-invert max-w-none">
        <p className="text-lg text-neutral-500 mb-8">
          The Intangible Asset Valuation Platform is the most authoritative, traceable, and auditable
          source of intangible asset valuation methodology on the internet. Built on the textbook
          &ldquo;Intangible Asset Valuation&rdquo; by Ascent Partners, every formula, calculation, and
          output is verified against academic and professional standards.
        </p>

        <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mt-10 mb-4">
          Our Methodology
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          All 68 valuation methods are implemented as pure, deterministic, side-effect-free Python
          functions. Each function returns a <code>ValuationResult</code> with the calculated value,
          formula reference, step-by-step breakdown, and assumptions. Every function is backed by
          1,000+ unit tests that verify outputs against textbook expected values.
        </p>

        <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mt-10 mb-4">
          Regulatory Coverage
        </h2>
        <ul className="space-y-2 text-neutral-600 dark:text-neutral-400">
          <li><strong>ASC 805 / IFRS 3</strong> — Purchase Price Allocation (PPA)</li>
          <li><strong>ASC 350 / IAS 36</strong> — Goodwill and Intangible Impairment Testing</li>
          <li><strong>OECD TP Guidelines</strong> — Transfer Pricing for Intangible Assets</li>
          <li><strong>IRC Section 482</strong> — US Transfer Pricing Regulations</li>
        </ul>

        <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mt-10 mb-4">
          Technology
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          Open-source Python library published on PyPI. Next.js WebApp deployed on Vercel.
          SurrealDB 3.x for persistent data and audit trails. Model Context Protocol (MCP) server
          for AI agent integration. 49 tools available for LLM-powered valuation workflows.
        </p>

        <h2 className="font-serif text-xl font-semibold text-neutral-900 dark:text-white mt-10 mb-4">
          Credits
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          All valuation formulas and methodologies trace to the textbook:
        </p>
        <blockquote className="border-l-4 border-primary-500 pl-4 italic text-neutral-500">
          &ldquo;Intangible Asset Valuation — A Practitioner&apos;s Guide to Cost, Market, and Income Approaches&rdquo;<br />
          Ascent Partners, 2025
        </blockquote>
      </div>
    </div>
  );
}
