import records from "@/data/benchmarks.json";
import { hasValidCitation } from "./citation";
import type { BenchmarkFilter, BenchmarkRecord } from "./types";

/**
 * The published benchmark records, read from the committed file rather than a database.
 *
 * There was a SurrealDB behind this until 2026-11-19, and the endpoint answered 503 for every client
 * because the web container carried no `SURREALDB_*` env and the pinned client refused the engine's
 * version. The data is 13 cited records; a database was doing nothing a file cannot do, and it made
 * the route injectable — its query was built by interpolating four request parameters.
 *
 * The import is static so the records are bundled into the build: `Dockerfile.web` copies only
 * `.next/standalone`, `.next/static` and `public` into the run stage, so a `readFileSync` on
 * `data/` would fail there. `.dockerignore` un-ignores exactly this one file for the same reason.
 *
 * The cast is the one place the file's shape meets the type. `tests-webapp/unit/benchmarks.test.ts`
 * asserts the value domains (category, business_stage, asset_type and industry all fall inside the
 * sets the type and the product describe), and `assertCited()` below refuses to load an uncited
 * record — because the test is not the only witness. `docker build` runs `pnpm build` with no test
 * step, so an image can be built from a commit the suite never saw.
 */
export const BENCHMARKS: readonly BenchmarkRecord[] = records as readonly BenchmarkRecord[];

/**
 * Refuse to serve a figure with no source.
 *
 * `validateCitation` used to run at import time in the ETL that wrote the database; with the database
 * gone, this is where that check belongs, because the data file is now the store. A module that
 * throws here fails the build and fails the route, which is the correct direction: an endpoint that
 * cannot state where a number came from should not answer.
 *
 * Measured rather than assumed: blanking `citation.ref` on three records makes `pnpm build` exit 1
 * with "benchmark records without a complete citation chain: median_wacc (discount_rate), …", so
 * `next build` does evaluate this module. The records were restored immediately afterwards.
 */
function assertCited(source: readonly BenchmarkRecord[]): void {
  const uncited = source.filter((record) => !hasValidCitation(record.citation));
  if (uncited.length > 0) {
    const names = uncited.map((record) => `${record.metric_name} (${record.category})`).join(", ");
    throw new Error(`benchmark records without a complete citation chain: ${names}`);
  }
}

assertCited(BENCHMARKS);

/** Code-unit comparison, deliberately not `localeCompare`: the order is part of the API's behaviour. */
function compare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/**
 * Filter the records the way the SQL used to, without SQL.
 *
 * Semantics preserved from the old `WHERE` clause: `category` and `business_stage` match exactly,
 * while `asset_type` and `industry` match the requested value **or** `"all"` — a record marked
 * `"all"` applies to every value of that field. An absent or empty parameter filters nothing.
 */
export function filterBenchmarks(filter: BenchmarkFilter = {}): BenchmarkRecord[] {
  const matchesEitherAllOr = (requested: string | undefined, actual: string): boolean =>
    !requested || actual === requested || actual === "all";

  return BENCHMARKS.filter(
    (record) =>
      (!filter.category || record.category === filter.category) &&
      (!filter.business_stage || record.business_stage === filter.business_stage) &&
      matchesEitherAllOr(filter.asset_type, record.asset_type) &&
      matchesEitherAllOr(filter.industry, record.industry)
  ).sort(
    (a, b) =>
      compare(a.category, b.category) ||
      compare(a.business_stage, b.business_stage) ||
      compare(a.asset_type, b.asset_type)
  );
}
