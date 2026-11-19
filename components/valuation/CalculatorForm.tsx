"use client";

import { useState, useCallback } from "react";
import type { MethodParameter, ValuationResult, BusinessStage } from "@/lib/valuation/types";
import { StageSelector } from "./StageSelector";
import { ValuationResultCard } from "./ValuationResultCard";

interface CalculatorFormProps {
  methodSlug: string;
  methodName: string;
  parameters: MethodParameter[];
  stageDefaults?: Record<BusinessStage, Record<string, number>>;
  onCalculate: (params: Record<string, unknown>, stage: BusinessStage) => Promise<ValuationResult>;
}

export function CalculatorForm({
  methodSlug,
  methodName,
  parameters,
  stageDefaults,
  onCalculate,
}: CalculatorFormProps) {
  const [stage, setStage] = useState<BusinessStage>("growth");
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<ValuationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleStageChange = useCallback(
    (newStage: BusinessStage) => {
      setStage(newStage);
      if (stageDefaults?.[newStage]) {
        const defaults: Record<string, string> = {};
        Object.entries(stageDefaults[newStage]).forEach(([key, value]) => {
          defaults[key] = String(value);
        });
        setFormValues((prev) => ({ ...defaults, ...prev }));
      }
    },
    [stageDefaults]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const params: Record<string, unknown> = {};
      for (const param of parameters) {
        const raw = formValues[param.name];
        if (param.required && (raw === undefined || raw === "")) {
          throw new Error(`Missing required field: ${param.name}`);
        }
        if (raw !== undefined && raw !== "") {
          if (param.type === "number[]") {
            params[param.name] = raw.split(",").map(Number);
          } else if (param.type === "json") {
            params[param.name] = JSON.parse(raw);
          } else if (param.type === "boolean") {
            params[param.name] = raw === "true";
          } else if (param.type === "number" || param.type === "integer") {
            params[param.name] = Number(raw);
          } else {
            params[param.name] = raw;
          }
        }
      }

      const valuationResult = await onCalculate(params, stage);
      setResult(valuationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Calculation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="card-elevated p-6 space-y-5">
        <div>
          <label className="block text-sm font-semibold text-neutral-900 dark:text-white mb-2">
            Business Stage
          </label>
          <StageSelector value={stage} onChange={handleStageChange} />
        </div>

        {parameters.map((param) => (
          <div key={param.name}>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5">
              {param.name.replace(/_/g, " ")}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>

            {param.type === "boolean" ? (
              <select
                value={formValues[param.name] || "true"}
                onChange={(e) => setFormValues((prev) => ({ ...prev, [param.name]: e.target.value }))}
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            ) : param.type === "number[]" ? (
              <input
                type="text"
                placeholder="e.g., 1000000, 1100000, 1210000"
                value={formValues[param.name] || ""}
                onChange={(e) => setFormValues((prev) => ({ ...prev, [param.name]: e.target.value }))}
                required={param.required}
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono"
              />
            ) : param.type === "json" ? (
              <input
                type="text"
                placeholder='e.g., {"key": "value"}'
                value={formValues[param.name] || ""}
                onChange={(e) => setFormValues((prev) => ({ ...prev, [param.name]: e.target.value }))}
                required={param.required}
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono"
              />
            ) : (
              <input
                type="number"
                step={param.type === "integer" ? "1" : "0.01"}
                placeholder={param.description}
                value={formValues[param.name] || ""}
                onChange={(e) => setFormValues((prev) => ({ ...prev, [param.name]: e.target.value }))}
                required={param.required}
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono"
              />
            )}

            <p className="text-xs text-neutral-400 mt-1">{param.description}</p>
          </div>
        ))}

        <button
          type="submit"
          disabled={loading}
          className="w-full inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Calculating..." : `Calculate ${methodName}`}
        </button>
      </form>

      {error && (
        <div className="card p-4 border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {result && <ValuationResultCard result={result} />}
    </div>
  );
}
