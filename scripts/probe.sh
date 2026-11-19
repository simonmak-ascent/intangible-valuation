#!/usr/bin/env bash
# probe.sh — prove the tests can fail before the fix.
#
# A test that has never been red is decoration. This runs the change-set's tests against the code
# *without* the non-test changes: if they still pass, they do not exercise the fix, and the change is
# untested no matter what the suite says.
#
#   scripts/probe.sh --repo . --base origin/main \
#     --install-cmd 'pnpm install --frozen-lockfile' \
#     --test-cmd 'pnpm vitest run src/thing.test.ts'
#
# Exit 0 = the probe bit (tests failed without the fix). Exit 1 = they passed anyway.
# Exit 2 = the probe could not run, or the failure was the harness rather than an assertion —
# never treat that as a pass.
#
# TRUST BOUNDARY. `--test-cmd` and `--install-cmd` are the caller's own strings and are executed with
# `eval` inside the worktree. That is deliberate: the caller is the repository's own workflow, which
# can already run anything. A self-gaming caller (`--test-cmd false`) would "bit" every time; the
# guard against that is review of the caller's workflow, not this script.
#
# WHY THE DEPENDENCIES ARE INSTALLED TWICE. `git worktree add` checks out tracked files only, so the
# base tree has no node_modules, no venv, no build output. Running the tests there without installing
# fails for the wrong reason — a missing runner exits non-zero and would be read as "the test failed",
# which is exactly the false confidence this script exists to remove. `--install-cmd` therefore runs
# inside the worktree before the tests, and a harness failure is detected and refused (exit 2) rather
# than counted as the probe biting.
set -euo pipefail

REPO=""; BASE=""; TEST_CMD=""; INSTALL_CMD=""; ALLOW_NO_TESTS=0
HARNESS='Cannot find module|MODULE_NOT_FOUND|ModuleNotFoundError|command not found|No such file or directory|ERR_MODULE_NOT_FOUND|package.json not found'
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --base) BASE="${2:-}"; shift 2 ;;
    --test-cmd) TEST_CMD="${2:-}"; shift 2 ;;
    --install-cmd) INSTALL_CMD="${2:-}"; shift 2 ;;
    --harness-pattern) HARNESS="${2:-}"; shift 2 ;;
    --allow-no-tests) ALLOW_NO_TESTS=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$REPO" ] && [ -d "$REPO/.git" ] || { echo "probe: --repo must be a git checkout" >&2; exit 2; }
[ -n "$TEST_CMD" ] || { echo "probe: --test-cmd is required (the command that runs the changed tests)" >&2; exit 2; }
REPO="$(cd "$REPO" && pwd)"
BASE="${BASE:-origin/main}"

cd "$REPO"
git rev-parse --verify --quiet "$BASE^{commit}" >/dev/null || { echo "probe: unknown base $BASE" >&2; exit 2; }

# The change-set as it stands in the working tree, committed or not.
changed=$(git diff --name-only "$BASE" 2>/dev/null; git ls-files --others --exclude-standard)
mapfile -t files < <(printf '%s\n' "$changed" | sed '/^$/d' | sort -u)

is_test() {
  case "$1" in
    *.test.ts|*.test.tsx|*.spec.ts|*.spec.tsx|*.test.js|*.test.jsx|*.spec.js|*.test.mjs|*.spec.mjs|\
    *_test.js|*_test.ts|test_*.py|*_test.py|*_test.go|conftest.py) return 0 ;;
    tests/*|test/*|__tests__/*|*/tests/*|*/__tests__/*|*/test/*) return 0 ;;
    *) return 1 ;;
  esac
}

tests=(); sources=()
for f in "${files[@]}"; do
  if is_test "$f"; then tests+=("$f"); else sources+=("$f"); fi
done

if [ "${#tests[@]}" -eq 0 ]; then
  [ "$ALLOW_NO_TESTS" -eq 1 ] && { echo "probe: no test files changed; skipped by --allow-no-tests"; exit 0; }
  echo "probe: FAIL — no test file in the change-set, so nothing can prove the change" >&2
  exit 2
fi

work=$(mktemp -d)
cleanup() { git -C "$REPO" worktree remove --force "$work/tree" >/dev/null 2>&1 || true; rm -rf "$work"; }
trap cleanup EXIT

echo "probe: base $BASE, ${#tests[@]} test file(s), ${#sources[@]} non-test file(s)"
git worktree add --detach "$work/tree" "$BASE" >/dev/null 2>&1

# Only the tests travel. If the fix is what makes them pass, they cannot pass here.
for f in "${tests[@]}"; do
  [ -f "$REPO/$f" ] || continue
  mkdir -p "$work/tree/$(dirname "$f")"
  cp "$REPO/$f" "$work/tree/$f"
done

if [ -n "$INSTALL_CMD" ]; then
  echo "probe: installing in the base tree so a missing runner is not mistaken for a failing test"
  if ! ( cd "$work/tree" && eval "$INSTALL_CMD" ) >"$work/install" 2>&1; then
    echo "probe: COULD NOT RUN — the install failed in the base tree" >&2
    tail -5 "$work/install" | sed 's/^/        /' >&2
    exit 2
  fi
fi

set +e
( cd "$work/tree" && eval "$TEST_CMD" ) >"$work/out" 2>&1
status=$?
set -e

if [ "$status" -eq 0 ]; then
  echo "probe: FAIL — the tests pass without the fix, so they do not exercise it" >&2
  echo "        command: $TEST_CMD" >&2
  tail -5 "$work/out" | sed 's/^/        /' >&2
  exit 1
fi

# A non-zero exit is only evidence if the assertions ran. A missing module or a missing runner exits
# non-zero too, and reporting that as "the test failed" is the same false confidence in a new coat.
if grep -Eq "$HARNESS" "$work/out"; then
  echo "probe: COULD NOT RUN — the failure is the harness, not an assertion" >&2
  grep -E -m3 "$HARNESS" "$work/out" | sed 's/^/        /' >&2
  exit 2
fi

echo "probe: ok — the tests fail without the fix (exit $status)"
tail -5 "$work/out" | sed 's/^/        /'
