"use client";

import Link from "next/link";
import { CalculatorForm } from "@/components/valuation/CalculatorForm";
import { FormulaDisplay } from "@/components/valuation/FormulaDisplay";
import { ParameterGuide } from "@/components/valuation/ParameterGuide";
import type { ValuationResult, BusinessStage } from "@/lib/valuation/types";
import { calculateValuation } from "@/lib/valuation/client";
import { getCatalogMethod } from "@/lib/valuation/catalog";
import { getMethodCitations } from "@/lib/valuation/citations";

interface MethodCalculatorProps {
  slug: string;
}

const STAGE_DEFAULTS: Record<BusinessStage, Record<string, number>> = {
  startup: { discount_rate: 0.25, royalty_rate: 0.06, useful_life: 5, growth_rate: 0.5 },
  growth: { discount_rate: 0.15, royalty_rate: 0.05, useful_life: 10, growth_rate: 0.2 },
  mature: { discount_rate: 0.08, royalty_rate: 0.04, useful_life: 15, growth_rate: 0.03 },
};

export function MethodCalculator({ slug }: MethodCalculatorProps) {
  const method = getCatalogMethod(slug);

  if (!method) {
    return (
      <div className="card p-8 text-center">
        <h2 className="text-xl font-serif font-semibold text-neutral-900 dark:text-white mb-3">Method Not Found</h2>
        <p className="text-neutral-500">No method found for &quot;{slug}&quot;</p>
        <Link href="/calculator" className="inline-block mt-4 text-primary-500 hover:text-primary-600 font-medium text-sm">
          Browse all methods
        </Link>
      </div>
    );
  }

  const handleCalculate = async (params: Record<string, unknown>): Promise<ValuationResult> => {
    return calculateValuation(slug, params);
  };

  const citations = getMethodCitations(slug);

  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs font-semibold text-primary-500 uppercase tracking-wide mb-1">{method.category}</p>
        <h1 className="text-display-sm text-primary-500 mb-3">{method.name}</h1>
        <p className="text-neutral-500">{method.description}</p>
      </div>

      <FormulaDisplay
        formulaTex={method.formulaTex}
        formulaReference={method.textbookReference}
      />

      {citations.length > 0 && (
        <section aria-labelledby="sources-heading" className="card p-5">
          <h2 id="sources-heading" className="text-sm font-semibold text-neutral-900 dark:text-white mb-3">
            Sources &amp; references
          </h2>
          <ul className="space-y-2">
            {citations.map((c) => (
              <li key={c.id} className="text-sm text-neutral-600 dark:text-neutral-400">
                <span className="font-medium text-neutral-700 dark:text-neutral-300">{c.title}</span>
                {c.section ? <span className="text-neutral-400"> — {c.section}</span> : null}
                {c.publisher ? <span className="text-neutral-400"> ({c.publisher})</span> : null}
                {c.url ? (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-primary-500 hover:text-primary-600"
                  >
                    link
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <CalculatorForm
            methodSlug={slug}
            methodName={method.name}
            parameters={method.parameters}
            stageDefaults={STAGE_DEFAULTS}
            onCalculate={handleCalculate}
          />
        </div>
        <div className="lg:col-span-1">
          <ParameterGuide
            parameters={method.parameters}
          />
        </div>
      </div>
    </div>
  );
}
