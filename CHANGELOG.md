# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2026-10-03

### Changed

- Align package + manifest versions and re-publish under `simonmak-ascent`.

## [2.1.1] - 2026-10-02

### Changed

- Republish under the `simonmak-ascent` namespace: refresh PyPI project URLs and the MCP registry `mcp-name` marker.

## [2.1.0] - 2026-10-01

### Added

- **MCP prompts**: `purchase_price_allocation`, `value_ip_asset` and
  `impairment_test`, guided multi-method workflows whose tool/method steps and
  parameter lists are generated from the canonical tool surface.
- **MCP resources**: `intangible-valuation://methods` (full method catalog with
  required and optional parameters) plus one resource per tool, served by both the
  stdio server and the hosted endpoint (`prompts/*`, `resources/*`).
- Tool results now include `defaults_applied`, listing optional inputs that fell
  back to their defaults.

### Fixed

- Version drift: `pyproject.toml`, `mcp_server/pyproject.toml` and `server.json`
  are aligned again (the manifest said 2.0.2, the packages 2.0.1), and
  `serverInfo.version` is read from the installed package instead of a hard-coded
  2.0.0.

### Fixed
- **MCP Registry publish no longer races PyPI.** `publish-registry.yml` waits for the
  package version declared in `server.json` to be served by PyPI and to carry the
  `mcp-name:` ownership marker before calling `mcp-publisher publish`, via
  `scripts/wait_for_pypi.py`. A release now publishes to the registry on the first run, and
  re-dispatching an already-published version is an idempotent no-op instead of a failure.

## [2.0.1] — 2026-10-01

### Fixed
- Added the MCP Registry ownership marker
  (`<!-- mcp-name: io.github.simonmak-ascent/intangible-valuation -->`) to the package
  README so the PyPI stdio package passes ownership validation and publishes to the
  Official MCP Registry.

## [2.0.0] — 2026-09-30

### MCP 2.0.0 — Glama-ready tool surface
- Folded 49 flat MCP tools into **14 method-switched family tools** defined once in
  `mcp_server/tool_surface.py`; the stdio server is generated from it and the hosted
  Streamable-HTTP endpoint (`api/mcp.py`) shares the same surface.
- Every tool now carries a `title`, `outputSchema`, MCP `annotations`, `tags`, fully
  documented parameters, and TDQS-optimized descriptions (purpose, usage, alternatives,
  behaviour, per-method parameter mapping). `mcp-tdqs` lint: 0 errors, 100% param coverage.
- Added registry/reproducibility packaging: `glama.json`, `server.json`, `Dockerfile`,
  `mcp_server/` package; published to the Official MCP Registry as
  `io.github.simonmak-ascent/intangible-valuation`.
- **Registry manifests now declare both transports.** `server.json` carries a `packages`
  entry (PyPI `intangible-valuation`, `uvx` runtime, stdio transport) alongside the hosted
  `streamable-http` remote, and `glama.json` is a complete Glama manifest with pip/uvx
  install instructions. One version (`2.0.0`) is the single source of truth across
  `pyproject.toml`, `server.json`, and the MCP server, guarded by a packaging test.
- Added TDQS, CodeQL, OpenSSF Scorecard, scheduled pip-audit and MkDocs `--strict`
  workflows, plus a generated-server determinism gate and a production deploy canary.
- Exposed `/api/*` (hosted MCP + calculator) publicly and attached the canonical
  `intangible-valuation.simonmak.com` domain.
- Bumped `vitest` to 4.1.11, clearing two Dependabot advisories.
- 1082 tests, 91% coverage.

## [1.0.3] — 2026-05-21

### Authority Milestones
- Docs site migrated to Vercel (intangible-valuation.simonmak.com)
- GitHub Pages fully decommissioned (docs.yml, CNAME, gh-pages branch removed)
- Single `main` branch enforced — all side branches merged and deleted

### Content
- 3 example pages populated with 26 copy-paste runnable scenarios
  - Core Methods: 8 examples (PV, WACC, CAPM, annuities, terminal value, TAB, DLOM, control premium)
  - Advanced Methods: 10 examples (RFR, MPEEM, goodwill, PPA, impairment, Monte Carlo, decision trees, transfer pricing)
  - Industry Models: 8 case studies (pharma, SaaS, fintech, enterprise, retail, services, manufacturing, media)
- 4th AI Agent Skill added: impairment-testing (ASC 350 / IAS 36)
- discount-rate-construction skill rewritten with actual discount rate content
- 18-page GitHub Wiki published with valuation guides, regulatory references, case studies

### Technical
- `ValuationResult.__contains__` protocol added for dict-style access
- All 88 valuation functions return ValuationResult consistently
- Custom exceptions exported (ValuationError, InputValidationError, etc.)
- `brand_strength_index` accepts 0-100 scale (normalized internally)
- `mpeem()` handles simple list inputs for contributory_asset_charges
- All doc counts updated (49 MCP tools, 1056 tests)

## [1.0.2] — 2026-05-21

### Fixed
- Updated MCP tool count from 54 to 49 in all docs
- Updated test count from 698 to 1056 in all docs
- Removed stale `github.io` URL references from README

## [1.0.1] — 2026-05-21

### Fixed
- All public functions now return `ValuationResult` consistently (was mixed dict/ValuationResult)
- Package import path: `src/` renamed to `src/intangible_valuation/` per Python packaging standards
- `__version__` now sourced from `importlib.metadata` (single source of truth)
- CI/CD workflows: E501 ruff errors, pyjwt security audit, API doc references
- MCP docs example values corrected to actual computed output
- README docs badge updated to custom domain
- `ValuationResult` now supports dict-like protocol (`in`, `[]`, `.get()`, `.keys()`)
- `trademark_valuation()` accepts `brand_strength_index` on 0-100 scale
- `mpeem()` now handles simple list inputs for `contributory_asset_charges`
- `goodwill()` steps converted to strings for consistency

### Changed
- Skill directories renamed to match README (`valuation-calculator` → `asset-valuation`, etc.)
- docs/skills.md removed references to non-existent Monte Carlo/Decision Tree skills
- Dependency upper bounds added (`pydantic<3.0`, `numpy<3.0`)

## [1.0.0] — 2026-05-20

### Added
- MIT LICENSE file
- Official GitHub Actions deployment workflow (bypasses Jekyll)
- PyPI publish workflow aligned with release triggers
- Example documentation pages (core methods, advanced methods, industry models)
- Chapter index documentation page

### Fixed
- 59 E501 line-too-long errors in `mcp_server/tools.py`
- Import sorting in `mcp_server/server.py`
- `monte_carlo.py` type annotation for strict mypy build
- PyPI description field length (under 512 char limit)
- GitHub Pages layout (switched from Jekyll branch to GitHub Actions)

### Changed
- Version bumped from 0.1.0 to 1.0.0
- Development status from Alpha to Production/Stable

## [0.1.0] — 2026-05-20

### Added
- Book-aligned documentation site with Amazon purchase link
- Book hero section on homepage with cover image and description
- Chapter-to-module mapping table
- Ascent Partners branding (logo, `#0083AB` color, Titillium Web/Open Sans fonts)
- 124+ valuation functions across 22 modules
- MCP server with 54 tools
- 3 AI-Agent Skills (asset-valuation, discount-rate-construction, purchase-price-allocation)
- 698 unit tests against textbook example values
- GitHub Pages documentation site (MkDocs Material)
- `CITATION.cff` for academic referencing
- mypy type checking in CI
- GitHub Actions CI/CD workflows

### Core Mathematics (Chapter 2)
- Time value of money: PV, FV, annuity, perpetuity, growing annuity, terminal value
- Discount rates: build-up, CAPM, WACC, TAB, control premium, DLOM, currency adjustment
- Statistics: Monte Carlo simulation, decision trees

### Valuation Approaches (Chapter 3)
- Cost approach: reproduction cost, replacement cost
- Market approach: comparable transactions, royalty capitalization

### Income Methods (Chapter 4)
- Relief from Royalty with tax amortization benefit
- Multi-Period Excess Earnings Method (MPEEM)
- Incremental cash flow analysis

### Asset Types (Chapters 5–9)
- Intellectual property: patent, trademark, copyright, trade secret
- Technology: developed technology, software, data assets, platforms
- Customer-related: customer relationships, distribution network, non-compete
- Human capital: assembled workforce, key person

### Advanced Topics (Chapters 10–18)
- Goodwill calculation and PPA waterfall (ASC 805 / IFRS 3)
- Impairment testing (ASC 350 / IAS 36)
- Royalty analysis: benchmarking, 25% rule, adjustment
- Transfer pricing: CUP method
- Litigation damages: lost profits, pre-judgment interest
- Monte Carlo simulation and sensitivity analysis
- Decision tree analysis with backward induction
