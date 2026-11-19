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
      <p className="text-sm text-neutral-400 mb-8">Last updated: 2026-11-19</p>

      <div className="space-y-6 text-sm text-neutral-600 dark:text-neutral-400">
        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">1. Data We Collect</h2>
          <p>
            There is no account and nothing to sign up for, so we do not collect a name, an email address or a user
            profile. A calculation sends the figures you type to our valuation API, which returns a result and keeps no
            record of it. We do not set cookies. Your light/dark preference is stored in your own browser and is never
            transmitted.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">2. How We Use Data</h2>
          <p>
            Your inputs are used for one purpose: to perform the calculation you asked for. They are not stored, profiled
            or sold, and they are not sent to any third party. The one exception is a server-side error: a failed
            calculation is logged by the valuation service with the exception detail, and the value that failed
            validation can appear in that message. Those logs stay on our infrastructure.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">3. Data Storage</h2>
          <p>
            The service runs on Ascent Partners Group infrastructure, not on Vercel. Its database holds published
            benchmark reference data, which contains no personal information. The tables that belonged to the previous
            version of this service — user accounts, saved results, an audit trail — are no longer read or written by
            anything here, and removing them from any deployment that still holds them is a one-off step in that
            deployment rather than something the service does at runtime.
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
            We do not set cookies, we do not record sessions and we run no analytics. Error reporting is active only if
            a reporting key is configured: in that case a page error is sent to Sentry with the request body removed,
            and 10% of page loads are sampled for timing. This deployment does not configure one.
          </p>
        </section>

        <section>
          <h2 className="font-serif text-lg font-semibold text-neutral-900 dark:text-white mb-2">6. Your Rights</h2>
          <p>
            There is no account and no profile to access, correct, export or delete. If you believe an older version of
            this service recorded something about you, write to support@intangible-valuation.ascent-partners.com and it
            will be removed.
          </p>
        </section>
      </div>
    </div>
  );
}
