-- ============================================================================
-- V001: Indexes — the two surviving tables only
--
-- Indexes on `users`, `valuations`, `api_metrics` and `skills_catalog` went with those tables on
-- 2026-11-19. An index naming a table this schema no longer creates is not part of the schema: on a
-- fresh database it has no subject, and on a populated one it would attach to whatever still bears
-- that name.
-- ============================================================================

-- Benchmarks: fast defaults lookup
DEFINE INDEX idx_benchmarks_category_stage ON benchmarks COLUMNS category, business_stage;
DEFINE INDEX idx_benchmarks_asset ON benchmarks COLUMNS asset_type;
DEFINE INDEX idx_benchmarks_industry ON benchmarks COLUMNS industry;

-- Method catalog: slug lookup
DEFINE INDEX idx_method_slug ON method_catalog COLUMNS slug UNIQUE;
DEFINE INDEX idx_method_category ON method_catalog COLUMNS category;
