// @vitest-environment node
import { describe, it, expect, vi, beforeEach } from "vitest";

/**
 * The route is glue, but the glue is the part a caller sees: it must never turn a failure into a
 * number. The rate module is mocked here — `treasury.test.ts` covers its real behaviour with an
 * injected client — so these cases are purely about the 200 and 503 shapes.
 */

const mocks = vi.hoisted(() => {
  class MarketDataUnavailableError extends Error {
    constructor(message: string, options?: { cause?: unknown }) {
      super(message, options);
      this.name = "MarketDataUnavailableError";
    }
  }
  return { getRiskFreeRate: vi.fn(), MarketDataUnavailableError };
});

vi.mock("@/lib/market/treasury", () => ({
  getRiskFreeRate: mocks.getRiskFreeRate,
  MarketDataUnavailableError: mocks.MarketDataUnavailableError,
}));

import { GET } from "@/app/v1/rates/risk-free/route";

const rate = {
  rate: 0.04912,
  percent: 4.912,
  asOf: "2026-11-20T19:59:55.000Z",
  symbol: "^TNX",
};

describe("GET /v1/rates/risk-free", () => {
  beforeEach(() => {
    mocks.getRiskFreeRate.mockReset();
  });

  it("serves the rate with a cache lifetime matching the in-process TTL", async () => {
    mocks.getRiskFreeRate.mockResolvedValue(rate);

    const response = await GET();

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(rate);
    expect(response.headers.get("cache-control")).toContain("max-age=3600");
  });

  it("answers 503 with a reason rather than a plausible number", async () => {
    mocks.getRiskFreeRate.mockRejectedValue(
      new mocks.MarketDataUnavailableError("Yahoo Finance returned an unusable quote for ^TNX"),
    );

    const response = await GET();

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({
      error: "market data unavailable",
      detail: "Yahoo Finance returned an unusable quote for ^TNX",
    });
  });

  it("does not leak an unexpected exception's message as a market-data detail", async () => {
    mocks.getRiskFreeRate.mockRejectedValue(new TypeError("fetch failed"));

    const response = await GET();

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({
      error: "market data unavailable",
      detail: "unexpected failure",
    });
  });

  it("is never prerendered, so the build cannot bake a rate into the image", async () => {
    const { dynamic } = await import("@/app/v1/rates/risk-free/route");
    expect(dynamic).toBe("force-dynamic");
  });
});
