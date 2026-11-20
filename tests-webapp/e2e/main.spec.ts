import { test, expect } from "@playwright/test";

/**
 * Assertions are scoped to a landmark (banner, main, contentinfo) and use exact matching where one
 * accessible name is a substring of another, because Playwright's strict mode fails an ambiguous
 * match rather than picking one.
 *
 * Six of the nine cases in this file were failing before this rewrite, and none of the failures was
 * about the product: the hero assertion tested a sentence that no longer exists ("…Authority"), and
 * the rest used bare `text=` locators that had become ambiguous as the copy grew — the footer
 * repeats three of the calculator's category names, and "Calculator" is a substring of "Try
 * Calculator". Nothing noticed, because no CI job runs this file: CI installs chromium and runs
 * `a11y.spec.ts` and `compliance.spec.ts` only. A spec that never runs is a claim, not a check.
 */

test.describe("Landing Page", () => {
  test("renders the hero and the two published counts", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1").first()).toContainText("Intangible Asset Valuation");
    // The two numbers the product publishes: 68 catalog methods and 14 MCP tools. The 14 is the
    // control this one imitates — tests/test_tool_count_copy.py compares every published statement
    // of the tool count with `tool_count()` across 15 files. The 68 in the footer is still a
    // hardcoded literal with nothing tying it to `CATALOG.length`, so asserting it here at least
    // fails when the copy changes; a method-count equivalent of that Python test does not exist yet.
    await expect(page.getByText("68 methods").first()).toBeVisible();
    await expect(page.getByText("14 tools").first()).toBeVisible();
  });

  test("navigates to calculator from the primary CTA", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Try Calculator" }).first().click();
    await expect(page).toHaveURL(/\/calculator/);
  });
});

test.describe("Calculator", () => {
  test("displays the method categories", async ({ page }) => {
    await page.goto("/calculator");
    const main = page.getByRole("main");
    await expect(main.getByText("Core Methods").first()).toBeVisible();
    await expect(main.getByText("Valuation Approaches").first()).toBeVisible();
    await expect(main.getByText("Income Methods").first()).toBeVisible();
  });

  test("navigates to a method page", async ({ page }) => {
    await page.goto("/calculator/present-value");
    await expect(page.locator("h1").first()).toContainText("Present Value");
    await expect(page.getByRole("button", { name: /calculat/i }).first()).toBeVisible();
  });

  test("computes a present value through the Python engine", async ({ page }) => {
    // /api/* is the Python container behind the ALB; `next dev` serves no such route, so this can only
    // pass against a deployed origin (PLAYWRIGHT_BASE_URL). Skipping is honest; asserting here was not.
    test.skip(!process.env.PLAYWRIGHT_BASE_URL, "needs a deployed origin — next dev has no /api/*");
    await page.goto("/calculator/present-value");

    await page.fill('input[placeholder*="Future value"]', "100000");
    await page.fill('input[placeholder*="discount"]', "0.10");
    await page.fill('input[placeholder*="periods"]', "5");

    await page.click('button[type="submit"]');

    // 100000 / 1.1^5 = 62092.13. The previous assertion accepted "error" as a pass, which is how a
    // 404 HTML page rendered into the result card shipped and stayed green.
    await expect(page.getByText("$62,092.13")).toBeVisible({ timeout: 15000 });
  });
});

test.describe("MCP Gateway", () => {
  test("displays setup instructions", async ({ page }) => {
    await page.goto("/developers/mcp");
    await expect(page.getByText("Quick Start").first()).toBeVisible();
    // Substring match: only the command block spells the full spec (the prose above it says just
    // `pip install`). `.first()` keeps strict mode quiet if another line ever quotes it.
    await expect(page.getByText("pip install intangible-valuation").first()).toBeVisible();
  });
});

test.describe("Skills Page", () => {
  test("lists the four skills", async ({ page }) => {
    await page.goto("/skills");
    for (const name of [
      "Asset Valuation",
      "Discount Rate Construction",
      "Purchase Price Allocation",
      "Impairment Testing",
    ]) {
      await expect(page.getByText(name, { exact: true }).first()).toBeVisible();
    }
  });
});

test.describe("Navigation", () => {
  test("header links work", async ({ page }) => {
    await page.goto("/");
    // Scoped to the banner, and exact: `name: "Calculator"` also matches "Try Calculator".
    await page
      .getByRole("banner")
      .getByRole("link", { name: "Calculator", exact: true })
      .click();
    await expect(page).toHaveURL(/\/calculator/);
  });

  test("footer links present", async ({ page }) => {
    await page.goto("/");
    // Scoped to contentinfo: "Documentation" is also a CTA inside main on the landing page.
    const footer = page.getByRole("contentinfo");
    await expect(footer.getByRole("link", { name: "Documentation" })).toBeVisible();
    await expect(footer.getByRole("link", { name: "GitHub" })).toBeVisible();
  });
});
