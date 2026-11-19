import { NextRequest, NextResponse } from "next/server";
import { filterBenchmarks } from "@/lib/valuation/benchmarks";

/**
 * The published benchmark records.
 *
 * This used to query SurrealDB, and the query was built by interpolating four request parameters into
 * SurrealQL with a client that connects as root. It was unreachable only because the web container
 * carried no `SURREALDB_*`; the route is now a filter over a committed, citation-validated file, so
 * there is no query to inject into and nothing to be unavailable.
 *
 * A parameter is passed through as a plain string and compared, never concatenated, so the payload
 * that used to be interesting — `?category=" OR 1=1 --` — simply matches no record.
 */
export function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const benchmarks = filterBenchmarks({
    // `||`, not `??`: an empty string is what a client-side "All" option sends, and the parameter has
    // always meant "do not filter on this field" when it is empty. `??` would let `""` through and
    // filter every record out.
    category: searchParams.get("category") || undefined,
    business_stage: searchParams.get("business_stage") || undefined,
    asset_type: searchParams.get("asset_type") || undefined,
    industry: searchParams.get("industry") || undefined,
  });

  return NextResponse.json({ benchmarks, count: benchmarks.length });
}
