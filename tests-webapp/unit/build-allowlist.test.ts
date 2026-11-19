import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

/**
 * The install-script allowlist in `pnpm-workspace.yaml` is a security control, so it gets a check
 * rather than a comment.
 *
 * What went wrong without it: the list was written by walking every `package.json` under
 * `node_modules`, which picked up `ljharb-monorepo-symlink-test` — a test fixture *inside the
 * `resolve` tarball* at `resolve/test/resolver/multirepo/package.json`, not a package pnpm installs.
 * It could never have built, and pre-approving it was a standing grant for a name outside the graph.
 * Two reviewers found it independently. The first assertion below is the one that would have caught
 * it; the negative control for it is recorded in the PR body.
 *
 * These assertions check *configuration*. That pnpm aborts on an unlisted build is its documented
 * contract and was confirmed by hand once, in a scratch project, because no assertion here can run
 * an install: `onlyBuiltDependencies: []` + `strictDepBuilds: true` + a dependency with a
 * postinstall → `ERR_PNPM_IGNORED_BUILDS`, exit 1; the same package listed → exit 0.
 */

const ROOT = process.cwd();
const WORKSPACE = readFileSync(join(ROOT, "pnpm-workspace.yaml"), "utf8");
const LOCKFILE = readFileSync(join(ROOT, "pnpm-lock.yaml"), "utf8");

/** The entries under `onlyBuiltDependencies:`, in file order. */
function allowedBuildScripts(): string[] {
  const lines = WORKSPACE.split("\n");
  const start = lines.findIndex((line) => line.trim() === "onlyBuiltDependencies:");
  if (start === -1) return [];
  const names: string[] = [];
  for (const line of lines.slice(start + 1)) {
    const match = line.match(/^\s*-\s*"?([^"\s#]+)"?\s*$/);
    if (!match) break; // first non-list line ends the block
    names.push(match[1]);
  }
  return names;
}

/** `@scope/name@1.2.3` → `{ name: "@scope/name", version: "1.2.3" }`; a bare name has no version. */
function splitSpec(spec: string): { name: string; version?: string } {
  const at = spec.lastIndexOf("@");
  return at > 0 ? { name: spec.slice(0, at), version: spec.slice(at + 1) } : { name: spec };
}

describe("install-script allowlist", () => {
  it("names only packages that are actually in the dependency graph, at the version it pins", () => {
    const specs = allowedBuildScripts();
    expect(specs.length, "the allowlist is empty — did the key get renamed?").toBeGreaterThan(0);
    for (const spec of specs) {
      const { name, version } = splitSpec(spec);
      // Anchored to the lockfile key form (`  name@version:` / `  '@scope/name@version':`) rather
      // than a substring test: `resolver@` also occurs inside `unrs-resolver@1.12.2`, `cli@` inside
      // `@sentry/cli@2.39.1` and `canvas` inside `@sentry-internal/replay-canvas@…`, so a substring
      // would pass for a name that is not installed — the false positive that put a phantom in this
      // list. With a version present, the exact release must be the one in the lockfile.
      const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const suffix = version ? `@${version.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}` : "@";
      expect(
        new RegExp(`^ {2}'?${escaped}${suffix}'?:`, "m").test(LOCKFILE),
        `${spec} is allowed to run install scripts but is not that exact package in pnpm-lock.yaml`
      ).toBe(true);
    }
  });

  it("keeps the blanket permission off", () => {
    // The regression guard: this setting permits every dependency's scripts, transitive included.
    // It must catch the shapes a deliberate re-enable takes, not only a clean revert — an inline
    // comment, YAML 1.2's `True`, or a quoted "true" all still resolve to the boolean.
    expect(WORKSPACE).not.toMatch(
      /^\s*dangerouslyAllowAllBuilds:\s*["']?true["']?\s*(?:#.*)?$/im
    );
  });

  it("sets strictDepBuilds, so an unlisted build is an error rather than a warning", () => {
    // pnpm 10 defaults this to false: it skips the build, warns, and exits 0, so the allowlist
    // would fail late — at `pnpm build` or in the container — instead of here. (pnpm 11 flips the
    // default and retires `onlyBuiltDependencies`; see package.json's pnpm pin.)
    expect(WORKSPACE).toMatch(/^strictDepBuilds:\s*true\s*(?:#.*)?$/m);
  });

  it("keeps the image build safe while it ignores scripts", () => {
    // Dockerfile.web's deps stage runs `pnpm install --ignore-scripts` and does not copy this file,
    // so the image is built from a node_modules that no test run exercised. That is safe only while
    // the two conditions in its comment hold: Next does not need esbuild, and Sentry's build plugin
    // is not wired (so @sentry/cli's binary is not needed). Assert the second here; the first is
    // what `pnpm build` in the build stage would catch loudly.
    //
    // This is a tripwire, not a gate: it reads one file for one identifier, and a wrapper re-exported
    // without the name appearing (`export { default } from "./sentry.wrapped"`) would not trip it.
    // It catches the ordinary wiring forms, which is what a future change would look like.
    const nextConfig = readFileSync(join(ROOT, "next.config.ts"), "utf8");
    expect(
      nextConfig.includes("withSentryConfig"),
      "next.config.ts wraps the config in withSentryConfig — Dockerfile.web's --ignore-scripts is no longer safe"
    ).toBe(false);
  });
});
