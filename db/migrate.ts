import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { getSurrealClient, closeSurrealClient } from "@/lib/surreal/client";
import { assertSchemaNoReservedWords } from "@/lib/db/reserved-words";
import { splitStatements } from "@/lib/db/statements";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCHEMA_DIR = join(__dirname, "schema");

interface MigrationFile {
  name: string;
  path: string;
  order: number;
}

function getMigrationFiles(direction: "up" | "down" = "up"): MigrationFile[] {
  if (!existsSync(SCHEMA_DIR)) {
    throw new Error(`Schema directory not found: ${SCHEMA_DIR}`);
  }

  const files = readdirSync(SCHEMA_DIR)
    .filter((f) => f.endsWith(".surql"))
    .map((f) => {
      const match = f.match(/^(\d+)_(.+)\.surql$/);
      if (!match) throw new Error(`Invalid migration file name: ${f}. Expected format: NNN_description.surql`);
      return { name: f, path: join(SCHEMA_DIR, f), order: parseInt(match[1], 10) };
    });

  files.sort((a, b) => a.order - b.order);

  if (direction === "down") {
    files.reverse();
  }

  return files;
}

async function applyMigration(db: ReturnType<typeof getSurrealClient> extends Promise<infer T> ? T : never, file: MigrationFile): Promise<void> {
  const sql = readFileSync(file.path, "utf-8");
  assertSchemaNoReservedWords(sql, file.name);
  const statements = splitStatements(sql);

  for (const statement of statements) {
    try {
      await db.query(statement);
    } catch (error) {
      console.error(`  FAILED: ${file.name} — ${statement.slice(0, 80)}...`);
      throw error;
    }
  }

  console.log(`  OK: ${file.name}`);
}

async function migrate(): Promise<void> {
  const isRollback = process.argv.includes("--rollback");
  const direction = isRollback ? "down" : "up";

  console.log(`\nMigration: ${isRollback ? "ROLLBACK" : "UP"}\n`);

  const db = await getSurrealClient();
  const files = getMigrationFiles(direction);

  if (files.length === 0) {
    console.log("  No migration files found.");
    return;
  }

  for (const file of files) {
    await applyMigration(db, file);
  }

  console.log(`\n${isRollback ? "Rollback" : "Migration"} complete. ${files.length} file(s) processed.\n`);
}

migrate()
  .catch((error) => {
    console.error("\nMigration failed:", error);
    process.exit(1);
  })
  .finally(() => closeSurrealClient());
