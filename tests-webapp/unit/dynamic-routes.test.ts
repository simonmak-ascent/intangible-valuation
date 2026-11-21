import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

/**
 * A dynamic route that renders whatever param it is given, under a `loading.tsx` boundary (a sibling
 * on `/calculator/[method]`, the `(en)` group's on `/docs/[slug]`), answers **200** for an unknown
 * path — `notFound()`'s "Page not found" body, or the calculator's own "Method Not Found" card — a
 * soft 404 that no status-code check catches and that search engines index. Measured in production
 * on 2026-11-21: `/docs/nope`, `/docs/value-in-use` and `/calculator/nope` all returned 200.
 *
 * `dynamicParams = false` makes the router answer 404 before the page renders. This is a tripwire,
 * not a gate: it asserts the declaration is present, because the behaviour it prevents is only
 * observable by requesting a URL that is not built.
 */
const ROUTES = [
  "app/(en)/docs/[slug]/page.tsx",
  "app/(en)/calculator/[method]/page.tsx",
];

const read = (file: string) => readFileSync(join(process.cwd(), file), "utf8");

describe("dynamic routes refuse unknown params", () => {
  it.each(ROUTES)("%s declares dynamicParams = false", (file) => {
    expect(read(file)).toMatch(/export const dynamicParams = false;/);
  });

  it.each(ROUTES)("%s enumerates its params, so the refusal has a list behind it", (file) => {
    expect(read(file)).toMatch(/export function generateStaticParams\(\)/);
  });
});
