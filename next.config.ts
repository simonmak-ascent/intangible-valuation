import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  images: {
    formats: ["image/avif", "image/webp"],
  },
  // The library reference is static output under public/docs (Dockerfile.web, docs stage). It must be
  // served from a URL whose base ends in /docs/, because MkDocs emits relative asset and nav URLs:
  // at bare /docs they would resolve against / and 404 (there is no public/assets). A redirect, not a
  // rewrite — a rewrite keeps the URL at /docs and the stylesheet still misses.
  async redirects() {
    return [{ source: "/docs", destination: "/docs/index.html", permanent: false }];
  },
  headers: async () => [
    {
      source: "/(.*)",
      headers: [
        {
          key: "Strict-Transport-Security",
          value: "max-age=63072000; includeSubDomains; preload",
        },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      ],
    },
    {
      source: "/api/(.*)",
      headers: [
        { key: "Access-Control-Allow-Origin", value: "*" },
        { key: "Access-Control-Allow-Methods", value: "GET, POST, OPTIONS" },
        { key: "Access-Control-Allow-Headers", value: "Content-Type, Authorization" },
      ],
    },
  ],
};

export default nextConfig;
