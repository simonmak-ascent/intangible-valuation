import { defineConfig, devices } from "@playwright/test";

/**
 * Workstation and CI agree on one browser, because that is what is installed in both.
 *
 * This file used to declare four projects — chromium, firefox, safari (webkit) and mobile-chrome.
 * Only chromium is installed here (`~/.cache/ms-playwright` holds chromium builds and ffmpeg) and CI's
 * `pnpm exec playwright install chromium` installs only chromium, so a bare
 * `pnpm test:e2e` failed on the first firefox test with "Executable doesn't exist" before reaching
 * any assertion. A project that cannot launch is not coverage; it is a red run that hides whether
 * the suite that *can* run passes.
 *
 * Set PLAYWRIGHT_ALL_BROWSERS=1 after `pnpm exec playwright install firefox webkit` to get them back.
 *
 * `full-site.spec.ts` is excluded unless PLAYWRIGHT_LIVE=1: it defaults its base URL to the live
 * origin and posts to it, so including it in a local run means every `pnpm test:e2e` writes to
 * production. AGENTS.md already describes it as the deploy-time suite; this makes the default match
 * that description instead of contradicting it.
 *
 * An explicit file argument does not override `testIgnore` — it is applied at collection — so the
 * deploy-time run is `PLAYWRIGHT_LIVE=1 pnpm exec playwright test tests-webapp/e2e/full-site.spec.ts`.
 * Without the variable Playwright exits non-zero with "No tests found", which is loud rather than a
 * green run over nothing.
 */
const allBrowsers = process.env.PLAYWRIGHT_ALL_BROWSERS === "1";
const live = process.env.PLAYWRIGHT_LIVE === "1";

export default defineConfig({
  testDir: "./tests-webapp/e2e",
  testIgnore: live ? [] : ["**/full-site.spec.ts"],
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: allBrowsers
    ? [
        { name: "chromium", use: { ...devices["Desktop Chrome"] } },
        { name: "firefox", use: { ...devices["Desktop Firefox"] } },
        { name: "safari", use: { ...devices["Desktop Safari"] } },
        { name: "mobile-chrome", use: { ...devices["Pixel 5"] } },
      ]
    : [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    // `pnpm`, not `npm`: this repository is pnpm/lockfile-pinned, and the dev server should be
    // started by the package manager the lockfile belongs to.
    command: "pnpm exec next dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    // A cold Next dev start plus a full run of this suite took ~25s here; 180s leaves room for a
    // first compile on a loaded machine without turning a slow start into a failure.
    timeout: 180_000,
    cwd: process.cwd(),
  },
});
