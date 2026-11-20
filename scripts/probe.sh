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
HARNESS='Cannot find module|MODULE_NOT_FOUND|ModuleNotFoundError|ImportError|command not found|No such file or directory|ERR_MODULE_NOT_FOUND|package.json not found|no tests ran|deselected|No tests found|Missing script|SyntaxError|IndentationError'
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
#
# ONE EXCEPTION: a module this change-set ADDS cannot be imported in a tree that predates it. A test
# that starts with `import api.limits` against a new `api/limits.py` is a ModuleNotFoundError in the
# base tree, and that error is the proof the test needs the change — not a broken harness. Treating it
# as "could not run" made every change-set that adds a module fail the mandatory probe job, which is
# a gate that blocks correct work rather than a gate that finds defects. So the harness pattern is
# screened against the added-file list first, and only a module named there counts.
added_module_failure() {
  local added spec cand path rel hit matched=0
  # `R` as well as `A`: git reports a moved module under its new path as `R`, so `A` alone leaves a
  # module this change-set renamed unattributable — and refuses a test that genuinely needs the change.
  mapfile -t added < <( { git diff --name-only --diff-filter=AR "$BASE" 2>/dev/null
                          git ls-files --others --exclude-standard; } | sed '/^$/d' | sort -u )
  if [ "${#added[@]}" -eq 0 ]; then return 1; fi
  # `grep -oE` — one output line per occurrence — with `|| true`, rather than `sed -n`. Two reasons.
  # `sed`, a process substitution inherits `errexit` and `pipefail`, so an unguarded `grep` matching
  # nothing failed its pipeline and ended the substitution before the second extractor ran, which made
  # a Node-only failure produce no specifiers and report "could not run"; the `||` list keeps that
  # non-match out of `errexit`. And `sed -n "s/.*…/\1/p"` is greedy, so a line naming two modules
  # would yield only the last, silently exempting the first from the check below.
  while IFS= read -r spec; do
    [ -n "$spec" ] || continue
    hit=0
    case "$spec" in
      */*)
        # A path-like specifier: `./limits`, `../shared/x`, or the absolute id a bundler reports
        # (`file://` URL or resolved path). Normalised to repository-relative first, because the
        # probe runs in a worktree whose absolute prefix is not something the caller can predict.
        # `./x` is matched **by name**, not resolved against the importing file, which the message
        # does not carry; only `../` is refused outright.
        norm="${spec#file://}"
        norm="${norm#"$work/tree"/}"
        while [ "${norm#./}" != "$norm" ]; do norm="${norm#./}"; done
        case "$norm" in
          # Escapes the tree, or was never under it: no added file can correspond, and guessing would
          # be worse than refusing. Unattributable, so exit 2.
          /*|../*) ;;
          *)
            for path in "${added[@]}"; do
              case "$path" in
                "$norm"|*/"$norm"|"$norm".ts|*/"$norm".ts|"$norm".tsx|*/"$norm".tsx|\
                "$norm".js|*/"$norm".js|"$norm".mjs|*/"$norm".mjs)
                  hit=1; break ;;
              esac
            done ;;
        esac ;;
      *)
        # Dotted module: `api.limits` is `api/limits.py` or `api/limits/__init__.py`, in the root or
        # under one of this repository's source prefixes.
        cand="$(printf '%s' "$spec" | tr '.' '/')"
        for path in "${added[@]}"; do
          case "$path" in
            "$cand".py|"$cand"/__init__.py|src/"$cand".py|src/"$cand"/__init__.py|\
            lib/"$cand".py|lib/"$cand"/__init__.py|python/"$cand".py|python/"$cand"/__init__.py)
              hit=1; break ;;
          esac
        done
        # A namespace package has no `__init__.py`, so Python names only the top of the chain:
        # `import pkg.limits` reports `No module named 'pkg'`. That is still the change-set's own
        # module only if the directory did not exist at base — checked rather than assumed.
        if [ "$hit" -eq 0 ] && [ -z "$(git ls-tree -r --name-only "$BASE" -- "$cand" 2>/dev/null)" ]; then
          for path in "${added[@]}"; do
            case "$path" in
              "$cand"/*|src/"$cand"/*|lib/"$cand"/*|python/"$cand"/*) hit=1; break ;;
            esac
          done
        fi ;;
    esac
    # Every specifier must be attributable. Returning at the first match would let one added module
    # excuse an unrelated missing one in the same run, and `probe-test-cmd` runs the whole suite.
    if [ "$hit" -eq 0 ]; then
      echo "        the base tree could not import '$spec', and this change-set does not add it" >&2
      return 1
    fi
    echo "        '$spec' is added by this change-set" >&2
    matched=1
  done < <( { grep -aoE "No module named '[^']+'" "$work/out" | sed "s/^No module named '//; s/'\$//" || true
              grep -aoE "Cannot find module '[^']+'" "$work/out" | sed "s/^Cannot find module '//; s/'\$//" || true; } )
  [ "$matched" -eq 1 ]
}

# The screen applies only when the run produced **no test-level result** — a collection or import
# error, not an assertion failure. Two lanes, spelled differently, and the difference matters:
#
#   pytest  `1 failed, 4 passed in 0.1s`      — a count *is* the test-level result.
#   vitest  ` Test Files  1 failed (1)`       — file-level, and printed even when nothing ran,
#           `      Tests  no tests`             beside `Tests  no tests` (measured on vitest 4.1.12).
#
# A bare `[0-9]+ (passed|failed)` therefore treats a vitest import failure as an assertion failure,
# which is fail-open on exactly the lane `pnpm test` occupies. So: on the vitest lane only a count on
# the `Tests` line counts; elsewhere (pytest, and any runner that prints no such line) the count does.
# The verdict is the runner's **last** summary line, not any line in the file. Two reasons:
#
#   * `probe-test-cmd` here chains runners (`pnpm test && pytest tests/ -q`), so one log carries more
#     than one summary. Both runners in use print their summary last — pytest after its coverage
#     report, vitest's `Tests` line after `Test Files` — so the last one normally belongs to the runner
#     that decided the exit status.
#   * a failing test's traceback can quote harness text (this script's own tests provoke it), and a
#     screen that reads any line in the file cannot tell that from a run that never started.
#
# The assumption is "the deciding runner prints a summary", and it has a known hole: if the second
# runner dies without one (`INTERNALERROR`, OOM, a timeout), the first runner's green summary is still
# the last line and the run reads as a bite. That hole favours the change-set, so it is recorded here
# rather than papered over.
#
#   pytest  `9 failed, 5 passed in 4.40s`   test-level result
#           `1 error in 0.08s`             collection error, nothing ran
#   vitest  `Tests  1 failed (1)`           test-level result
#           `Tests  no tests`               file-level failure, nothing ran (measured on 4.1.12)
last_summary="$( { grep -aE '([0-9]+ (passed|failed|error|deselected)|Tests[[:space:]]+(no tests|[0-9]+)|no tests ran)' "$work/out" || true; } | tail -n1)"
ran=0
case "$last_summary" in
  *"no tests"*) ran=0 ;;
  *[0-9]*" passed"*|*[0-9]*" failed"*) ran=1 ;;
  *) ran=0 ;;
esac
# The guard also keeps this script's own test suite from being screened: its assertion messages quote
# `No module named 'pkg'`, and a run reporting `N failed` failed on an assertion regardless.
#
# A summary that reports *no* test-level result is proof nothing ran, whatever text came with it:
# pytest's `1 error in` can come from a fixture raising `RuntimeError`, whose name is not in HARNESS,
# and requiring that match as well let such a run reach `probe: ok`. A run that printed no summary at
# all still needs the text match, because a one-line runner is a shape this script supports.
if [ "$ran" -eq 0 ] && { [ -n "$last_summary" ] || grep -aqE "$HARNESS" "$work/out"; }; then
  if added_module_failure; then
    echo "probe: ok — the tests fail without the fix because they import a module this change-set adds (exit $status)"
    tail -5 "$work/out" | sed 's/^/        /'
    exit 0
  fi
  echo "probe: COULD NOT RUN — the failure is the harness, not an assertion" >&2
  # `|| true`: this grep is empty whenever the screen fired on a summary alone, and under `set -e`
  # its failure aborted the script with status 1 — which the caller reads as "the tests pass without
  # the fix", the opposite verdict.
  { grep -aE -m3 "$HARNESS" "$work/out" || true; } | sed 's/^/        /' >&2
  exit 2
fi

echo "probe: ok — the tests fail without the fix (exit $status)"
tail -5 "$work/out" | sed 's/^/        /'
