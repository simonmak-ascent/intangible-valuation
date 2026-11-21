import { describe, it, expect } from "vitest";
import {
  createRateReader,
  fetchRiskFreeRate,
  MarketDataUnavailableError,
  TREASURY_SYMBOLS,
  type QuoteClient,
  type RiskFreeRate,
} from "@/lib/market/treasury";

/**
 * The rate crosses a network boundary and an untyped JSON parse, so every case here is about a
 * payload that must NOT become a plausible-looking number. A fake client is injected throughout: no
 * test in this file reaches Yahoo, and none needs the package loaded.
 */

const quote = (overrides: Record<string, unknown> = {}) => ({
  symbol: "^TNX",
  regularMarketPrice: 4.912,
  regularMarketTime: new Date("2026-11-20T19:59:55Z"),
  ...overrides,
});

const clientReturning = (payload: unknown): QuoteClient => ({ quote: async () => payload });

describe("fetchRiskFreeRate", () => {
  it("converts the index's percent into the decimal fraction the library takes", async () => {
    const rate = await fetchRiskFreeRate(clientReturning(quote()));

    // ^TNX quotes 4.912 meaning 4.912%; CAPM wants 0.04912. Both are reported so a caller never has to
    // guess which one it received.
    expect(rate.rate).toBe(0.04912);
    expect(rate.percent).toBe(4.912);
    expect(rate.asOf).toBe("2026-11-20T19:59:55.000Z");
    expect(rate.symbol).toBe("^TNX");
  });

  it("keeps the session the quote belongs to rather than implying it is today's", async () => {
    // A Friday close read on a Sunday keeps Friday's timestamp: the point of returning `asOf`.
    const rate = await fetchRiskFreeRate(clientReturning(quote()));
    expect(rate.asOf.startsWith("2026-11-20")).toBe(true);
  });

  it("rounds both values to the precision the payload carries", async () => {
    // The wire value is a float tail: 4.911999702453613. Four decimals of a percent is its own
    // precision (`priceHint: 4`), and the fraction follows from that, not from the raw float.
    const rate = await fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: 4.9119997 })));
    expect(rate.percent).toBe(4.912);
    expect(rate.rate).toBe(0.04912);
  });

  it("asks Yahoo for the 10-year by default, and for another tenor on request", async () => {
    const asked: string[] = [];
    const spy: QuoteClient = {
      quote: async (symbol: string) => {
        asked.push(symbol);
        return quote({ symbol });
      },
    };

    await fetchRiskFreeRate(spy);
    await fetchRiskFreeRate(spy, TREASURY_SYMBOLS.thirtyYear);

    expect(asked).toEqual(["^TNX", "^TYX"]);
  });

  it("rejects a price that is a string, not a number", async () => {
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: "4.912" }))),
    ).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("rejects a non-finite price instead of returning Infinity", async () => {
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: Number.POSITIVE_INFINITY }))),
    ).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("rejects a price that is already a fraction, which would otherwise read as 0.05%", async () => {
    // A vendor switch to decimals would otherwise be served as 0.000491 — the four-decimal percent
    // (0.0491) then divided by 100 — a plausible-looking rate, which is the one outcome this module
    // must never produce.
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: 0.04912 }))),
    ).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("accepts a bill's near-zero yield, which the note floor would refuse", async () => {
    // ^IRX traded around 0.01–0.15% in 2020-21: a 0.5 floor would refuse correct vendor data.
    const rate = await fetchRiskFreeRate(
      clientReturning(quote({ symbol: "^IRX", regularMarketPrice: 0.05 })),
      TREASURY_SYMBOLS.thirteenWeek,
    );
    expect(rate.percent).toBe(0.05);
    expect(rate.rate).toBe(0.0005);
  });

  it("refuses that same value for a note, where it is a fraction sent by mistake", async () => {
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: 0.05 }))),
    ).rejects.toThrow(/0\.1-25%/);
  });

  it("accepts the 5-year's August 2020 close, which a 0.5 floor would have refused", async () => {
    // Measured: ^FVX closed 0.195% on 2020-08-04 and stayed under 0.5% for weeks. A floor above that
    // is a false refusal of correct vendor data, not a guard.
    const rate5 = await fetchRiskFreeRate(
      clientReturning(quote({ symbol: "^FVX", regularMarketPrice: 0.195 })),
      TREASURY_SYMBOLS.fiveYear,
    );
    expect(rate5.percent).toBe(0.195);
    expect(rate5.rate).toBe(0.00195);
  });

  it("rejects an absurd magnitude and a zero", async () => {
    for (const price of [0, 4912, -4.912]) {
      await expect(
        fetchRiskFreeRate(clientReturning(quote({ regularMarketPrice: price }))),
      ).rejects.toBeInstanceOf(MarketDataUnavailableError);
    }
  });

  it("rejects an answer for a different instrument rather than serving it", async () => {
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ symbol: "^FVX" }))),
    ).rejects.toThrow(/\^FVX when \^TNX was requested/);
  });

  it("rejects epoch seconds where a Date is expected", async () => {
    // A future major handing back seconds rather than a Date is refused here. Nothing divides a
    // timestamp: had the schema taken any value, `asOf` would read 1970 — a wrong date on a correct
    // rate, not a wrong rate.
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketTime: 1763678395 }))),
    ).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("wraps a transport failure and keeps the vendor's error as the cause", async () => {
    const failure = new Error("429 Too Many Requests");
    const client: QuoteClient = {
      quote: async () => {
        throw failure;
      },
    };

    await expect(fetchRiskFreeRate(client)).rejects.toMatchObject({
      name: "MarketDataUnavailableError",
      cause: failure,
    });
  });

  it("names the field that failed, so a log is diagnosable without the payload", async () => {
    await expect(
      fetchRiskFreeRate(clientReturning(quote({ regularMarketTime: 1763678395 }))),
    ).rejects.toThrow(/regularMarketTime/);
  });
});

const rate: RiskFreeRate = {
  rate: 0.04912,
  percent: 4.912,
  asOf: "2026-11-20T19:59:55.000Z",
  symbol: "^TNX",
};

describe("createRateReader", () => {
  it("serves from cache inside the TTL and refetches once it expires", async () => {
    let clock = 0;
    let calls = 0;
    const reader = createRateReader(
      async () => {
        calls += 1;
        return rate;
      },
      { ttlMs: 1000, now: () => clock },
    );

    await reader.read();
    clock = 999;
    await reader.read();
    expect(calls).toBe(1);

    clock = 1001;
    await reader.read();
    expect(calls).toBe(2);
  });

  it("makes one outbound call for concurrent readers", async () => {
    // The regression test for the property the comments claim: without single flight this is 3.
    let calls = 0;
    const reader = createRateReader(async () => {
      calls += 1;
      await Promise.resolve();
      return rate;
    });

    await Promise.all([reader.read(), reader.read(), reader.read()]);
    expect(calls).toBe(1);
  });

  it("remembers a failure briefly, then retries", async () => {
    let clock = 0;
    let calls = 0;
    const reader = createRateReader(
      async () => {
        calls += 1;
        throw new MarketDataUnavailableError("boom");
      },
      { failureTtlMs: 500, now: () => clock },
    );

    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
    expect(calls).toBe(1); // the second read was served the cached failure, not Yahoo

    clock = 501;
    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
    expect(calls).toBe(2);
  });

  it("never serves a cached value in place of a fresh failure", async () => {
    let clock = 0;
    const reader = createRateReader(
      async () => {
        if (clock === 0) return rate;
        throw new MarketDataUnavailableError("down");
      },
      { ttlMs: 100, failureTtlMs: 100, now: () => clock },
    );

    await reader.read();
    clock = 101;
    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("wraps a non-market error so callers see one failure type", async () => {
    const reader = createRateReader(async () => {
      throw new TypeError("fetch failed");
    });

    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
  });

  it("does not let a read that started before reset write the cache afterwards", async () => {
    // The reset-during-fetch case: without the generation check, the older fetch overwrites the
    // cache for a full TTL and its `finally` clears a newer read's in-flight marker.
    let resolveFirst!: (value: RiskFreeRate) => void;
    const first = new Promise<RiskFreeRate>((resolve) => {
      resolveFirst = resolve;
    });
    const second: RiskFreeRate = { ...rate, rate: 0.04, percent: 4.0 };
    const stale: RiskFreeRate = { ...rate, rate: 0.03, percent: 3.0 };
    let calls = 0;

    const reader = createRateReader(
      async () => {
        calls += 1;
        return calls === 1 ? first : second;
      },
      { ttlMs: 10_000 },
    );

    const pending = reader.read(); // fetch A starts and hangs
    reader.reset();
    expect(await reader.read()).toEqual(second); // fetch B completes

    resolveFirst(stale); // A settles late
    await pending;

    expect(await reader.read()).toEqual(second); // the cache still holds B's value
    expect(calls).toBe(2);
  });

  it("does not let a pre-reset failure overwrite a newer one", async () => {
    let rejectFirst!: (error: unknown) => void;
    const first = new Promise<RiskFreeRate>((_, reject) => {
      rejectFirst = reject;
    });
    let calls = 0;

    const reader = createRateReader(
      async () => {
        calls += 1;
        if (calls === 1) return first;
        throw new MarketDataUnavailableError("fresh");
      },
      { failureTtlMs: 60_000 },
    );

    const pending = reader.read(); // fetch A hangs
    reader.reset();
    await expect(reader.read()).rejects.toThrow("fresh"); // fetch B fails
    rejectFirst(new MarketDataUnavailableError("stale")); // A fails late
    await expect(pending).rejects.toThrow("stale");

    // The cached failure must still be B's: without the guard, A's late write wins.
    await expect(reader.read()).rejects.toThrow("fresh");
    expect(calls).toBe(2);
  });

  it("does not let a pre-reset read clear a newer read's in-flight marker", async () => {
    let resolveFirst!: (value: RiskFreeRate) => void;
    let resolveSecond!: (value: RiskFreeRate) => void;
    const first = new Promise<RiskFreeRate>((resolve) => {
      resolveFirst = resolve;
    });
    const second = new Promise<RiskFreeRate>((resolve) => {
      resolveSecond = resolve;
    });
    let calls = 0;

    const reader = createRateReader(
      async () => {
        calls += 1;
        return calls === 1 ? first : second;
      },
      { ttlMs: 60_000 },
    );

    const pendingA = reader.read(); // A hangs
    reader.reset();
    const pendingB = reader.read(); // B hangs

    resolveFirst({ ...rate, rate: 0.03, percent: 3.0 });
    await pendingA; // A settles; its `finally` must not clear B's marker

    const third = reader.read(); // must join B, not start a third fetch
    expect(calls).toBe(2);

    resolveSecond(rate);
    await expect(third).resolves.toEqual(rate);
    await expect(pendingB).resolves.toEqual(rate);
  });

  it("reset clears the remembered failure, so the next read retries", async () => {
    // Without `failed = null` in `reset`, the read after it would be served the failure held for
    // `failureTtlMs` instead of retrying — and no test would notice.
    let calls = 0;
    let failing = true;
    const reader = createRateReader(async () => {
      calls += 1;
      if (failing) throw new MarketDataUnavailableError("boom");
      return rate;
    });

    await expect(reader.read()).rejects.toBeInstanceOf(MarketDataUnavailableError);
    failing = false;
    reader.reset();
    await expect(reader.read()).resolves.toEqual(rate);
    expect(calls).toBe(2);
  });

  it("reset clears the cached value, so the next read refetches", async () => {
    // The other half, which no other case can see: every other `reset` here happens while a fetch is
    // pending, so `cached` is still null. Without `cached = null` in `reset`, this read is served the
    // value held for the full TTL instead of refetching.
    let calls = 0;
    const reader = createRateReader(
      async () => {
        calls += 1;
        return { ...rate, rate: 0.03 + calls / 100, percent: 3.0 + calls };
      },
      { ttlMs: 60 * 60 * 1000 },
    );

    const first = await reader.read();
    reader.reset();
    const second = await reader.read();

    expect(calls).toBe(2);
    expect(second).not.toEqual(first);
  });
});
