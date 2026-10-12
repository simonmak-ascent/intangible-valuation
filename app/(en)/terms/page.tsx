import type { Metadata } from "next";
import { Breadcrumb } from "@/components/layout/Breadcrumb";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms of Service for the Intangible Valuation WebApp.",
};

export default function TermsPage() {
  return (
    <div className="container-narrow py-12">
      <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "Terms of Service" }]} />
      <h1 className="text-display-sm text-primary-500 mt-6 mb-6">Terms of Service</h1>
      <p className="text-sm text-neutral-400 mb-8">Last updated: 2026-08-13</p>

      <div className="prose prose-neutral dark:prose-invert max-w-none space-y-6 text-sm text-neutral-600 dark:text-neutral-400">
        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">1. Acceptance</h2>
          <p>
            By accessing or using the Intangible Valuation WebApp, you agree to these Terms of Service. If you do not
            agree, do not use the service.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">2. Service Description</h2>
          <p>
            The service provides valuation calculations for intangible assets, based on the methodologies published in
            the <em>Intangible Asset Valuation</em> textbook (Valuation in Practice Series, Ascent Partners). Results are
            provided for informational purposes only.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">3. Not Financial Advice</h2>
          <p>
            The service does not provide financial, investment, tax, legal, or accounting advice. Any valuation output is
            an estimate based on your inputs and published methodologies, and must be independently reviewed by a
            qualified professional before use in any decision.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">4. Subscriptions & Billing</h2>
          <p>
            Paid plans are billed monthly through Stripe. You may cancel at any time via the billing portal; cancellation
            takes effect at the end of the current billing period. All payments are processed by Stripe; we never store
            your card details.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">5. Acceptable Use</h2>
          <p>
            You may not reverse-engineer, scrape, resell, or redistribute the service or its benchmark data. You may not
            use the service to provide regulated financial advice without appropriate licensure.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">6. Data & Sources</h2>
          <p>
            All benchmark and methodology data is real and sourced from credible, cited sources (a full citation chain is
            provided with every data point). We make no warranty regarding the accuracy of third-party source data.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">7. Limitation of Liability</h2>
          <p>
            The service is provided &ldquo;as is&rdquo;. To the maximum extent permitted by law, we disclaim all
            warranties and shall not be liable for any indirect, incidental, or consequential damages arising from use of
            the service.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white">8. Contact</h2>
          <p>
            Questions about these terms: support@intangible-valuation.simonmak.com.
          </p>
        </section>
      </div>
    </div>
  );
}
