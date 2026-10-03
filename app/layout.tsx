import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import { AppShell } from "@/components/layout/AppShell";
import "@/app/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono", display: "swap" });

export const metadata: Metadata = {
  title: {
    default: "Intangible Asset Valuation — The Authority",
    template: "%s | Intangible Valuation",
  },
  description:
    "The most authoritative, traceable, and auditable source of intangible asset valuation. 68 methods, 1,000+ textbook-verified tests, MCP gateway, and AI-agent ready.",
  keywords: [
    "intangible asset valuation",
    "patent valuation",
    "brand valuation",
    "goodwill calculation",
    "purchase price allocation",
    "relief from royalty",
    "MPEEM",
    "discount rate",
    "WACC",
    "CAPM",
    "MCP server",
    "AI valuation",
  ],
  authors: [{ name: "Ascent Partners" }],
  openGraph: {
    title: "Intangible Asset Valuation — The Authority",
    description: "The most authoritative, traceable, and auditable source of intangible asset valuation.",
    type: "website",
    siteName: "Intangible Valuation",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen flex flex-col">
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var t=localStorage.getItem('theme');var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;if(d)document.documentElement.classList.add('dark');}catch(e){}",
          }}
        />
        <AppShell>{children}</AppShell>
        <Analytics />
      </body>
    </html>
  );
}
