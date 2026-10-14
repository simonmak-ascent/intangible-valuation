import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.ascent-partners.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/dashboard", "/admin", "/sign-in", "/sign-up", "/v1/"] },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
