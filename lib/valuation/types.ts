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

export interface Benchmark {
  id: string;
  category: "royalty_rate" | "discount_rate" | "useful_life" | "growth_rate";
  business_stage: BusinessStage;
  asset_type: string;
  industry: string;
  metric_name: string;
  value: number;
  unit?: string;
  p25?: number;
  p75?: number;
  source: string;
  source_url?: string;
}

export interface StageDefaults {
  businessStage: BusinessStage;
  discountRate: { median: number; low: number; high: number };
  royaltyRate: { median: number; low: number; high: number };
  usefulLife: { median: number; low: number; high: number };
  growthRate: { median: number; low: number; high: number };
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
