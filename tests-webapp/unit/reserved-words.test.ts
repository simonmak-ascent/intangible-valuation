import { describe, it, expect } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { assertNotReserved, assertSchemaNoReservedWords } from "@/lib/db/reserved-words";

describe("Reserved-word denylist (lesson: `function` field broke SurrealQL)", () => {
  it("rejects a reserved word field name", () => {
    expect(() => assertNotReserved("function", "field")).toThrow(/Reserved word/);
  });

  it("allows a normal field name", () => {
    expect(() => assertNotReserved("result_value", "field")).not.toThrow();
  });

  it("is case-insensitive", () => {
    expect(() => assertNotReserved("SELECT", "field")).toThrow(/Reserved word/);
  });

  it("rejects reserved words in schema SQL", () => {
    expect(() =>
      assertSchemaNoReservedWords("DEFINE FIELD function ON t TYPE string;", "001.surql")
    ).toThrow(/Reserved word 'function'/);
  });

  it("passes clean schema SQL", () => {
    expect(() =>
      assertSchemaNoReservedWords("DEFINE FIELD result_value ON valuations TYPE number;", "001.surql")
    ).not.toThrow();
  });

  it("allows `value` as a field name — it is contextual, not a parser keyword", () => {
    // Measured on SurrealDB 3.2.0 and 2.3.7: this statement, `INSERT INTO benchmarks { value: 1.0 }`
    // and `SELECT *` all succeed. The denylist carried `value` anyway, so `pnpm db:migrate` refused the
    // repository's own schema before sending a single statement.
    expect(() =>
      assertSchemaNoReservedWords(
        "DEFINE FIELD value ON benchmarks TYPE number ASSERT $value != NONE;",
        "001.surql"
      )
    ).not.toThrow();
  });

  it("accepts every file in db/schema, which is what the guard exists to allow", () => {
    // The unit tests above pin individual words; this one pins the property they are a proxy for.
    // A denylist entry that rejects the schema it guards is worse than no guard, because migrate.ts
    // fails with a parser message about a word that parses.
    const dir = join(process.cwd(), "db", "schema");
    const files = readdirSync(dir).filter((f) => f.endsWith(".surql"));
    expect(files.length).toBeGreaterThan(0);
    for (const file of files) {
      const sql = readFileSync(join(dir, file), "utf8");
      expect(() => assertSchemaNoReservedWords(sql, file), file).not.toThrow();
    }
  });
});
