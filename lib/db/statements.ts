/**
 * Split a `.surql` migration file into the statements the driver should send.
 *
 * The previous version was `sql.split(";")` followed by dropping any chunk that happened to start
 * with `--`. That works only while no comment contains a semicolon: one did, so a sentence in a
 * header comment became a "statement" and the migration failed with a parser error about prose.
 * Comments are removed first, line by line, and only then is the remainder split.
 *
 * Line comments only. No schema in this repository has a `--` inside a string literal, and a SQL
 * lexer here would be more risk than the problem it solves.
 */
export function splitStatements(sql: string): string[] {
  return sql
    .split("\n")
    // Strip to end of line, not only whole-line comments: `DEFINE …; -- note; prose` otherwise splits
    // inside the comment and sends `prose` to the parser — the bug this function exists to fix, one
    // line further along than the case that exposed it. Safe because no `--` in these files appears
    // inside a string literal, which `tests-webapp/unit/schema-statements.test.ts` asserts.
    .map((line) => {
      const comment = line.indexOf("--");
      return comment === -1 ? line : line.slice(0, comment);
    })
    .join("\n")
    .split(";")
    .map((statement) => statement.trim())
    .filter((statement) => statement.length > 0);
}
