import type { MetadataRoute } from "next";
import { CATALOG_SLUGS } from "@/lib/valuation/catalog";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.ascent-partners.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE_URL}/calculator`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/mcp`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/skills`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/about`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/terms`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/privacy`, changeFrequency: "yearly", priority: 0.3 },
  ];

  const methodPages: MetadataRoute.Sitemap = CATALOG_SLUGS.map((slug) => ({
    url: `${BASE_URL}/calculator/${slug}`,
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  return [...staticPages, ...methodPages];
}
