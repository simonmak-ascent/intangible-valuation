import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] container-page text-center">
      <div className="text-8xl font-bold text-primary-200 mb-4">404</div>
      <h2 className="text-2xl font-serif font-semibold text-neutral-900 dark:text-white mb-3">
        Page not found
      </h2>
      <p className="text-neutral-500 mb-6 max-w-md">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        href="/"
        className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
      >
        Back to Home
      </Link>
    </div>
  );
}
