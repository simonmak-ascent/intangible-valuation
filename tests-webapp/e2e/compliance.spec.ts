import { test, expect } from "@playwright/test";

/**
 * The pages that used to be reached through billing. There is nothing to buy: auth and billing were
 * removed on 2026-11-19, so `/pricing` is static copy and the plan tiers are
 * labels rather than products.
 *
 * Renamed from `billing.spec.ts` when the checkout half went away. That file's fourth case,
 * "checkout button degrades gracefully without billing config", asserted only that the Pro heading was
 * visible — not the 503 it was named after — so the replacement asserts something real instead: the
 * free tier's link target, and the absence of the CTAs that used to start a checkout.
 */
test.describe("Published pages (AC-COMP-01)", () => {
  test("pricing page renders all three tiers", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.getByRole("heading", { name: "Pricing" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Free" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Pro" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Enterprise" })).toBeVisible();
  });

  test("the free tier links to the calculator and nothing is purchasable", async ({ page }) => {
    await page.goto("/pricing");
    // The only actionable control in the tiers is the free tier's link; the paid tiers render as
    // disabled text. The theme toggle is a button on every page, so the assertion names the CTAs that
    // used to exist rather than counting buttons.
    await expect(page.getByRole("link", { name: "Open the calculator" })).toHaveAttribute("href", "/calculator");
    await expect(page.getByRole("button", { name: "Subscribe" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Contact sales" })).toHaveCount(0);
  });

  test("terms page renders (AC-COMP-01)", async ({ page }) => {
    await page.goto("/terms");
    await expect(page.getByRole("heading", { name: "Terms of Service" })).toBeVisible();
    // The page used to describe Stripe billing and a billing portal. Nothing takes payment now, and a
    // terms page that promises a payment relationship is a false statement rather than stale copy.
    await expect(page.locator("body")).not.toContainText("Stripe");
    await expect(page.locator("body")).not.toContainText("billing portal");
  });

  test("privacy page renders (AC-COMP-01)", async ({ page }) => {
    await page.goto("/privacy");
    await expect(page.getByRole("heading", { name: "Privacy Policy" })).toBeVisible();
    // Same reason: the policy described collecting an email, name, saved valuations and billing
    // status, none of which the service has.
    await expect(page.locator("body")).not.toContainText("Stripe");
    await expect(page.locator("body")).not.toContainText("saved valuations");
  });
});
