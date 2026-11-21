import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { CATALOG, CATALOG_SLUGS, getCatalogMethod } from "@/lib/valuation/catalog";

describe("Valuation method catalog", () => {
  it("declares all 68 methods", () => {
    expect(CATALOG.length).toBe(68);
    expect(CATALOG_SLUGS.length).toBe(68);
  });

  it("has no duplicate slugs", () => {
    expect(new Set(CATALOG_SLUGS).size).toBe(CATALOG_SLUGS.length);
  });

  it("uses kebab-case slugs only", () => {
    for (const slug of CATALOG_SLUGS) {
      expect(slug).toMatch(/^[a-z0-9-]+$/);
      expect(slug).not.toContain("_");
    }
  });

  it("declares mcp as null, or a real tool with at least one method", () => {
    for (const method of CATALOG) {
      if (method.mcp === null) continue;
      expect(method.mcp.tool).toMatch(/^valuation_[a-z0-9_]+$/);
      expect(method.mcp.methods.length).toBeGreaterThan(0);
      for (const m of method.mcp.methods) expect(m).toMatch(/^[a-z0-9_]+$/);
    }
  });

  it("leaves no method without an MCP path", () => {
    // The 21 that used to have none were added to the tool surface on 2026-11-21, and
    // `tests/test_catalog_alignment.py` proves each of the 68 mappings against the dispatcher.
    const apiOnly = CATALOG.filter((m) => m.mcp === null).map((m) => m.slug);
    expect(apiOnly).toEqual([]);
  });

  it("declares a non-empty parameters schema for every method", () => {
    for (const method of CATALOG) {
      expect(method.parameters.length).toBeGreaterThan(0);
      for (const p of method.parameters) {
        expect(p.name).toMatch(/^[a-z0-9_]+$/);
        expect(p.type).toBeTruthy();
      }
    }
  });

  it("declares a pythonFunction and textbookReference for every method", () => {
    for (const method of CATALOG) {
      expect(method.pythonFunction).toMatch(/^intangible_valuation\.[a-z0-9_.]+$/);
      expect(method.textbookReference).toMatch(/^(Ch \d+|Appendix [A-Z])/);
    }
  });

  it("resolves every slug via getCatalogMethod", () => {
    for (const slug of CATALOG_SLUGS) {
      expect(getCatalogMethod(slug)).toBeDefined();
    }
  });
});

describe("Catalog source-of-truth parity", () => {
  const routeFile = readFileSync(
    join(process.cwd(), "app", "v1", "valuation", "route.ts"),
    "utf-8"
  );

  it("route.ts imports the shared catalog (no inline duplicate)", () => {
    expect(routeFile).toContain('import { CATALOG } from "@/lib/valuation/catalog"');
    expect(routeFile).not.toContain("slug: \"present-value\"");
  });
});
