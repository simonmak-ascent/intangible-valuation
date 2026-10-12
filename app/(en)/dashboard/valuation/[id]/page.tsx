"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ValuationResultCard } from "@/components/valuation/ValuationResultCard";
import { getDashboardValuationDetail } from "@/lib/valuation/client";
import type { SavedValuationDetail } from "@/lib/valuation/types";

export default function ValuationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [valuation, setValuation] = useState<SavedValuationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardValuationDetail(id)
      .then((data) => setValuation(data as SavedValuationDetail))
      .catch((err) => setError(err instanceof Error ? err.message : "Valuation not found"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="container-page py-8 animate-pulse">
        <div className="h-8 w-48 bg-neutral-200 dark:bg-neutral-700 rounded mb-6" />
        <div className="h-48 bg-neutral-100 dark:bg-neutral-800 rounded-xl" />
      </div>
    );
  }

  if (error || !valuation) {
    return (
      <div className="container-page py-8">
        <div className="card p-8 text-center">
          <h2 className="text-lg font-serif font-semibold mb-3">Valuation Not Found</h2>
          <p className="text-neutral-500 mb-4">{error}</p>
          <Link href="/dashboard" className="text-primary-500 font-medium text-sm">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  const result = {
    value: valuation.result_value,
    method: valuation.method,
    formula_reference: valuation.formula_reference,
    steps: valuation.steps,
    assumptions: valuation.assumptions,
    inputs: valuation.inputs,
    pv_before_tab: valuation.pv_before_tab,
    tab_factor: valuation.tab_factor,
  };

  return (
    <div className="container-page py-8">
      <Link href="/dashboard" className="text-sm text-primary-500 hover:text-primary-600 mb-4 inline-block">
        &larr; Back to Dashboard
      </Link>
      <div className="mb-6">
        <p className="text-xs text-neutral-400">
          Saved on {new Date(valuation.created_at).toLocaleString()}
          {valuation.asset_type && ` • ${valuation.asset_type}`}
          {valuation.business_stage && ` • ${valuation.business_stage}`}
        </p>
      </div>
      <ValuationResultCard result={result} />
    </div>
  );
}
