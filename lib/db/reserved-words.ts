// SurrealDB reserved words — a field/table name in this list breaks the
// SurrealQL parser (a field named `function` failed in the sibling repo).
// Every schema field/table name is validated against this list before migration.
//
// `value` was in this list and is not a parser keyword: measured on SurrealDB 3.2.0 and again on
// 2.3.7, `DEFINE FIELD value ON benchmarks TYPE number ASSERT $value != NONE;` plus
// `INSERT INTO benchmarks { value: 1.0 }` both succeed, and `SELECT *` returns the field.
// SurrealDB's own language tests use the bare identifier the same way. Its presence made
// `pnpm db:migrate` refuse this repository's own `db/schema/001_tables.surql` — the guard fired before
// any SQL was sent, so the schema had never been applied from this file.
//
// Still contextual: `DEFINE FIELD … VALUE` and `$value` inside ASSERT are keywords, and `SELECT value
// FROM x` is ambiguous with the `SELECT VALUE` clause, so backtick the identifier in a hand-written
// projection. Nothing here does that — the routes use `SELECT *` and the seed writes an object key.

export const RESERVED_WORDS = [
  "function", "return", "table", "field", "index", "event", "select", "update", "delete", "create",
  "if", "then", "else", "end", "type", "in", "out", "set", "let", "from", "where", "group", "order",
  "limit", "start", "on", "as", "none", "null", "true", "false", "and", "or", "not",
];

export function assertNotReserved(name: string, context: string): void {
  if (RESERVED_WORDS.includes(name.toLowerCase())) {
    throw new Error(`Reserved word '${name}' used as ${context}`);
  }
}

export function assertSchemaNoReservedWords(surql: string, file: string): void {
  const fieldMatches = surql.matchAll(/DEFINE (FIELD|TABLE)\s+([A-Za-z_][A-Za-z0-9_]*)/g);
  for (const match of fieldMatches) {
    const name = match[2];
    if (RESERVED_WORDS.includes(name.toLowerCase())) {
      throw new Error(`Reserved word '${name}' used in ${file} (DEFINE ${match[1].toUpperCase()})`);
    }
  }
}
