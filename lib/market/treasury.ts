import { z } from "zod";

/**
 * The risk-free rate, read from Yahoo Finance through the `yahoo-finance2` package.
 *
 * The Python library does no network I/O (`src/intangible_valuation/utils/constants.py` says so in
 * its docstring), so this module is where the estate's one live market read lives. It is the
 * reference for how to read the index: the package handles the endpoint and the `User-Agent` Yahoo
 * requires, and this file handles the things that bite a caller.
 *
 * 1. **The value is a percent.** Yahoo quotes `^TNX` as 4.912, meaning 4.912%, so the `rate` that
 *    leaves here is divided by 100 — `percent` deliberately is not. Measured 2026-11-20: `^TNX` 4.912
 *    against a 4.00% library default, a 0.912pp gap carried through CAPM as 11.20% versus 12.11%.
 * 2. **A quote belongs to a session, not to now.** `regularMarketTime` is the session the price was
 *    struck in — a Friday close read on a Sunday is still Friday's, and on a public holiday it can be
 *    older than the previous business day. It is returned as `asOf` rather than dropped, so a caller
 *    can say how old the number is instead of implying it is today's.
 * 3. **The numbers are bounded per tenor, and the bound is a trade-off.** A vendor that started
 *    sending `0.04912` instead of `4.912` would otherwise yield `0.000491` — a plausible-looking
 *    rate, which is exactly what this file must never produce. The floor therefore sits above that
 *    fraction and below each note's own low: `^FVX` closed at 0.195% in August 2020, `^TNX` at
 *    0.499% in March 2020, `^TYX` at 0.937% — so on those three tenors a fraction is refused loudly
 *    (503) while real data is served. (A first draft used 0.5 and would have refused that whole
 *    `^FVX` month.) The 13-week bill is the exception: `^IRX` printed negative in March 2020 and sat
 *    near zero for years, so its 0.001% floor cannot sit above 0.04912 — a ÷100 error on that one
 *    tenor is served as `0.000491` (the four-decimal percent, 0.0491, then ÷100), which no bound can
 *    tell from a genuine bill yield. That floor refuses the negative prints itself, and the library
 *    refuses a negative Rf as well (`core/discount_rates.py`, `capm_discount_rate`).
 */

/** The Treasury tenors Yahoo quotes, each a percentage. */
export const TREASURY_SYMBOLS = {
  thirteenWeek: "^IRX",
  fiveYear: "^FVX",
  tenYear: "^TNX",
  thirtyYear: "^TYX",
} as const;

/**
 * The one method this module needs from the client.
 *
 * Narrow on purpose: tests pass a fake, so no unit test reaches the network, and swapping the vendor
 * means satisfying one method rather than this package's whole surface.
 */
export interface QuoteClient {
  quote(symbol: string): Promise<unknown>;
}

export interface RiskFreeRate {
  /** Decimal fraction: `0.04912` for the 4.912% the index quotes. */
  rate: number;
  /** The index's own value, in percent, to four decimals — the payload's own precision. */
  percent: number;
  /** The session the quote belongs to, ISO 8601. */
  asOf: string;
  symbol: string;
}

/** Raised for any failure to produce a rate — transport, or a payload that does not fit the shape. */
export class MarketDataUnavailableError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "MarketDataUnavailableError";
  }
}

/**
 * The fields relied on, validated rather than assumed.
 *
 * The response crosses a network boundary into an untyped JSON parse. `z.number()` in Zod 4 already
 * rejects `NaN`, `Infinity` and a string, so a `null` or `"4.912"` cannot become a plausible-looking
 * rate; the bounds below reject the other way a rate goes wrong — the wrong magnitude. (An earlier
 * `.refine(Number.isFinite)` here was dead: removing it changed no test, which is how a guard that
 * cannot fail announces itself.)
 *
 * `regularMarketTime` is checked to be a `Date`: the package converts it today, and a future major
 * handing back epoch seconds would be refused here. Had the schema taken any value, the consequence
 * would be an `asOf` in 1970 — a wrong date on a correct rate, not a wrong rate.
 */
const QuoteSchema = z.object({
  symbol: z.string().min(1),
  // Only "a number" here: the magnitude check needs the symbol, so it runs after the identity check.
  regularMarketPrice: z.number(),
  regularMarketTime: z.date(),
});

/**
 * Floors by tenor, in percent.
 *
 * The three note floors are above 0.04912 — the ÷100 fraction of a 4.912% quote, which would
 * otherwise serve `0.000491` — and below the tenor's measured low (0.195 / 0.499 / 0.937), so
 * correct vendor data is never refused and the unit error is.
 *
 * The bill cannot have that guard: `^IRX` went negative in March 2020 and sat near zero for years
 * before it, so a floor above 0.04912 would refuse real data. `0.04912` for `^IRX` is therefore
 * accepted and served as `0.000491` — the one tenor where the ÷100 error is indistinguishable from
 * a genuine yield.
 */
const MIN_PERCENT_BY_SYMBOL: Record<string, number> = {
  [TREASURY_SYMBOLS.thirteenWeek]: 0.001,
  [TREASURY_SYMBOLS.fiveYear]: 0.1,
  [TREASURY_SYMBOLS.tenYear]: 0.1,
  [TREASURY_SYMBOLS.thirtyYear]: 0.1,
};

/**
 * A tenor this module has no magnitude knowledge of: refuse zero, negatives and a magnitude over the
 * ceiling. It cannot refuse the ÷100 error, because `0.04912` sits inside a bill's genuine range.
 */
const GENERIC_MIN_PERCENT = 0.001;

/** No Treasury tenor has been near this; above it is an arithmetic or unit error, not a market move. */
const MAX_PERCENT = 25;

/**
 * Read the rate for one symbol, with no caching and no client construction.
 *
 * `client` is a parameter rather than module state so this is testable without a network call and
 * without resetting anything between tests.
 */
export async function fetchRiskFreeRate(
  client: QuoteClient,
  symbol: string = TREASURY_SYMBOLS.tenYear,
): Promise<RiskFreeRate> {
  let raw: unknown;
  try {
    raw = await client.quote(symbol);
  } catch (error) {
    // The cause is kept: `cause` holds the vendor's own error, which is what a log needs to
    // distinguish a 429 from a DNS failure without this message guessing at either.
    throw new MarketDataUnavailableError(`Yahoo Finance quote failed for ${symbol}`, { cause: error });
  }

  const parsed = QuoteSchema.safeParse(raw);
  if (!parsed.success) {
    throw new MarketDataUnavailableError(
      `Yahoo Finance returned an unusable quote for ${symbol}: ${parsed.error.issues
        .map((issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`)
        .join("; ")}`,
    );
  }

  // Asking for one instrument and serving another would be a silent wrong answer, not a failure.
  if (parsed.data.symbol !== symbol) {
    throw new MarketDataUnavailableError(
      `Yahoo Finance answered for ${parsed.data.symbol} when ${symbol} was requested`,
    );
  }

  // Magnitude, now that the symbol is known: a fraction where a percent belongs is the one wrong
  // answer that would still look right.
  const floor = MIN_PERCENT_BY_SYMBOL[symbol] ?? GENERIC_MIN_PERCENT;
  if (parsed.data.regularMarketPrice < floor || parsed.data.regularMarketPrice > MAX_PERCENT) {
    throw new MarketDataUnavailableError(
      `Yahoo Finance quoted ${parsed.data.regularMarketPrice} for ${symbol}, outside the ` +
        `${floor}-${MAX_PERCENT}% range a Treasury yield can take`,
    );
  }

  // Four decimals of a percent (the payload's own precision), then the fraction the library takes.
  const percent = Math.round(parsed.data.regularMarketPrice * 1e4) / 1e4;
  const rate = Math.round((percent / 100) * 1e6) / 1e6;

  return {
    rate,
    percent,
    asOf: parsed.data.regularMarketTime.toISOString(),
    symbol,
  };
}

/** One hour: the index moves once a session, and Yahoo answers 429 to undisciplined callers. */
const CACHE_TTL_MS = 60 * 60 * 1000;

/** A failure is remembered briefly; retrying it on every request is the 429 amplifier. */
const FAILURE_TTL_MS = 30 * 1000;

/** The package sets no fetch timeout of its own, so a stalled socket would hold the handler open. */
const FETCH_TIMEOUT_MS = 5_000;

export interface RateReaderOptions {
  ttlMs?: number;
  failureTtlMs?: number;
  /** Injected so the cache's expiry behaviour is testable without waiting. */
  now?: () => number;
}

export interface RateReader {
  read(): Promise<RiskFreeRate>;
  reset(): void;
}

/**
 * A cache in front of one source, with three properties this estate needs and one process-wide.
 *
 * - **Single flight.** A cold cache hit by N concurrent requests makes one outbound call. Without it
 *   there would be N simultaneous `v7/finance/quote` round trips (and N turns at the package's
 *   four-slot queue) for one figure — the client is already shared, and the package de-dupes its own
 *   crumb request, so those are not the things this control saves.
 * - **A brief negative cache.** During an outage the cache would otherwise stay empty and every
 *   inbound request would make its own outbound attempt. A failure is held for `failureTtlMs` and
 *   rethrown, so the route answers 503 without becoming the 429 generator.
 * - **A seam.** `source` and `now` are parameters, so the stateful half is tested with no module
 *   mocking and no real clock.
 *
 * `reset` clears the caches and bumps a generation counter, so a read that was already in flight
 * cannot write its (now stale) value back afterwards. A caller already awaiting that read still
 * receives its value — the reset governs the cache, not promises already handed out.
 */
export function createRateReader(
  source: () => Promise<RiskFreeRate>,
  options: RateReaderOptions = {},
): RateReader {
  const ttlMs = options.ttlMs ?? CACHE_TTL_MS;
  const failureTtlMs = options.failureTtlMs ?? FAILURE_TTL_MS;
  const now = options.now ?? Date.now;

  let cached: { value: RiskFreeRate; expiresAt: number } | null = null;
  let failed: { error: MarketDataUnavailableError; expiresAt: number } | null = null;
  let inFlight: Promise<RiskFreeRate> | null = null;
  // Bumped by `reset`. A read that started before the bump must not write the cache or clear
  // `inFlight` when it settles: otherwise a reset during a fetch leaves the pre-reset value cached
  // for a full TTL, and a stale `finally` would let a third reader start a second fetch.
  let generation = 0;

  return {
    async read() {
      if (cached && cached.expiresAt > now()) {
        return cached.value;
      }
      if (failed && failed.expiresAt > now()) {
        throw failed.error;
      }

      if (!inFlight) {
        const startedIn = generation;
        inFlight = (async () => {
          try {
            const value = await source();
            if (startedIn === generation) {
              cached = { value, expiresAt: now() + ttlMs };
              failed = null;
            }
            return value;
          } catch (error) {
            const failure =
              error instanceof MarketDataUnavailableError
                ? error
                : new MarketDataUnavailableError("Yahoo Finance quote failed", { cause: error });
            if (startedIn === generation) {
              failed = { error: failure, expiresAt: now() + failureTtlMs };
            }
            throw failure;
          } finally {
            if (startedIn === generation) {
              inFlight = null;
            }
          }
        })();
      }

      return inFlight;
    },

    reset() {
      generation += 1;
      cached = null;
      failed = null;
      inFlight = null;
    },
  };
}

let clientPromise: Promise<QuoteClient> | null = null;

/**
 * Build the real client, once.
 *
 * Imported dynamically so that a process which never reads a rate — every build, every unit test with
 * an injected client — never loads the package at all. The instance is kept because it owns the
 * cookie jar and the crumb: rebuilding it per refresh would repeat Yahoo's consent handshake.
 */
async function defaultClient(): Promise<QuoteClient> {
  if (!clientPromise) {
    clientPromise = (async () => {
      const { default: YahooFinance } = await import("yahoo-finance2");
      const yahooFinance = new YahooFinance({
        suppressNotices: ["yahooSurvey"],
        // Unset, the package fetches the npm registry when a result fails its own validation. This
        // repository pins its version, so the check only adds a second vendor to the failure path.
        versionCheck: false,
      });
      return {
        quote: (symbol: string) =>
          yahooFinance.quote(symbol, {}, {
            // Per call, never in the constructor: a constructor-level signal would abort every later
            // call once it fired.
            fetchOptions: { signal: AbortSignal.timeout(FETCH_TIMEOUT_MS) },
          }),
      };
    })();
    // A rejected construction must not be cached forever; the next call retries.
    clientPromise.catch(() => {
      clientPromise = null;
    });
  }

  return clientPromise;
}

const defaultReader = createRateReader(async () => fetchRiskFreeRate(await defaultClient()));

/** The cached rate, refreshed hourly. Throws {@link MarketDataUnavailableError} rather than guessing. */
export const getRiskFreeRate = defaultReader.read;
