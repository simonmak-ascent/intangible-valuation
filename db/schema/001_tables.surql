-- ============================================================================
-- V001: Tables — Intangible Valuation
--
-- Two tables survive. Removed on 2026-11-19 with auth and billing: the account model (`users`,
-- `valuations`, `audit_trail`), the billing model (`plans`, `subscriptions`, `usage`,
-- `webhook_events`, `consents`), and the tables nothing read (`api_metrics`, `skills_catalog`).
-- The estate's data class for this app is `none`, and the running web container carried no
-- `SURREALDB_*` env. The routes that read those tables were account-gated and are deleted here; the
-- one surviving reader is the benchmarks route, which answers 503 without a store rather than
-- returning rows.
--
-- `benchmarks` is the only table the application reads — `app/v1/benchmarks/route.ts`. It is written
-- only by `pnpm db:seed` (`lib/etl/import.ts`), which connects as root. `method_catalog` is retained
-- deliberately as the published method reference; nothing writes it at request time.
--
-- Removed tables leave their definitions behind in an existing database. Nothing in this repository
-- reads or writes them, but that does not make them unreachable: there are two interpolation sinks —
-- `GET /v1/benchmarks` (`app/v1/benchmarks/route.ts`) and the uncalled `getStageDefaults`
-- (`lib/valuation/defaults.ts`) — and the client connects as root, so a database wired to the web
-- container must not be treated as safe until both are parameterised or deleted and the residual
-- tables are dropped. Dropping them is a data operation an operator runs once, not a migration.
--
-- The permissions below take effect when a table is created. `db/migrate.ts` keeps no record of
-- applied migrations and runs every file on every invocation, so on a database where `benchmarks`
-- already exists this file aborts with "the table already exists" before reaching later statements:
-- an existing table must be removed, or redefined with OVERWRITE, before this file can re-apply.
-- ============================================================================

-- Benchmark data
--
-- Permissions live in the table definition, not in a later file. `DEFINE TABLE benchmarks
-- PERMISSIONS …` in a separate migration fails with "the table already exists", because this file
-- has already created it. That was the second of the two reasons `pnpm db:migrate` had never applied
-- on a clean database; the first was `lib/db/reserved-words.ts` rejecting the `value` field below.
DEFINE TABLE benchmarks SCHEMAFULL PERMISSIONS
  FOR select FULL
  FOR create, update, delete NONE;
DEFINE FIELD category ON benchmarks TYPE string ASSERT $value IN ['royalty_rate', 'discount_rate', 'useful_life', 'growth_rate'];
DEFINE FIELD business_stage ON benchmarks TYPE string ASSERT $value IN ['startup', 'growth', 'mature'];
DEFINE FIELD asset_type ON benchmarks TYPE string DEFAULT 'all';
DEFINE FIELD industry ON benchmarks TYPE string DEFAULT 'all';
DEFINE FIELD metric_name ON benchmarks TYPE string ASSERT $value != NONE;
DEFINE FIELD value ON benchmarks TYPE number ASSERT $value != NONE;
DEFINE FIELD unit ON benchmarks TYPE option<string>;
DEFINE FIELD p25 ON benchmarks TYPE option<number>;
DEFINE FIELD p75 ON benchmarks TYPE option<number>;
DEFINE FIELD source ON benchmarks TYPE string ASSERT $value != NONE;
DEFINE FIELD source_url ON benchmarks TYPE option<string>;
DEFINE FIELD last_updated ON benchmarks TYPE datetime DEFAULT time::now();

-- Method catalog
DEFINE TABLE method_catalog SCHEMAFULL PERMISSIONS
  FOR select FULL
  FOR create, update, delete NONE;
DEFINE FIELD slug ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD subcategory ON method_catalog TYPE option<string>;
DEFINE FIELD asset_types ON method_catalog TYPE option<array>;
DEFINE FIELD business_stages ON method_catalog TYPE option<array>;
DEFINE FIELD description ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD formula_tex ON method_catalog TYPE option<string>;
DEFINE FIELD textbook_reference ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD parameters ON method_catalog TYPE array ASSERT array::len($value) > 0;
DEFINE FIELD python_function ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD mcp_tool_name ON method_catalog TYPE option<string>;
DEFINE FIELD skill_reference ON method_catalog TYPE option<string>;
DEFINE FIELD complexity ON method_catalog TYPE string DEFAULT 'basic' ASSERT $value IN ['basic', 'intermediate', 'advanced'];
DEFINE FIELD is_active ON method_catalog TYPE bool DEFAULT true;
