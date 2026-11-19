import { describe, it, expect, vi, afterEach } from "vitest";
import { calculateValuation, API_BASE } from "@/lib/valuation/client";

/**
 * The calculator must talk to the surface that actually computes. It used to post to
 * `/v1/valuation/<method>`, a Next route that server-side fetched `${origin}/api/index.py` — a path
 * Next does not serve — so every calculation returned a 404 HTML page which the result card rendered
 * as text. This test fails on that URL, so the regression cannot come back silently.
 */
describe("the calculator's data path", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("posts to the Python engine's path, not the removed Next proxy", () => {
    expect(API_BASE).toBe("/api/valuation");
  });

  it("sends the method and parameters to /api/valuation/<method>", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ value: 62092.13, method: "Present Value" }) });
    vi.stubGlobal("fetch", fetchMock);

    const result = await calculateValuation("present-value", {
      future_value: 100000,
      discount_rate: 0.1,
      periods: 5,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/valuation/present-value");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ future_value: 100000, discount_rate: 0.1, periods: 5 });
    expect(result.value).toBe(62092.13);
  });

  it("surfaces the engine's error instead of rendering its body", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ error: "Invalid parameters: missing future_value" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(calculateValuation("present-value", {})).rejects.toThrow(/missing future_value/);
  });

  it("reports an HTML body as an engine error, not a parser crash", async () => {
    // This is the shape an ALB 502/504 takes, and the shape the old /v1/valuation proxy produced.
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new SyntaxError("Unexpected token '<'");
      },
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(calculateValuation("present-value", {})).rejects.toThrow(/did not return JSON/);
  });

  it("survives an error body that is JSON null or a bare scalar", async () => {
    // `data as ApiError` on `null` threw a TypeError, and CalculatorForm renders err.message — so the
    // TypeError became the result the user saw. The guard in client.ts exists for these two shapes;
    // this case fails if it is removed.
    for (const body of [null, 42, "nope"]) {
      const fetchMock = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => body,
      });
      vi.stubGlobal("fetch", fetchMock);

      await expect(calculateValuation("present-value", {})).rejects.toThrow(/^API error: 500$/);
    }
  });
});
