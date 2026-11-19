import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";

// No session control. The Sign In / Dashboard / sign-out cluster that used to sit here called
// `useSession()`, which fetches `/v1/auth/session` on mount. That route is deleted with the account
// surface, so the control would resolve to unauthenticated after a failed request and could never
// show a signed-in state.
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-200 dark:border-neutral-800 bg-white/95 dark:bg-neutral-950/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 dark:supports-[backdrop-filter]:bg-neutral-950/80">
      <div className="container-page flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2 group" aria-label="Home">
            <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center text-white font-bold text-sm">
              IV
            </div>
            <span className="font-serif font-semibold text-lg text-neutral-900 dark:text-white">
              Intangible Valuation
            </span>
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/calculator" className="text-sm font-medium text-neutral-600 hover:text-primary-500 transition-colors">
            Calculator
          </Link>
          <Link href="/docs" className="text-sm font-medium text-neutral-600 hover:text-primary-500 transition-colors">
            Docs
          </Link>
          <Link href="/mcp" className="text-sm font-medium text-neutral-600 hover:text-primary-500 transition-colors">
            MCP
          </Link>
          <Link href="/skills" className="text-sm font-medium text-neutral-600 hover:text-primary-500 transition-colors">
            Skills
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link
            href="/calculator"
            className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-4 py-2 text-sm font-semibold hover:bg-primary-600 transition-colors"
          >
            Try Calculator
          </Link>
        </div>
      </div>
    </header>
  );
}
