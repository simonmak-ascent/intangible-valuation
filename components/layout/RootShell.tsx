import type { Metadata } from "next";
import { Open_Sans, Titillium_Web, Raleway, JetBrains_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import { AppShell } from "@/components/layout/AppShell";
import "@/app/globals.css";

const openSans = Open_Sans({ subsets: ["latin"], variable: "--font-open-sans", display: "swap" });
const titillium = Titillium_Web({ subsets: ["latin"], weight: ["400", "600", "700"], variable: "--font-titillium", display: "swap" });
const raleway = Raleway({ subsets: ["latin"], variable: "--font-raleway", display: "swap" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono", display: "swap" });

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
        <Analytics />
      </body>
    </html>
  );
}
