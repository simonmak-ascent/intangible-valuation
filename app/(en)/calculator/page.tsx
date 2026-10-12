import type { Metadata } from "next";
import { MethodBrowser } from "./MethodBrowser";
import type { MethodCategory } from "@/lib/valuation/types";

export const metadata: Metadata = {
  title: "Valuation Calculator",
  description: "Interactive calculators for 68 textbook-verified intangible asset valuation methods.",
};

export default async function CalculatorPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string }>;
}) {
  const { category } = await searchParams;
  const initialCategory: MethodCategory | "all" =
    category === "core" || category === "approaches" || category === "income_methods" || category === "asset_types" || category === "advanced"
      ? category
      : "all";

  return <MethodBrowser initialCategory={initialCategory} />;
}
