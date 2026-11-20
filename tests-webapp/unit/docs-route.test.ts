import { describe, it, expect } from "vitest";
import nextConfig from "../../next.config";

/**
 * The library reference is MkDocs output copied into `public/docs` by the image's docs stage
 * (docker/Dockerfile.web). MkDocs emits **relative** asset and nav URLs, so the page must be served from a
 * URL whose base ends in `/docs/`: at bare `/docs` the stylesheet resolves to `/assets/…` and 404s.
 * That is why this is a redirect to `/docs/index.html`, not a rewrite, and why the assertion below
 * checks the destination rather than just "a rule exists".
 */
describe("the /docs surface", () => {
  it("redirects the bare path to the index MkDocs emits", async () => {
    const redirects = (await nextConfig.redirects?.()) ?? [];
    const docs = redirects.find((r) => r.source === "/docs");

    expect(docs, "no redirect covers /docs — the Docs link in the header would 404").toBeDefined();
    expect(docs?.destination).toBe("/docs/index.html");
    expect(docs?.permanent).toBe(false);
  });

  it("does not publish a second copy of the reference under a rewrite", async () => {
    const rewrites = (await nextConfig.rewrites?.()) ?? [];
    const list = Array.isArray(rewrites) ? rewrites : await rewrites;

    for (const entry of list) {
      const rules = "source" in entry ? [entry] : entry;
      for (const rule of rules) {
        expect(rule.destination).not.toBe("/docs/index.html");
      }
    }
  });
});

/**
 * `/mcp` is a temporary hold-the-URL redirect, not a page: the MCP endpoint moves to `/mcp` at the
 * edge (an ALB rule owned by apg-infra), so the guide page had to leave the path for the container.
 * `permanent` must stay `false` — a 308 is cached by browsers past the point the edge takes the path,
 * which would leave readers on a redirect that no longer describes where the endpoint lives.
 */
describe("the /mcp surface", () => {
  it("redirects the endpoint path to the moved page while the edge rule is pending", async () => {
    const redirects = (await nextConfig.redirects?.()) ?? [];
    const mcp = redirects.find((r) => r.source === "/mcp");

    expect(mcp, "no redirect covers /mcp — the URL would 404 until the ALB rule lands").toBeDefined();
    expect(mcp?.destination).toBe("/developers/mcp");
    expect(mcp?.permanent).toBe(false);
  });
});
