import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

/**
 * `middleware.ts` protects exactly two surfaces — `/admin` and `/dashboard` — and lets everything else
 * fall through so the router can answer 404. Both properties are one careless edit away from breaking,
 * and both have broken once:
 *
 *  - an early `NextResponse.next()` was added *above* the guards to "let static assets through", which
 *    meant a dotted path under `/admin` skipped the session check entirely;
 *  - a `publicPaths` allowlist plus a `pathname.includes(".")` escape made the gate look default-deny
 *    while gating nothing, since the fallthrough was already `next()`.
 *
 * A comment cannot hold either property. This reads the file and asserts the order.
 */
const src = readFileSync(join(process.cwd(), "middleware.ts"), "utf8");

describe("middleware guard ordering", () => {
  it("has the admin guard before any NextResponse.next()", () => {
    const guard = src.indexOf('isAdminPath(pathname)');
    const firstNext = src.indexOf("NextResponse.next()");

    expect(guard, "no admin guard found").toBeGreaterThan(-1);
    expect(firstNext, "no NextResponse.next() found").toBeGreaterThan(-1);
    expect(
      firstNext,
      "a NextResponse.next() appears before the admin guard — a dotted path can skip the session check"
    ).toBeGreaterThan(guard);
  });

  it("has the dashboard guard before the fallthrough", () => {
    const guard = src.indexOf('isDashboardPath(pathname)');
    const adminNext = src.indexOf("NextResponse.next()", src.indexOf('isAdminPath(pathname)'));

    expect(guard).toBeGreaterThan(adminNext);
  });

  it("carries no allowlist and no dotted-path escape", () => {
    expect(src, "the allowlist is back; it gates nothing now that the fallthrough is open").not.toContain(
      "publicPaths"
    );
    expect(src, 'the "contains a dot" escape is back').not.toContain('includes(".")');
  });
});
