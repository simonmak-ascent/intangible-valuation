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

/**
 * How a parameter is rendered. Extracted so the decision can be asserted without a DOM — the form
 * used to fall through to `<input type="number">` for every type it did not name, and a `string`
 * parameter then accepted nothing: the browser rejects "IAS36" in a number input, so the standard
 * was never sent and the calculation silently ran as ASC 350.
 */
export type FieldKind = "boolean" | "number-array" | "json" | "select" | "text" | "number";

export function fieldKind(param: MethodParameter): FieldKind {
  if (param.type === "boolean") return "boolean";
  if (param.type === "number[]") return "number-array";
  if (param.type === "json") return "json";
  if (param.type === "string") return param.options && param.options.length > 0 ? "select" : "text";
  if (param.type === "number" || param.type === "integer") return "number";
  // Exhaustive: a new member of MethodParameter["type"] fails `tsc` here instead of silently
  // rendering a number input for a value it cannot hold — which is the defect this function exists
  // to prevent, reintroduced one union member at a time.
  const unhandled: never = param.type;
  return unhandled;
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

            {(() => {
              const kind = fieldKind(param);
              const common = {
                value: formValues[param.name] || "",
                onChange: (e: { target: { value: string } }) =>
                  setFormValues((prev) => ({ ...prev, [param.name]: e.target.value })),
                required: param.required,
                className:
                  "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono",
              };

              if (kind === "boolean") {
                return (
                  <select {...common} value={formValues[param.name] || "true"}>
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                  </select>
                );
              }

              if (kind === "select") {
                // A fixed domain gets a select: the impairment `standard` is ASC350 or IAS36, and a
                // free-text field turns a typo into a pydantic pattern error at the server.
                return (
                  <select {...common}>
                    <option value="">Choose…</option>
                    {(param.options ?? []).map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                );
              }

              if (kind === "text") {
                return <input type="text" placeholder={param.description} {...common} />;
              }

              if (kind === "number-array") {
                return <input type="text" placeholder="e.g., 1000000, 1100000, 1210000" {...common} />;
              }

              if (kind === "json") {
                return <input type="text" placeholder='e.g., {"key": "value"}' {...common} />;
              }

              return <input type="number" step={param.type === "integer" ? "1" : "0.01"} placeholder={param.description} {...common} />;
            })()}

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
