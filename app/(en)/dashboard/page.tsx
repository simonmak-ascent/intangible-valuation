"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";
import { getDashboardValuations } from "@/lib/valuation/client";
import { getCatalogMethod } from "@/lib/valuation/catalog";
import type { SavedValuation } from "@/lib/valuation/types";

export default function DashboardPage() {
  const [valuations, setValuations] = useState<SavedValuation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardValuations({ page: 1, limit: 50 })
      .then((data) => {
        const res = data as { valuations?: SavedValuation[] };
        setValuations(res.valuations ?? []);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load valuations"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container-page py-8">
      <div className="flex gap-8">
        <DashboardSidebar />

        <div className="flex-1 min-w-0">
          <div className="mb-8">
            <h1 className="text-display-sm text-primary-500 mb-2">Dashboard</h1>
            <p className="text-neutral-500">
              Your saved valuations, audit trail, and export options.
            </p>
          </div>

          {loading ? (
            <div className="card p-8 text-center">
              <p className="text-neutral-500">Loading...</p>
            </div>
          ) : error ? (
            <div className="card p-8 text-center border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950">
              <p className="text-sm text-red-600 dark:text-red-400 mb-4">{error}</p>
              <p className="text-xs text-neutral-500">
                Sign in to view your saved valuations. If you are signed in, verify SurrealDB is reachable.
              </p>
            </div>
          ) : valuations.length === 0 ? (
            <div className="card p-12 text-center">
              <h3 className="text-lg font-serif font-semibold text-neutral-900 dark:text-white mb-3">
                No valuations yet
              </h3>
              <p className="text-neutral-500 mb-6">
                Run a valuation calculation to see it saved here. All results are stored with full audit trail.
              </p>
              <Link
                href="/calculator"
                className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
              >
                Start Valuing
              </Link>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <table className="w-full">
                <thead className="bg-neutral-50 dark:bg-neutral-900">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-400 uppercase">Method</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-400 uppercase">Category</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-neutral-400 uppercase">Result</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-neutral-400 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
                  {valuations.map((v) => (
                    <tr key={v.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-colors">
                      <td className="px-4 py-3">
                        <Link
                          href={`/dashboard/valuation/${v.id}`}
                          className="text-sm font-medium text-primary-500 hover:text-primary-600"
                        >
                          {v.name || getCatalogMethod(v.method)?.name || v.method}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-neutral-500">{v.category}</td>
                      <td className="px-4 py-3 text-sm text-right font-mono text-neutral-900 dark:text-white">
                        ${v.result_value.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-neutral-400">
                        {new Date(v.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
