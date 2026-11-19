import { describe, it, expect } from "vitest";
import { BENCHMARKS, filterBenchmarks } from "@/lib/valuation/benchmarks";
import { validateCitation } from "@/lib/valuation/citation";

/**
 * `data/benchmarks.json` is now the store, not a seed, so its integrity is a test rather than an
 * import-time rejection. Four properties matter and each is easy to lose:
 *
 *  1. every record carries a complete citation chain — a figure with no source is worse than no
 *     figure, which is why the old ETL refused uncited records;
 *  2. every value falls inside the domain its type claims, because `BENCHMARKS` is a cast over the
 *     JSON import and a cast cannot fail;
 *  3. the filter reproduces what the SQL `WHERE` clause did, including the `"all"` wildcard on
 *     `asset_type` and `industry`;
 *  4. an injection payload returns nothing, and an empty parameter filters nothing.
 *
 * Assertions here are written to fail on the bug they name, not merely to pass: the wildcard case
 * pins the exact row count an exact-match implementation would get wrong, and the sort case uses the
 * same comparator as the implementation rather than JavaScript's default `sort()`.
 */

describe("published benchmark records", () => {
  it("carries the four categories the product documents", () => {
    expect(BENCHMARKS).toHaveLength(13);
    const byCategory = new Map<string, number>();
    for (const record of BENCHMARKS) {
      byCategory.set(record.category, (byCategory.get(record.category) ?? 0) + 1);
    }
    expect(Object.fromEntries(byCategory)).toEqual({
      discount_rate: 3,
      growth_rate: 2,
      royalty_rate: 5,
      useful_life: 3,
    });
  });

  it("gives every record a complete citation chain", () => {
    for (const record of BENCHMARKS) {
      expect(validateCitation(record.citation), `${record.metric_name} (${record.category})`).toEqual([]);
    }
  });

  it("fails the validator when a citation field is missing — the check can fail", () => {
    // A validator never observed failing is unproven. This mutates a copy, not the module.
    const broken = { ...BENCHMARKS[0], citation: { ...BENCHMARKS[0].citation } } as {
      citation: Record<string, unknown>;
    };
    delete broken.citation.ref;
    const errors = validateCitation(broken.citation as never);
    expect(errors.map((error) => error.field)).toContain("ref");
  });

  it("keeps every value inside the domain its type claims", () => {
    // The import is a cast, so nothing else would catch a record whose category or stage is a value
    // the type forbids. `business_stage` legitimately includes "all"; the type says so.
    const categories = new Set(["royalty_rate", "discount_rate", "useful_life", "growth_rate"]);
    const stages = new Set(["startup", "growth", "mature", "all"]);
    for (const record of BENCHMARKS) {
      expect(categories.has(record.category), `${record.metric_name}: category ${record.category}`).toBe(true);
      expect(stages.has(record.business_stage), `${record.metric_name}: stage ${record.business_stage}`).toBe(true);
      expect(Number.isFinite(record.value), record.metric_name).toBe(true);
      expect(record.unit?.trim(), record.metric_name).toBeTruthy();
    }
  });
});

describe("filterBenchmarks", () => {
  it("returns everything when nothing is asked for", () => {
    expect(filterBenchmarks()).toHaveLength(BENCHMARKS.length);
  });

  it("treats an empty parameter as no filter", () => {
    // `?category=` is what a client's "All" option sends. The old route did `|| undefined`.
    expect(filterBenchmarks({ category: "" })).toHaveLength(BENCHMARKS.length);
    expect(filterBenchmarks({ asset_type: "", industry: "" })).toHaveLength(BENCHMARKS.length);
  });

  it("filters category exactly", () => {
    const rows = filterBenchmarks({ category: "royalty_rate" });
    expect(rows).toHaveLength(5);
    expect(rows.every((row) => row.category === "royalty_rate")).toBe(true);
  });

  it("filters business_stage exactly", () => {
    const rows = filterBenchmarks({ business_stage: "startup" });
    expect(rows).toHaveLength(4);
    expect(rows.every((row) => row.business_stage === "startup")).toBe(true);
  });

  it("treats asset_type as value-or-all", () => {
    // 5 records are "patent" and 5 are "all". Exact matching would return 5, so 10 is the number
    // that fails on that bug; `toBeGreaterThanOrEqual(5)` would pass either way.
    const rows = filterBenchmarks({ asset_type: "patent" });
    expect(rows).toHaveLength(10);
    expect(rows.every((row) => row.asset_type === "patent" || row.asset_type === "all")).toBe(true);
  });

  it("treats industry as value-or-all", () => {
    // 12 records are industry "all" and exactly one is "technology": exact matching would return 1.
    expect(filterBenchmarks({ industry: "technology" })).toHaveLength(BENCHMARKS.length);
  });

  it("returns nothing for a payload that used to be an injection", () => {
    // The old route interpolated these straight into SurrealQL with a root client.
    // `category` has no "all" values, so a value that matches no record returns nothing.
    expect(filterBenchmarks({ category: '" OR 1=1 --' })).toEqual([]);
    expect(filterBenchmarks({ asset_type: '" OR 1=1 --' })).toHaveLength(5); // only the "all" rows
  });

  it("cannot be widened by a payload — only the wildcard rows match a value no record carries", () => {
    // `industry` is 12 "all" + 1 "technology". A record marked "all" applies to every industry, so a
    // garbage value legitimately matches those 12 — the same set an unknown real industry matches.
    // What must never happen is a row outside that set appearing, which is what the old query did.
    const payload = filterBenchmarks({ industry: 'all" OR 1=1 --' });
    expect(payload).toHaveLength(12);
    expect(payload.every((row) => row.industry === "all")).toBe(true);
    expect(payload).toEqual(filterBenchmarks({ industry: "petroleum" }));
  });

  it("sorts by category, business_stage, asset_type, field by field", () => {
    // Code-unit order, matching `compare()` in benchmarks.ts. The fields are compared separately
    // rather than as one joined string: "a" versus "a b" orders one way as a tuple and the other way
    // as "a|…" versus "a b|…", because ' ' is 32 and '|' is 124. Comparing the joined keys would
    // agree on today's values by luck, which is the sort of oracle that drifts silently.
    const cmp = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);
    const key = (row: { category: string; business_stage: string; asset_type: string }) =>
      `${row.category}/${row.business_stage}/${row.asset_type}`;
    const rows = filterBenchmarks();
    const sorted = [...rows].sort(
      (a, b) =>
        cmp(a.category, b.category) || cmp(a.business_stage, b.business_stage) || cmp(a.asset_type, b.asset_type)
    );
    expect(rows.map(key)).toEqual(sorted.map(key));
  });

  it("does not mutate the module-level records", () => {
    const before = BENCHMARKS.map((record) => record.metric_name);
    filterBenchmarks({ category: "royalty_rate" });
    expect(BENCHMARKS.map((record) => record.metric_name)).toEqual(before);
  });
});
