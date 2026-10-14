import { NextResponse } from "next/server";
import { CATALOG } from "@/lib/valuation/catalog";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    endpoints: CATALOG,
    total_methods: CATALOG.length,
    categories: ["core", "approaches", "income_methods", "asset_types", "advanced"],
    docs_url: "https://intangible-valuation.ascent-partners.com",
  });
}
