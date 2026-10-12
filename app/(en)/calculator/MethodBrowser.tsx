"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import { CATALOG } from "@/lib/valuation/catalog";
import { cn } from "@/lib/utils/cn";
import type { MethodCategory } from "@/lib/valuation/types";

const CATEGORIES: { value: MethodCategory | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "core", label: "Core Methods" },
  { value: "approaches", label: "Valuation Approaches" },
  { value: "income_methods", label: "Income Methods" },
  { value: "asset_types", label: "Asset Types" },
  { value: "advanced", label: "Advanced Topics" },
];

export function MethodBrowser({ initialCategory }: { initialCategory: MethodCategory | "all" }) {
  const [category, setCategory] = useState<MethodCategory | "all">(initialCategory);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    return CATALOG.filter((m) => {
      const matchCategory = category === "all" || m.category === category;
      const q = query.trim().toLowerCase();
      const matchQuery =
        !q || m.name.toLowerCase().includes(q) || m.slug.includes(q) || m.description.toLowerCase().includes(q);
      return matchCategory && matchQuery;
    });
  }, [category, query]);

  return (
    <div className="container-page py-12">
      <div className="max-w-3xl mx-auto text-center mb-10">
        <h1 className="text-display-sm text-primary-500 mb-4">Valuation Calculator</h1>
        <p className="text-lg text-neutral-500 text-balance">
          Choose from {CATALOG.length} textbook-verified valuation methods. Every calculation shows the formula,
          step-by-step proof, and source citation.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6 max-w-3xl mx-auto">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Search methods…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-8 max-w-3xl mx-auto">
        {CATEGORIES.map((c) => (
          <button
            key={c.value}
            onClick={() => setCategory(c.value)}
            className={cn(
              "px-4 py-1.5 rounded-full text-sm font-medium transition-colors",
              category === c.value
                ? "bg-primary-500 text-white"
                : "border border-neutral-300 dark:border-neutral-700 text-neutral-600 dark:text-neutral-400 hover:border-primary-300 dark:hover:border-primary-700"
            )}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((m) => (
          <Link
            key={m.slug}
            href={`/calculator/${m.slug}`}
            className="card p-5 hover:shadow-elevation hover:border-primary-200 dark:hover:border-primary-800 transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-primary-500 uppercase tracking-wide">
                {CATEGORIES.find((c) => c.value === m.category)?.label ?? m.category}
              </span>
              <span
                className={cn(
                  "text-xs px-1.5 py-0.5 rounded-full",
                  m.complexity === "basic"
                    ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                    : m.complexity === "intermediate"
                      ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
                      : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                )}
              >
                {m.complexity}
              </span>
            </div>
            <h3 className="font-serif font-semibold text-neutral-900 dark:text-white mb-1 group-hover:text-primary-600">
              {m.name}
            </h3>
            <p className="text-xs text-neutral-500 line-clamp-2 mb-2">{m.description}</p>
            <p className="text-xs text-neutral-400 font-mono">{m.textbookReference}</p>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-neutral-500 py-12">No methods match your search.</p>
      )}
    </div>
  );
}
