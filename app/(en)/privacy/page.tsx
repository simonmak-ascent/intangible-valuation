import type { Metadata } from "next";
import { Breadcrumb } from "@/components/layout/Breadcrumb";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy for the Intangible Valuation WebApp.",
};

export default function PrivacyPage() {
  return (
    <div className="container-narrow py-12">
      <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "Privacy Policy" }]} />
      <h1 className="text-display-sm text-primary-500 mt-6 mb-6">Privacy Policy</h1>
      <p className="text-sm text-neutral-400 mb-8">Last updated: 2026-08-13</p>

      <div className="space-y-6 text-sm text-neutral-600 dark:text-neutral-400">
        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">1. Data We Collect</h2>
          <p>
            We collect the minimum data required to provide the service: your email, name, valuation inputs and results
            (saved valuations), and subscription/billing status. Billing data is handled by Stripe; we do not store card
            numbers.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">2. How We Use Data</h2>
          <p>
            Data is used solely to operate the service: perform calculations, persist your saved valuations and audit
            trail, manage subscriptions, and diagnose errors. We do not sell personal data.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">3. Data Storage</h2>
          <p>
            Data is stored in SurrealDB and processed on Vercel infrastructure. Valuations are retained to support the
            audit trail. You may request deletion of your account and data at any time.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">4. Data Sources</h2>
          <p>
            Benchmark and methodology data is real, sourced from credible public and licensed sources, each carrying a
            full citation chain. We do not collect personal data from these sources.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">5. Cookies & Analytics</h2>
          <p>
            We use Vercel Analytics and Sentry for aggregate usage and error monitoring. These are privacy-conscious and
            do not track you across unrelated sites.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">6. Your Rights</h2>
          <p>
            You may access, correct, export, or delete your data. Contact support@intangible-valuation.simonmak.com to
            exercise these rights.
          </p>
        </section>
      </div>
    </div>
  );
}
