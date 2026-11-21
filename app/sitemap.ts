import type { MetadataRoute } from "next";
import { CATALOG_SLUGS } from "@/lib/valuation/catalog";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.ascent-partners.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE_URL}/calculator`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/developers/mcp`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/skills`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/about`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/terms`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/privacy`, changeFrequency: "yearly", priority: 0.3 },
  ];

  // Every catalog method is both a calculator and a documentation page since 2026-11-21. The calculator
  // URLs were already listed; the docs URLs were not, because before that only four slugs had a page and
  // the other 64 answered 404 under `dynamicParams = false`.
  const methodPages: MetadataRoute.Sitemap = CATALOG_SLUGS.flatMap((slug) => [
    { url: `${BASE_URL}/calculator/${slug}`, changeFrequency: "monthly" as const, priority: 0.8 },
    { url: `${BASE_URL}/docs/${slug}`, changeFrequency: "monthly" as const, priority: 0.6 },
  ]);

  return [...staticPages, ...methodPages];
}
