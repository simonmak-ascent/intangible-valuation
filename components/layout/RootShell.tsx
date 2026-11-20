import type { Metadata } from "next";
import localFont from "next/font/local";
import { AppShell } from "@/components/layout/AppShell";
import "@/app/globals.css";

/**
 * Fonts are vendored, not fetched. These four families used to come from `next/font/google`, which
 * downloads them during `next build` — so the build opened TLS to Google and, on 2026-11-18, a
 * Quality Gate job sat 31 minutes at 0% CPU holding four ESTABLISHED sockets to a Google edge before
 * anyone noticed. A build must not depend on a third party being reachable, and the seven woff2 files
 * here are the latin subset of the same families at the same weights, so rendering is unchanged.
 *
 * The variable families carry their axis range in `weight`; Titillium Web is static and ships the
 * four weights the stylesheet asks for — 400, 600, 700, and 900 for `font-black` in the landing hero.
 */
const openSans = localFont({
  src: "../../app/fonts/open-sans-300-800.woff2",
  weight: "300 800",
  style: "normal",
  variable: "--font-open-sans",
  display: "swap",
});
const titillium = localFont({
  src: [
    { path: "../../app/fonts/titillium-web-400.woff2", weight: "400", style: "normal" },
    { path: "../../app/fonts/titillium-web-600.woff2", weight: "600", style: "normal" },
    { path: "../../app/fonts/titillium-web-700.woff2", weight: "700", style: "normal" },
    // The landing hero uses `font-black`, and `globals.css` forces `font-serif` on h1–h4, so 900 is
    // asked for. Without this the browser synthesises it from 700 — the reason to check the weights
    // the stylesheet uses rather than the weights a family happens to ship.
    { path: "../../app/fonts/titillium-web-900.woff2", weight: "900", style: "normal" },
  ],
  variable: "--font-titillium",
  display: "swap",
});
const raleway = localFont({
  src: "../../app/fonts/raleway-100-900.woff2",
  weight: "100 900",
  style: "normal",
  variable: "--font-raleway",
  display: "swap",
});
const jetbrainsMono = localFont({
  src: "../../app/fonts/jetbrains-mono-100-800.woff2",
  weight: "100 800",
  style: "normal",
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: { default: "Intangible Asset Valuation — The Authority", template: "%s | Intangible Valuation" },
  description:
    "The most authoritative, traceable, and auditable source of intangible asset valuation. 68 methods, 1,000+ textbook-verified tests, MCP gateway, and AI-agent ready.",
  keywords: ["intangible asset valuation", "patent valuation", "brand valuation", "goodwill calculation", "purchase price allocation", "relief from royalty", "MPEEM", "discount rate", "WACC", "CAPM", "MCP server", "AI valuation"],
  authors: [{ name: "Ascent Partners" }],
  openGraph: {
    title: "Intangible Asset Valuation — The Authority",
    description: "The most authoritative, traceable, and auditable source of intangible asset valuation.",
    type: "website",
    siteName: "Intangible Valuation",
  },
  robots: { index: true, follow: true },
  alternates: {
    canonical: "https://intangible-valuation.ascent-partners.com",
    languages: {
      "en-GB": "https://intangible-valuation.ascent-partners.com",
      "zh-Hans": "https://intangible-valuation.ascent-partners.com/zh",
      "zh-Hant-HK": "https://intangible-valuation.ascent-partners.com/hk",
      "x-default": "https://intangible-valuation.ascent-partners.com",
    },
  },
};

// Blocking theme init — dark default, persisted choice (APG parity, no FOUC).
const THEME_INIT =
  "try{var v=localStorage.getItem('apg-theme');document.documentElement.setAttribute('data-theme',v==='light'||v==='dark'?v:'dark');}catch(e){document.documentElement.setAttribute('data-theme','dark');}";

export function RootShell({ lang, children }: { lang: string; children: React.ReactNode }) {
  return (
    <html lang={lang} data-theme="dark" suppressHydrationWarning className={`${openSans.variable} ${titillium.variable} ${raleway.variable} ${jetbrainsMono.variable}`}>
      <body className="flex min-h-screen flex-col">
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
