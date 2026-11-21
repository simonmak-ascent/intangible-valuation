import { NextResponse } from "next/server";
import { getRiskFreeRate, MarketDataUnavailableError } from "@/lib/market/treasury";

/**
 * The 10-year Treasury yield, as a decimal fraction, read from Yahoo Finance.
 *
 * `force-dynamic` is deliberate: the route must not be prerendered during `next build`. A build that
 * fetched this would put a third-party network call on the image build path — the shape of failure
 * that made `next build` hang on Google Fonts until the families were vendored (#67) — and it would
 * bake a rate into the image that is stale by the time it serves. Rates are read per request and
 * cached in-process for an hour by `getRiskFreeRate`.
 *
 * A 503 with a reason is the failure mode, never a plausible-looking number: the caller can fall back
 * to its own assumption, but it has to choose to.
 */
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const rate = await getRiskFreeRate();
    return NextResponse.json(rate, {
      headers: {
        // An hour, matching the in-process TTL, plus five minutes of stale-while-revalidate rather
        // than a day: the honest bound is then about two hours — one in process, one in a shared
        // cache, plus the revalidation window — and `asOf` in the body says how old the figure really
        // is. Yahoo refuses script-identifying clients with 429, so a shared cache is what keeps
        // repeat callers from turning into outbound requests.
        "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=300",
      },
    });
  } catch (error) {
    // Sentry is wired for this app (`instrumentation.ts`, `sentry.server.config.ts`), but
    // `onRequestError` never fires for a route that catches its own errors — so an internal fault
    // here becomes a 503 whose detail is deliberately generic, with nothing reported server-side.
    // That is the cost of having no logger in this tree; it is recorded rather than left to be
    // discovered, and it matters only if a caller depends on this route.
    const detail = error instanceof MarketDataUnavailableError ? error.message : "unexpected failure";
    return NextResponse.json({ error: "market data unavailable", detail }, { status: 503 });
  }
}
