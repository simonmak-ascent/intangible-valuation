import { describe, it, expect } from "vitest";
import nextConfig from "../../next.config";

/**
 * The library reference is MkDocs output copied into `public/docs` by the image's docs stage
 * (Dockerfile.web). MkDocs emits **relative** asset and nav URLs, so the page must be served from a
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
