"use client";

import { useState } from "react";
import { Check } from "lucide-react";
import { trackEvent } from "@/lib/analytics";

const TIERS = [
  {
    id: "plans:free",
    name: "Free",
    price: "$0",
    description: "For trying the platform",
    features: ["All 68 valuation methods", "Step-by-step proofs", "5 saved valuations"],
    cta: "Current plan",
    highlight: false,
  },
  {
    id: "plans:pro",
    name: "Pro",
    price: "$29/mo",
    description: "For practitioners and auditors",
    features: ["Everything in Free", "Unlimited saved valuations", "Audit trail", "PDF export", "Benchmark data"],
    cta: "Subscribe",
    highlight: true,
  },
  {
    id: "plans:enterprise",
    name: "Enterprise",
    price: "Custom",
    description: "For firms and multi-user teams",
    features: ["Everything in Pro", "SSO & team roles", "Priority support"],
    cta: "Contact sales",
    highlight: false,
  },
];

export default function PricingPage() {
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async (planId: string) => {
    setLoading(true);
    trackEvent("checkout_started", { plan_id: planId });
    try {
      const res = await fetch("/v1/billing/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan_id: planId }),
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-page py-12">
      <div className="max-w-2xl mx-auto text-center mb-12">
        <h1 className="text-display-sm text-primary-500 mb-4">Pricing</h1>
        <p className="text-neutral-500">
          Start free. Upgrade when you need the audit trail, PDF export, and benchmark data.
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
            <button
              onClick={() => handleSubscribe(tier.id)}
              disabled={loading || tier.id === "plans:free" || tier.id === "plans:enterprise"}
              className={`w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors ${
                tier.highlight
                  ? "bg-primary-500 text-white hover:bg-primary-600"
                  : "border border-neutral-300 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {loading ? "Redirecting…" : tier.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
