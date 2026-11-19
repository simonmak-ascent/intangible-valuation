import type { CitationChain } from "./citation";

export interface ValuationResult {
  value: number;
  method: string;
  formula_reference: string;
  steps: string[];
  assumptions: string[];
  inputs: Record<string, unknown>;
  pv_before_tab?: number;
  tab_factor?: number;
  metadata?: {
    category?: string;
    asset_type?: string;
    textbook_chapter?: string;
  };
}

export interface MethodParameter {
  name: string;
  type: "number" | "number[]" | "integer" | "boolean" | "string" | "json";
  required: boolean;
  description: string;
  default?: unknown;
  minimum?: number;
  maximum?: number;
  options?: { label: string; value: string }[];
}

export interface MethodDefinition {
  slug: string;
  name: string;
  category: MethodCategory;
  subcategory?: string;
  assetTypes?: string[];
  businessStages?: BusinessStage[];
  description: string;
  formulaTex?: string;
  textbookReference: string;
  parameters: MethodParameter[];
  pythonFunction: string;
  mcpTool?: string;
  skillReference?: string;
  complexity: "basic" | "intermediate" | "advanced";
}

export type MethodCategory =
  | "core"
  | "approaches"
  | "income_methods"
  | "asset_types"
  | "advanced";

export type BusinessStage = "startup" | "growth" | "mature";

export interface ValuationRequest {
  method: string;
  params: Record<string, unknown>;
  businessStage?: BusinessStage;
}

export interface ValuationResponse {
  result: ValuationResult;
  error?: string;
}

export interface ApiError {
  error: string;
  message: string;
  missing_fields?: string[];
  invalid_fields?: Record<string, string>;
  available_methods?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface BenchmarkRecord {
  category: "royalty_rate" | "discount_rate" | "useful_life" | "growth_rate";
  // "all" is real: three records are not stage-specific and the value is returned verbatim. It is not
  // a wildcard here — `business_stage` is matched exactly, as the SQL did — so a stage filter excludes
  // those three. Only `asset_type` and `industry` treat "all" as "applies to every value".
  business_stage: BusinessStage | "all";
  asset_type: string;
  industry: string;
  metric_name: string;
  value: number;
  unit?: string;
  p25?: number;
  p75?: number;
  /** Every record carries its own chain; the file is the source of truth, so it is returned verbatim. */
  citation: CitationChain;
}

/** Query parameters `GET /v1/benchmarks` accepts. Absent or empty means "do not filter on this field". */
export interface BenchmarkFilter {
  category?: string;
  business_stage?: string;
  asset_type?: string;
  industry?: string;
}

export interface SkillDefinition {
  slug: string;
  name: string;
  description: string;
  category?: string;
  markdownPath: string;
  mcpToolsRequired?: string[];
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}
