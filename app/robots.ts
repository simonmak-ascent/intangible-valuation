import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.ascent-partners.com";

export default function robots(): MetadataRoute.Robots {
  return {
    // The account paths that used to be listed here (/dashboard, /admin, /sign-in, /sign-up) no longer
    // exist; a disallow for a 404 is a statement about a site that is not this one.
    rules: { userAgent: "*", allow: "/", disallow: ["/v1/"] },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
