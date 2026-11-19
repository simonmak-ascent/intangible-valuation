import { NextRequest, NextResponse } from "next/server";
import { getSurrealClient } from "@/lib/surreal/client";
import type { BusinessStage } from "@/lib/valuation/types";
import type { Benchmark } from "@/lib/valuation/types";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get("category") || undefined;
  const businessStage = searchParams.get("business_stage") as BusinessStage | undefined;
  const assetType = searchParams.get("asset_type") || undefined;
  const industry = searchParams.get("industry") || undefined;

  try {
    const db = await getSurrealClient();
    const conditions: string[] = [];
    if (category) conditions.push(`category = "${category}"`);
    if (businessStage) conditions.push(`business_stage = "${businessStage}"`);
    if (assetType) conditions.push(`(asset_type = "${assetType}" OR asset_type = "all")`);
    if (industry) conditions.push(`(industry = "${industry}" OR industry = "all")`);

    const whereClause = conditions.length > 0 ? ` WHERE ${conditions.join(" AND ")}` : "";
    const [benchmarks] = await db.query<[Benchmark[]]>(
      `SELECT * FROM benchmarks${whereClause} ORDER BY category, business_stage, asset_type`
    );

    return NextResponse.json({
      benchmarks: benchmarks ?? [],
      count: benchmarks?.length ?? 0,
    });
  } catch {
    // DB unavailable. There is no honest fallback: the values used to be served under invented
    // sources ("Damodaran 2025 (fallback)"), which is a citation that exists in no file. An empty
    // list is the truthful answer until the data is reachable.
    // An empty 200 is indistinguishable from "the table is empty", and a cache will persist it.
    return NextResponse.json(
      { error: "BENCHMARKS_UNAVAILABLE", message: "Benchmark store is unreachable" },
      { status: 503 }
    );
  }
}
