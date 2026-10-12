import type { Metadata } from "next";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { MethodCalculator } from "./MethodCalculator";
import { CATALOG_SLUGS, getCatalogMethod } from "@/lib/valuation/catalog";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://intangible-valuation.simonmak.com";

export function generateStaticParams() {
  return CATALOG_SLUGS.map((method) => ({ method }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ method: string }>;
}): Promise<Metadata> {
  const { method } = await params;
  const m = getCatalogMethod(method);
  return {
    title: m ? `${m.name} — Intangible Valuation` : "Valuation Calculator",
    description: m?.description ?? "Intangible asset valuation method.",
    alternates: { canonical: `${BASE_URL}/calculator/${method}` },
  };
}

export default async function MethodCalculatorPage({ params }: { params: Promise<{ method: string }> }) {
  const { method } = await params;
  const m = getCatalogMethod(method);

  return (
    <div>
      {m && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: `${m.name} — Intangible Valuation`,
              description: m.description,
              applicationCategory: "FinanceApplication",
              operatingSystem: "Any",
              url: `${BASE_URL}/calculator/${m.slug}`,
            }),
          }}
        />
      )}
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Calculator", href: "/calculator" },
          { label: method.replace(/-/g, " ") },
        ]}
      />
      <div className="container-narrow py-8">
        <MethodCalculator slug={method} />
      </div>
    </div>
  );
}
