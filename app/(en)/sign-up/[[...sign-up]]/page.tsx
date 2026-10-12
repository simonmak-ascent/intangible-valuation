"use client";

import Link from "next/link";
import { signIn } from "next-auth/react";
import { useState } from "react";

const showGoogle = !!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
const showGitHub = !!process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
const showOAuth = showGoogle || showGitHub;

export default function SignUpPage() {
  const [loading, setLoading] = useState(false);

  const handleSignUp = async (provider: string) => {
    setLoading(true);
    await signIn(provider, { callbackUrl: "/calculator" });
  };

  return (
    <div className="container-narrow py-16">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-2">
          <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
            IV
          </div>
          <h1 className="text-display-sm text-neutral-900 dark:text-white mb-2">Create your account</h1>
          <p className="text-neutral-500">
            Start valuing intangible assets with textbook-verified methodology. Free forever.
          </p>
        </div>

        <div className="card p-6 mt-6 space-y-4">
          {showOAuth ? (
            <>
              {showGoogle && (
                <button
                  onClick={() => handleSignUp("google")}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-3 rounded-lg border border-neutral-300 dark:border-neutral-700 px-4 py-3 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors disabled:opacity-50"
                >
                  <GoogleIcon />
                  Sign up with Google
                </button>
              )}
              {showGitHub && (
                <button
                  onClick={() => handleSignUp("github")}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-3 rounded-lg border border-neutral-300 dark:border-neutral-700 px-4 py-3 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors disabled:opacity-50"
                >
                  <GitHubIcon />
                  Sign up with GitHub
                </button>
              )}
            </>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-neutral-500 mb-4">
                Sign in with the demo account to get started.
              </p>
              <Link
                href="/sign-in"
                className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
              >
                Go to Sign In
              </Link>
            </div>
          )}
        </div>

        <div className="mt-6 space-y-3">
          <div className="flex items-start gap-3 p-3 rounded-lg bg-neutral-50 dark:bg-neutral-900">
            <span className="text-primary-500 mt-0.5">&#10003;</span>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              <strong>Free tier:</strong> All 68 valuation methods, step-by-step proofs, MCP gateway
            </p>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-neutral-50 dark:bg-neutral-900">
            <span className="text-primary-500 mt-0.5">&#10003;</span>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              <strong>Textbook-verified:</strong> Every formula traceable to source material
            </p>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-neutral-50 dark:bg-neutral-900">
            <span className="text-primary-500 mt-0.5">&#10003;</span>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              <strong>Audit trail:</strong> Complete traceability for compliance
            </p>
          </div>
        </div>

        <p className="text-center text-sm text-neutral-400 mt-6">
          Already have an account?{" "}
          <Link href="/sign-in" className="text-primary-500 hover:text-primary-600 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}

function GitHubIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
    </svg>
  );
}
