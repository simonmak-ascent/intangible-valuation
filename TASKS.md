# Execution list — deploy path and web image, 2026-11-20

| # | task | status | verify |
|---|---|---|---|
| 1.1 | `deploy-digest.yml`: `packages: write`, GHCR login, pre-pull before the rollout, unconditional `--publish-pointer` | done | `actionlint` exit 0; `--publish-pointer` present, `publish_pointer` input absent |
| 1.2 | pointer assertion: the `desired-<container>` tag resolves to the dispatched digest | done | assertion step gated on `!inputs.dry_run`, same as the converge step |
| 1.3 | `containers` required, no default; refuse a dispatch naming one role of a shared-digest pair | done | extracted step: api alone exits 1 naming mcp; both exits 0 |
| 1.4 | the job fails instead of skipping on a non-main ref | done | guard step first; job-level `if` absent |
| 1.5 | `compliance.json` declares `kind: container`, `deploy-digest.yml`, the converge unit and two probes | done | `json.load` reports kind container; only the caller arm remains red |
| 1.6 | health reports `IMAGE_DIGEST` when set, with the ambient-digest fixture in its tests | done | `IMAGE_DIGEST=sha256:ffff pytest tests/test_api/test_health.py` → 12 passed |
| 2.1 | web image publishes again: remove the unused npm toolchain from the run stage | done | built image: `command -v npm` absent; trivy exit 0 where the dispatch failed on 12 HIGH |
| 2.2 | pin the four `Dockerfile.web` base images by digest | done | `grep -c '^FROM .*@sha256:' Dockerfile.web` → 4 |
| 2.3 | correct the web container's `notes` in `container.json` | done | no occurrence of the node-built provenance sentences |
| 3.1 | one IAS 36 vocabulary: alias plus optional canonical parameter with mutual exclusion | done | both spellings post equal values; both-together and neither raise ValueError |
| 4.1 | CSP directives that need no nonce, in `next.config.ts` | done | header `object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'` on the built image; `/`, `/zh`, `/hk`, `/calculator`, `/docs` all 200 |
| 5.1 | delete the 11 local branches that are unmerged into `origin/main` | done | 11 archive tags verified against their tips; 10 branches deleted, `main` re-pointed at `origin/main` (64c56aa); manifest at `~/git/.branch-archive/manifest-2026-11-20.txt` |
| 5.2 | `HANDOVER.md` records the pointer mechanism and the assertion | done | `HANDOVER.md` names `--publish-pointer`, the pre-pull and the pointer assertion |
