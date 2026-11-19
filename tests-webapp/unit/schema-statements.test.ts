import { describe, it, expect } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { splitStatements } from "@/lib/db/statements";

describe("migration statement splitting", () => {
  it("drops line comments and trailing separators", () => {
    const sql = "-- a header\nDEFINE TABLE a SCHEMAFULL;\n\nDEFINE TABLE b SCHEMAFULL;\n";
    expect(splitStatements(sql)).toEqual(["DEFINE TABLE a SCHEMAFULL", "DEFINE TABLE b SCHEMAFULL"]);
  });

  it("does not turn a semicolon inside a comment into a statement", () => {
    // This is the case that broke `pnpm db:migrate`: prose was sent to the parser as SQL.
    const sql = [
      "-- Tables. One table survives; the others were removed.",
      "-- Written by the seed job; read by one route.",
      "DEFINE TABLE benchmarks SCHEMAFULL;",
    ].join("\n");
    expect(splitStatements(sql)).toEqual(["DEFINE TABLE benchmarks SCHEMAFULL"]);
  });

  it("keeps indented comment lines out of the output", () => {
    expect(splitStatements("  -- indented note\nDEFINE FIELD x ON t TYPE string;")).toEqual([
      "DEFINE FIELD x ON t TYPE string",
    ]);
  });

  it("strips a comment that starts mid-line, semicolons included", () => {
    // Why this case exists: the first version stripped only whole-line comments, so the right-hand
    // side of this line split at the semicolon *inside the comment* and `prose` was sent as SQL.
    expect(splitStatements("DEFINE TABLE a; -- note; prose\nDEFINE TABLE b;")).toEqual([
      "DEFINE TABLE a",
      "DEFINE TABLE b",
    ]);
  });

  it("never leaves a statement fragment that came from a comment", () => {
    const statements = splitStatements("-- a; b; c\nDEFINE TABLE a; -- d; e\n");
    expect(statements).toEqual(["DEFINE TABLE a"]);
  });

  it("has no `--` inside a literal in any schema file, which is what line stripping assumes", () => {
    // Not a claim about SQL in general: a `--` inside a quoted string would be truncated by line
    // stripping, so the assumption is pinned rather than assumed. Counting quotes alone is not
    // enough — `VALUE "a--b"` is balanced and still truncated — so the literals themselves are read.
    const dir = join(process.cwd(), "db", "schema");
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".surql"))) {
      const sql = readFileSync(join(dir, file), "utf8");
      for (const line of sql.split("\n")) {
        const quotes = (line.match(/"/g) ?? []).length;
        expect(quotes % 2, `${file}: unbalanced quotes on: ${line.slice(0, 60)}`).toBe(0);
        const literals = line.match(/"[^"]*"/g) ?? [];
        expect(
          literals.some((literal) => literal.includes("--")),
          `${file}: \`--\` inside a literal on: ${line.slice(0, 60)}`
        ).toBe(false);
        // The splitter removes comments at `--` and then splits on `;`, so a semicolon inside a
        // literal fragments a statement exactly as prose did. That assumption is as load-bearing as
        // the one above and was previously unstated.
        expect(
          literals.some((literal) => literal.includes(";")),
          `${file}: \`;\` inside a literal on: ${line.slice(0, 60)}`
        ).toBe(false);
      }
    }
  });

  it("returns nothing for a file that is only comments", () => {
    expect(splitStatements("-- nothing here\n-- at all\n")).toEqual([]);
  });

  it("produces only comment-free statements for every file in db/schema", () => {
    const dir = join(process.cwd(), "db", "schema");
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".surql"))) {
      const statements = splitStatements(readFileSync(join(dir, file), "utf8"));
      expect(statements.length, file).toBeGreaterThan(0);
      for (const statement of statements) {
        expect(statement.split("\n")[0].trim().startsWith("--"), `${file}: ${statement.slice(0, 40)}`).toBe(false);
      }
    }
  });
});
