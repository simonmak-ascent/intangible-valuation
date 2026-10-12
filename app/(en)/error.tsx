"use client";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] container-page text-center">
      <h2 className="text-2xl font-serif font-semibold text-neutral-900 dark:text-white mb-3">
        Something went wrong
      </h2>
      <p className="text-neutral-500 mb-6 max-w-md">
        {error.message || "An unexpected error occurred."}
      </p>
      <button
        onClick={reset}
        className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
      >
        Try again
      </button>
    </div>
  );
}
