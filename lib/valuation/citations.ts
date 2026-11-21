import { CATALOG } from "./catalog";
import type { MethodCategory } from "./types";

export type CitationKind =
  | "textbook"
  | "standard"
  | "paper"
  | "data-vendor"
  | "official-source";

export interface Citation {
  id: string;
  title: string;
  kind: CitationKind;
  authors?: string;
  year?: number;
  publisher?: string;
  url?: string;
  section?: string;
}

export const SOURCE_REGISTRY: Record<string, Citation> = {
  "ias-38": {
    id: "ias-38",
    title: "IAS 38 — Intangible Assets",
    kind: "standard",
    publisher: "IFRS Foundation",
    year: 2024,
    url: "https://www.ifrs.org/issued-standards/list-of-standards/ias-38-intangible-assets/",
  },
  "ifrs-13": {
    id: "ifrs-13",
    title: "IFRS 13 — Fair Value Measurement",
    kind: "standard",
    publisher: "IFRS Foundation",
    year: 2013,
    url: "https://www.ifrs.org/issued-standards/list-of-standards/ifrs-13-fair-value-measurement/",
  },
  "ivs-2025": {
    id: "ivs-2025",
    title: "International Valuation Standards (IVS) 2025 — incl. IVS 104, 105, 106, 210",
    kind: "standard",
    publisher: "International Valuation Standards Council",
    year: 2025,
    url: "https://www.ivsc.org/",
  },
  "ias-36": {
    id: "ias-36",
    title: "IAS 36 — Impairment of Assets",
    kind: "standard",
    publisher: "IFRS Foundation",
    year: 2024,
    url: "https://www.ifrs.org/issued-standards/list-of-standards/ias-36-impairment-of-assets/",
  },
  "asc-350": {
    id: "asc-350",
    title: "ASC 350 — Intangibles — Goodwill and Other",
    kind: "standard",
    publisher: "FASB",
    year: 2024,
    url: "https://asc.fasb.org/350",
  },
  "asc-805": {
    id: "asc-805",
    title: "ASC 805 — Business Combinations",
    kind: "standard",
    publisher: "FASB",
    year: 2024,
    url: "https://asc.fasb.org/805",
  },
  "asc-820": {
    id: "asc-820",
    title: "ASC 820 — Fair Value Measurement",
    kind: "standard",
    publisher: "FASB",
    year: 2024,
    url: "https://asc.fasb.org/820",
  },
  "isae-3000": {
    id: "isae-3000",
    title: "ISAE 3000 (Revised) — Assurance Engagements Other than Audits/Reviews",
    kind: "standard",
    publisher: "IAASB",
    year: 2013,
    url: "https://www.iaasb.org/",
  },
  "aicpa-vs": {
    id: "aicpa-vs",
    title: "AICPA Valuation of Privately-Held-Company Equity Securities Issued as Compensation",
    kind: "standard",
    publisher: "AICPA",
    year: 2013,
  },
  damodaran: {
    id: "damodaran",
    title: "Damodaran on Valuation & Online Datasets (ERP, betas, risk-free rates)",
    kind: "paper",
    authors: "Aswath Damodaran",
    publisher: "NYU Stern",
    url: "https://pages.stern.nyu.edu/~adamodar/",
  },
  wipo: {
    id: "wipo",
    title: "WIPO — Intellectual Property Valuation and Licensing Guidance",
    kind: "official-source",
    publisher: "World Intellectual Property Organization",
    url: "https://www.wipo.int/",
  },
  fred: {
    id: "fred",
    title: "FRED — Federal Reserve Economic Data",
    kind: "data-vendor",
    publisher: "Federal Reserve Bank of St. Louis",
    url: "https://fred.stlouisfed.org/",
  },
  hkex: {
    id: "hkex",
    title: "HKEXnews — Listed Company Information and Announcements",
    kind: "official-source",
    publisher: "Hong Kong Exchanges and Clearing",
    url: "https://www.hkexnews.hk/",
  },
};

const CATEGORY_STANDARDS: Record<MethodCategory, string[]> = {
  core: ["ifrs-13"],
  approaches: ["ivs-2025", "ifrs-13"],
  income_methods: ["ias-38", "ifrs-13", "ivs-2025"],
  asset_types: ["ias-38", "ivs-2025"],
  advanced: ["ias-38", "ifrs-13", "ivs-2025"],
};

const EXTRA_CITATIONS: Record<string, string[]> = {
  "capm": ["damodaran"],
  "wacc": ["damodaran"],
  "build-up-discount-rate": ["damodaran"],
  "terminal-value": ["damodaran"],
  "relief-from-royalty": ["wipo", "ivs-2025"],
  "mpeem": ["damodaran"],
  "purchase-price-allocation": ["asc-805", "ifrs-13"],
  "cash-generating-unit-impairment": ["ias-36"],
  "goodwill-impairment": ["asc-350", "ias-36"],
  "intangible-impairment-test": ["ias-36", "ias-38"],
  "deferred-tax-liability-ppa": ["asc-805"],
  "bargain-purchase-analysis": ["asc-805", "ifrs-13"],
};

export function getMethodCitations(slug: string): Citation[] {
  const method = CATALOG.find((m) => m.slug === slug);
  if (!method) return [];

  const result: Citation[] = [
    {
      id: `textbook:${method.slug}`,
      title: "Intangible Asset Valuation (source book)",
      kind: "textbook",
      section: method.textbookReference,
    },
  ];

  const seen = new Set<string>();
  const ids = [
    ...(CATEGORY_STANDARDS[method.category] ?? []),
    ...(EXTRA_CITATIONS[method.slug] ?? []),
  ];
  for (const id of ids) {
    const citation = SOURCE_REGISTRY[id];
    if (citation && !seen.has(citation.id)) {
      seen.add(citation.id);
      result.push(citation);
    }
  }
  return result;
}

export function citationCoverage(): string[] {
  return CATALOG.filter((m) => {
    const citations = getMethodCitations(m.slug);
    return !citations.some((c) => c.kind !== "textbook");
  }).map((m) => m.slug);
}
