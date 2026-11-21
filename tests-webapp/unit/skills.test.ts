import fs from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

/**
 * The `/skills` page renders from `skills/<slug>/SKILL.md` (it read a hand-written copy until
 * 2026-11-21, which is how its "Required MCP Tools" chips came to list *methods* — `relief_from_royalty`,
 * `mpeem` — none of which is a tool). These assertions are the contract the page now depends on, and
 * they fail if a skill loses its front matter or names something that is not a tool.
 */

const ROOT = path.resolve(__dirname, "../..");

/** The catalogue is the directory, so the test discovers what the page discovers. */
const SLUGS = fs
  .readdirSync(path.join(ROOT, "skills"), { withFileTypes: true })
  .filter((e) => e.isDirectory() && fs.existsSync(path.join(ROOT, "skills", e.name, "SKILL.md")))
  .map((e) => e.name);

/**
 * The tool surface itself. A shape test accepts anything spelled `valuation_*` — a method key, a
 * plural typo, or a tool renamed in `tool_surface.py` and left behind here — so this asserts
 * membership in the declared surface, not the spelling.
 */
const TOOL_NAMES = new Set(
  Array.from(
    fs.readFileSync(path.join(ROOT, "mcp_server", "tool_surface.py"), "utf8").matchAll(/"name":\s*"(valuation_[a-z_]+)"/g),
    (m) => m[1],
  ),
);

/**
 * Kept in step with `app/(en)/skills/page.tsx`'s parser by hand. If that parser learns a new form
 * (quoted values, block lists), mirror it here — a copy that still understands only the old format
 * would test green against a page that had changed.
 */
function frontMatter(slug: string): Record<string, string> {
  const text = fs.readFileSync(path.join(ROOT, "skills", slug, "SKILL.md"), "utf8");
  const block = /^---\n([\s\S]*?)\n---/.exec(text);
  const fields: Record<string, string> = {};
  for (const line of (block?.[1] ?? "").split("\n")) {
    const kv = /^([a-z_]+):\s*(.*)$/.exec(line.trim());
    if (kv) fields[kv[1]] = kv[2];
  }
  return fields;
}

describe("the skills catalogue the page renders", () => {
  it("gives every directory under skills/ a SKILL.md", () => {
    // Deliberately not derived from SLUGS: the page and this file apply the same filter, so a
    // directory that loses its SKILL.md would vanish from both and from a test that starts at the
    // filtered list. Start from the raw directory so the omission is red.
    const dirs = fs
      .readdirSync(path.join(ROOT, "skills"), { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name);
    expect(dirs.length, "skills/ holds no skill directories").toBeGreaterThan(0);
    for (const slug of dirs) {
      expect(fs.existsSync(path.join(ROOT, "skills", slug, "SKILL.md")), `${slug} has no SKILL.md`).toBe(true);
    }
  });

  it("gives every skill a name, a description and a category", () => {
    for (const slug of SLUGS) {
      const fm = frontMatter(slug);
      expect(fm.name, `${slug} has no name`).toBeTruthy();
      expect(fm.description?.length ?? 0, `${slug} description is too short`).toBeGreaterThan(20);
      expect(["valuation", "workflow", "compliance"], `${slug} category`).toContain(fm.category);
    }
  });

  it("declares the fourteen tools the surface declares", () => {
    expect(TOOL_NAMES.size, "tool_surface.py should declare 14 tools").toBe(14);
  });

  it("names only real tool names under `tools:`", () => {
    // The tool surface is 14 names, all `valuation_*`. A method key such as `relief_from_royalty`
    // must not appear here — that was the defect this test exists to keep closed.
    for (const slug of SLUGS) {
      const raw = frontMatter(slug).tools ?? "";
      const tools = raw.replace(/^\[|\]$/g, "").split(",").map((t) => t.trim()).filter(Boolean);
      expect(tools.length, `${slug} lists no tools`).toBeGreaterThan(0);
      for (const tool of tools) {
        expect(TOOL_NAMES.has(tool), `${slug} names '${tool}', which tool_surface.py does not declare`).toBe(true);
      }
    }
  });
});

/**
 * The bodies are documentation an agent follows, and they are Markdown. A rewrite that drops one
 * opening fence turns the rest of the file into a code block — which happened, and every other test
 * stayed green because none of them read the bodies.
 */
describe("the skill bodies", () => {
  it("keeps every file's code fences balanced", () => {
    for (const slug of SLUGS) {
      const text = fs.readFileSync(path.join(ROOT, "skills", slug, "SKILL.md"), "utf8");
      const fences = text.split("\n").filter((line) => line.trimStart().startsWith("```")).length;
      expect(fences % 2, `${slug} has ${fences} fences — one is unclosed`).toBe(0);
    }
  });

  it("calls only tools, never a bare library function", () => {
    for (const slug of SLUGS) {
      const text = fs.readFileSync(path.join(ROOT, "skills", slug, "SKILL.md"), "utf8");
      for (const match of text.matchAll(/^([a-z_][a-z0-9_]*)\(/gm)) {
        expect(TOOL_NAMES.has(match[1]), `${slug} calls '${match[1]}', which is not a tool`).toBe(true);
      }
    }
  });
});

/**
 * A table headed "Method" is the reference a reader copies a `method` value from, so every backticked
 * name in one must be a real method key. The call guard cannot see these — they are table cells, not
 * calls — and three of them were wrong (`build_up_discount_rate`, `capm_discount_rate`,
 * `market_approach_comparables`) while the suite was green.
 */
describe("the method reference tables", () => {
  const METHOD_KEYS = new Set(
    Array.from(
      fs.readFileSync(path.join(ROOT, "mcp_server", "tool_surface.py"), "utf8").matchAll(
        /_method\(\s*"([a-z_]+)"/g,
      ),
      (m) => m[1],
    ),
  );

  it("parses the surface's method keys", () => {
    expect(METHOD_KEYS.size).toBeGreaterThan(30);
    expect(METHOD_KEYS.has("build_up")).toBe(true);
  });

  it("lists only method keys under a Method heading", () => {
    for (const slug of SLUGS) {
      const lines = fs.readFileSync(path.join(ROOT, "skills", slug, "SKILL.md"), "utf8").split("\n");
      let inMethodTable = false;
      for (const line of lines) {
        if (line.startsWith("|")) {
          if (/\|\s*Method\b/.test(line)) inMethodTable = true;
          if (!inMethodTable) continue;
          for (const name of Array.from(line.matchAll(/`([a-z_][a-z0-9_]*)`/g), (m) => m[1])) {
            expect(METHOD_KEYS.has(name), `${slug} lists '${name}' in a Method table, which is not a method key`).toBe(true);
          }
        } else if (line.trim() === "") {
          inMethodTable = false;
        }
      }
    }
  });
});
