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
  //
  // /mcp is a temporary redirect, not a page: the MCP endpoint is moving from /api/mcp to /mcp at the
  // edge (an ALB rule owned by apg-infra), and this page had to leave the path so it can be served by
  // the iv-mcp container. Until that rule lands, /mcp keeps working as a redirect to the moved page
  // rather than 404ing; once it lands the edge answers first and this entry never fires.
  async redirects() {
    return [
      { source: "/docs", destination: "/docs/index.html", permanent: false },
      { source: "/mcp", destination: "/developers/mcp", permanent: false },
    ];
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
        // The directives that need no nonce, and therefore work with a static headers() block.
        // `script-src` is deliberately absent: the App Router emits inline payloads (`self.__next_f.push`,
        // 17 of them on the home page, measured 2026-11-20), so `script-src 'self'` breaks hydration;
        // a nonce requires per-request middleware, and middleware.ts is deliberately deleted. Claiming
        // `script-src` here without a nonce would be theatre. `frame-ancestors` duplicates
        // X-Frame-Options for browsers that only honour the modern directive.
        {
          key: "Content-Security-Policy",
          value: "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
        },
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
