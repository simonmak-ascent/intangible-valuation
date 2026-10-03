"use client";

import Link from "next/link";
import { useSession, signIn, signOut } from "next-auth/react";
import { LogIn, LogOut, User } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  const { data: session, status } = useSession();
  const isAuthenticated = status === "authenticated";

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
          {status === "loading" ? (
            <div className="w-8 h-8 rounded-full bg-neutral-200 dark:bg-neutral-700 animate-pulse" />
          ) : isAuthenticated ? (
            <>
              <Link
                href="/dashboard"
                className="hidden md:inline-flex text-sm font-medium text-neutral-600 hover:text-primary-500 transition-colors"
              >
                Dashboard
              </Link>
              <button
                onClick={() => signOut({ callbackUrl: "/" })}
                className="hidden md:inline-flex items-center gap-1.5 text-sm font-medium text-neutral-500 hover:text-red-500 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-neutral-100 dark:bg-neutral-800">
                <User className="w-4 h-4 text-primary-500" />
                <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                  {session?.user?.name || session?.user?.email}
                </span>
              </div>
            </>
          ) : (
            <button
              onClick={() => signIn(undefined, { callbackUrl: "/calculator" })}
              className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-300 dark:border-neutral-700 px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
            >
              <LogIn className="w-4 h-4" />
              Sign In
            </button>
          )}
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
