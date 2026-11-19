import Link from "next/link";
import { Check } from "lucide-react";

// Static copy. This page used to be a client component whose Subscribe button POSTed to
// `/v1/billing/checkout`, took the Stripe Checkout URL the route returned and sent the browser there,
// with `/dashboard?checkout=success` as the return address — three things that no longer exist. Auth
// and billing left the design on 2026-11-18 and were deleted
// on 2026-11-19, so the prices below describe what is planned, not something
// that can be bought. Only the free tier is actionable — it links to the calculator, which is free
// and needs no account; Pro and Enterprise render a disabled label.
const TIERS = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    description: "The calculator, with no account",
    features: ["All 68 valuation methods", "Step-by-step proofs", "Every step of the working is shown"],
    cta: "Open the calculator",
    href: "/calculator",
    highlight: false,
  },
  {
    id: "pro",
    name: "Pro",
    price: "$29/mo",
    description: "For practitioners and auditors",
    features: ["Everything in Free", "Saved valuations", "Audit trail", "PDF export", "Benchmark data"],
    cta: "Not yet available",
    href: null,
    highlight: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Custom",
    description: "For firms and multi-user teams",
    features: ["Everything in Pro", "SSO & team roles", "Priority support"],
    cta: "Not yet available",
    href: null,
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <div className="container-page py-12">
      <div className="max-w-2xl mx-auto text-center mb-12">
        <h1 className="text-display-sm text-primary-500 mb-4">Pricing</h1>
        <p className="text-neutral-500">
          The calculator is free and needs no account. Team plans are not available yet.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {TIERS.map((tier) => (
          <div
            key={tier.id}
            className={`card p-6 flex flex-col ${tier.highlight ? "border-primary-400 ring-2 ring-primary-500/20" : ""}`}
          >
            <h2 className="font-serif font-semibold text-lg text-neutral-900 dark:text-white">{tier.name}</h2>
            <p className="text-2xl font-bold font-mono text-primary-600 dark:text-primary-400 my-2">{tier.price}</p>
            <p className="text-sm text-neutral-500 mb-4">{tier.description}</p>
            <ul className="space-y-2 mb-6 flex-1">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                  <Check className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            {tier.href ? (
              <Link
                href={tier.href}
                className="w-full text-center rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors bg-primary-500 text-white hover:bg-primary-600"
              >
                {tier.cta}
              </Link>
            ) : (
              <span
                aria-disabled="true"
                className="w-full text-center rounded-lg px-4 py-2.5 text-sm font-semibold border border-neutral-300 dark:border-neutral-700 text-neutral-600 dark:text-neutral-400 cursor-not-allowed"
              >
                {tier.cta}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
