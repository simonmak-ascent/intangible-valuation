"""Behaviour of `scripts/probe.sh`, the script behind the mandatory `test / probe` CI job.

Written after PR #69 failed that job with:

    probe: COULD NOT RUN — the failure is the harness, not an assertion
    E   ModuleNotFoundError: No module named 'api.limits'

The probe ran a new test against the base tree, out of which the module it imports had not been
created yet, and read the import error as a broken harness. A test that adds a module therefore
could never pass the probe, which is a gate that blocks correct work instead of finding defects.

Each case below builds a throwaway git repository, so the probe executes its real code path rather
than a mock of it.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from pathlib import Path

PROBE = Path(__file__).resolve().parents[1] / "scripts" / "probe.sh"


def _run(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run("git init -q -b main", repo)
    _run("git config user.email probe@test.local", repo)
    _run("git config user.name probe", repo)
    (repo / "app.py").write_text("VALUE = 1\n")
    _run("git add -A && git commit -qm base", repo)
    return repo


def _probe(repo: Path, test_cmd: str) -> subprocess.CompletedProcess[str]:
    return _run(
        f"bash {shlex.quote(str(PROBE))} --repo . --base HEAD --test-cmd {shlex.quote(test_cmd)}",
        repo,
    )


def _diagnostics(result: subprocess.CompletedProcess[str]) -> str:
    """Failure message that does **not** reproduce the probe's output.

    `probe.sh` classifies a run by matching text in it, so an assertion message that echoes probe
    output is indistinguishable from a real import error — and these tests deliberately provoke those
    errors. Embedding the text made the probe refuse the change-set that adds these tests, twice.
    The output goes to a file and the message carries only the exit code and the path.
    """
    path = Path(tempfile.gettempdir()) / f"probe-output-{os.getpid()}.txt"
    path.write_text(result.stdout + result.stderr, encoding="utf-8")
    return f"probe exited {result.returncode}; full output at {path}"


def test_a_module_the_change_adds_is_the_expected_failure(tmp_path: Path) -> None:
    """The case that failed CI: new `pkg/limits.py` + a test importing it."""
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "limits.py").write_text("MAX = 10\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.py").write_text(
        "from pkg.limits import MAX\n\n\ndef test_max():\n    assert MAX == 10\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_limits.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "import a module this change-set adds" in result.stdout
    assert "'pkg' is added by this change-set" in output


def test_a_module_under_an_existing_package_is_attributed(tmp_path: Path) -> None:
    """The dotted path whose parent package already exists at base: `api/__init__.py` is there,
    `api/limits.py` is not, so Python names the full chain."""
    repo = _repo(tmp_path)
    (repo / "api").mkdir()
    (repo / "api" / "__init__.py").write_text("")
    _run("git add -A && git commit -qm api-package", repo)
    (repo / "api" / "limits.py").write_text("MAX = 10\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.py").write_text(
        "from api.limits import MAX\n\n\ndef test_max():\n    assert MAX == 10\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_limits.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "'api.limits' is added by this change-set" in output


def test_a_node_relative_import_of_an_added_module_is_attributed(tmp_path: Path) -> None:
    """`Cannot find module './limits'`.

    This branch produced **no specifiers at all** until the unguarded `grep | sed` was given
    `|| true`: a process substitution inherits `errexit` and `pipefail`, so the Python extractor
    matching nothing ended the group before the Node one ran. The runner here prints the message a
    bundler would, so the branch is exercised rather than assumed.
    """
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.ts").write_text("import { MAX } from '../lib/limits';\n")
    (repo / "tests" / "runner.py").write_text(
        "import sys\nsys.stderr.write(\"Error: Cannot find module './limits'\\n\")\nsys.exit(1)\n"
    )

    result = _probe(repo, "python3 tests/runner.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "'./limits' is added by this change-set" in output


def test_the_node_extractor_is_load_bearing(tmp_path: Path) -> None:
    """Mutation check: remove the `|| true` guards and the Node case must go red.

    The mutant differs from the current file only in those guards, so it isolates the bytes that
    carry the behaviour. A test that passes with the fix removed proves nothing.
    """
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "runner.py").write_text(
        "import sys\nsys.stderr.write(\"Error: Cannot find module './limits'\\n\")\nsys.exit(1)\n"
    )

    current = PROBE.read_text()

    def extractor(guard: str) -> str:
        return (
            '  done < <( { grep -aoE "No module named \'[^\']+\'" "$work/out" | sed "s/^No module named \'//; s/\'\\$//"'
            + guard
            + '\n              grep -aoE "Cannot find module \'[^\']+\'" "$work/out" | sed "s/^Cannot find module \'//; s/\'\\$//"'
            + guard
            + "; } )"
        )

    fixed = extractor(" || true")
    # The historically dead form: identical minus the `||` guards.
    broken = extractor("")
    assert fixed in current, "the extractor block moved; update this mutation check with it"
    mutant = tmp_path / "probe-old.sh"
    mutant.write_text(current.replace(fixed, broken))

    fixed_run = _run(
        f"bash {shlex.quote(str(PROBE))} --repo . --base HEAD --test-cmd 'python3 tests/runner.py'",
        repo,
    )
    mutant_run = _run(
        f"bash {shlex.quote(str(mutant))} --repo . --base HEAD --test-cmd 'python3 tests/runner.py'",
        repo,
    )

    assert fixed_run.returncode == 0, _diagnostics(fixed_run)
    # Exit 2 alone is not enough: bash also exits 2 on a syntax error, so a malformed mutant would
    # pass this check vacuously. The message is what proves the screening reached its own conclusion.
    assert mutant_run.returncode == 2, (
        "the guard-less extractors were expected to fail this case; if they pass, the "
        f"mutation check is no longer testing anything: {mutant_run.stdout}{mutant_run.stderr}"
    )
    assert "COULD NOT RUN" in mutant_run.stderr, _diagnostics(mutant_run)


def test_a_bundler_absolute_specifier_is_attributed(tmp_path: Path) -> None:
    """Vitest reports the *resolved* id, not the relative one: `Cannot find module 'file:///…'`.

    This repository's probe runs `pnpm test && pytest tests/`, so a real run produces that shape.
    Before normalisation it entered the dotted branch, became a meaningless candidate and the
    correct change-set failed the probe — the failure mode this whole change exists to remove.
    """
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "runner.py").write_text(
        "import os, sys\n"
        'sys.stderr.write("Error: Cannot find module \'file://" + os.getcwd() + "/lib/limits.ts\'\\n")\n'
        "sys.exit(1)\n"
    )

    result = _probe(repo, "python3 tests/runner.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "is added by this change-set" in output


def test_a_specifier_outside_the_tree_is_not_attributed(tmp_path: Path) -> None:
    """`../x` cannot be resolved without the importing file's path, and guessing would be worse than
    refusing: the probe says it could not run rather than inventing an attribution."""
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "runner.py").write_text(
        "import sys\nsys.stderr.write(\"Error: Cannot find module '../outside/thing'\\n\")\nsys.exit(1)\n"
    )

    result = _probe(repo, "python3 tests/runner.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "does not add it" in result.stderr


def test_an_assertion_quoting_a_module_error_still_counts_as_a_failure(tmp_path: Path) -> None:
    """A test whose assertion message quotes the harness text must not be read as a broken harness.

    This is the trap the screen set for this very file: the cases above embed `No module named 'pkg'`
    in their failure messages, and the probe's screen read that as "could not run" — so the probe
    refused the change-set that adds it. A run reporting `N failed` failed on an assertion.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_message.py").write_text(
        "def test_message():\n    raise AssertionError(\"boom: No module named 'definitely_absent'\")\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_message.py")

    assert result.returncode == 0, _diagnostics(result)
    assert "the tests fail without the fix" in result.stdout


def _vitest_import_failure(spec: str) -> str:
    """The summary vitest prints when a test file cannot import, measured on the pinned 4.1.12:

         Test Files  1 failed (1)
              Tests  no tests

    File-level failure, no test executed — so a guard that keys on `N failed` reads it as an
    assertion failure and the probe reports a bite that never happened.
    """
    return (
        "import sys\n"
        f"sys.stderr.write(\"Error: Cannot find module '{spec}'\\n\")\n"
        "sys.stderr.write(' Test Files  1 failed (1)\\n')\n"
        "sys.stderr.write('      Tests  no tests\\n')\n"
        "sys.exit(1)\n"
    )


def test_a_vitest_import_failure_is_screened_not_counted(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.ts").write_text("import './nowhere';\n")
    (repo / "tests" / "runner.py").write_text(_vitest_import_failure("./nowhere"))

    result = _probe(repo, "python3 tests/runner.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_a_vitest_import_failure_of_an_added_module_is_attributed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "lib").mkdir()
    (repo / "lib" / "limits.ts").write_text("export const MAX = 10;\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.ts").write_text("import './limits';\n")
    (repo / "tests" / "runner.py").write_text(_vitest_import_failure("./limits"))

    result = _probe(repo, "python3 tests/runner.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "'./limits' is added by this change-set" in output


def test_a_vitest_test_level_failure_counts_as_the_probe_biting(tmp_path: Path) -> None:
    """The other side of the lane predicate: `Tests  1 failed (1)` means a test executed.

    Without this case, the guard's `ran=1` branch on the vitest lane is never exercised, and a fix
    that simply screened every vitest run would pass the suite.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "runner.py").write_text(
        "import sys\n"
        "sys.stderr.write(\"AssertionError: expected 2, got 1 (Cannot find module './limits')\\n\")\n"
        "sys.stderr.write(' Test Files  1 failed (1)\\n')\n"
        "sys.stderr.write('      Tests  1 failed (1)\\n')\n"
        "sys.exit(1)\n"
    )

    result = _probe(repo, "python3 tests/runner.py")

    assert result.returncode == 0, _diagnostics(result)
    assert "the tests fail without the fix" in result.stdout


def test_a_passing_first_runner_does_not_answer_for_a_failing_second(tmp_path: Path) -> None:
    """The real `probe-test-cmd`: `pnpm test && pytest tests/ -q` — two runners, one log.

    vitest passes and writes `Tests  1 passed (1)`; pytest then aborts at collection on a module the
    change-set does not add. A predicate that asks "did any line report a test count" says yes, and
    the probe claims a bite that never happened. A pytest collection error decides on its own, because
    `&&` means nothing after it ran.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "green.py").write_text(
        "import sys\n"
        "sys.stderr.write(' Test Files  1 passed (1)\\n')\n"
        "sys.stderr.write('      Tests  1 passed (1)\\n')\n"
    )
    (repo / "tests" / "test_limits.py").write_text(
        "from absent_mod import THING\n\n\ndef test_thing():\n    assert THING\n"
    )

    result = _probe(
        repo,
        "python3 tests/green.py && python3 -m pytest -q tests/test_limits.py",
    )

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_a_passing_first_runner_does_not_hide_an_attributable_second(tmp_path: Path) -> None:
    """Same chain, but the module the second runner could not import is the change-set's own."""
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "limits.py").write_text("MAX = 10\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "green.py").write_text(
        "import sys\n"
        "sys.stderr.write(' Test Files  1 passed (1)\\n')\n"
        "sys.stderr.write('      Tests  1 passed (1)\\n')\n"
    )
    (repo / "tests" / "test_limits.py").write_text(
        "from pkg.limits import MAX\n\n\ndef test_max():\n    assert MAX == 10\n"
    )

    result = _probe(
        repo,
        "python3 tests/green.py && python3 -m pytest -q tests/test_limits.py",
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "is added by this change-set" in output


def test_a_renamed_module_is_attributed(tmp_path: Path) -> None:
    """A module this change-set *moves* is added under its new name.

    Git reports a rename as `R`, not `A`, so a filter of `A` alone leaves it unattributable and the
    probe refuses a test that genuinely needs the change — the failure this screen exists to remove,
    in a shape that has nothing to do with the base tree.
    """
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "old_limits.py").write_text("MAX = 10\n")
    _run("git add -A && git commit -qm old-name", repo)
    _run("git mv pkg/old_limits.py pkg/limits.py", repo)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.py").write_text(
        "from pkg.limits import MAX\n\n\ndef test_max():\n    assert MAX == 10\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_limits.py")

    output = result.stdout + result.stderr
    assert result.returncode == 0, _diagnostics(result)
    assert "is added by this change-set" in output


def test_a_test_that_does_not_compile_is_screened(tmp_path: Path) -> None:
    """A copied test with a syntax error runs nothing, so its non-zero exit is not evidence.

    `HARNESS` had no pattern for it: pytest reports `1 error in 0.05s`, which matches neither count,
    so the run reached `probe: ok` and claimed a bite that never happened.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_broken.py").write_text("def test_x(:\n    pass\n")

    result = _probe(repo, "python3 -m pytest -q tests/test_broken.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_a_collection_error_without_a_harness_token_is_screened(tmp_path: Path) -> None:
    """`1 error in 0.05s` from a module that raises on import, with no text `HARNESS` knows.

    Requiring the harness match as well as `ran=0` let this reach `probe: ok` — a bite claimed for a
    run in which no test executed.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_boom.py").write_text("raise RuntimeError('the valuation library is not importable')\n")

    result = _probe(repo, "python3 -m pytest -q tests/test_boom.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_a_run_that_selected_no_tests_is_screened(tmp_path: Path) -> None:
    """pytest exits 5 with `1 deselected in …`: nothing ran, so a non-zero exit is not evidence."""
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_one.py").write_text("def test_a():\n    assert True\n")

    result = _probe(repo, "python3 -m pytest -q tests/test_one.py -k nothing_matches_this")

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_a_passing_first_runner_does_not_survive_a_second_that_selected_nothing(
    tmp_path: Path,
) -> None:
    """vitest green, then pytest exits 5 with `no tests ran` — the decider printed a summary, it was
    simply not one the count recognised, so the first runner's green line was still the last match."""
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "green.py").write_text(
        "import sys\n"
        "sys.stderr.write(' Test Files  1 passed (1)\\n')\n"
        "sys.stderr.write('      Tests  1 passed (1)\\n')\n"
    )
    (repo / "tests" / "test_one.py").write_text("def test_a():\n    assert True\n")

    result = _probe(
        repo,
        "python3 tests/green.py && python3 -m pytest -q tests/test_one.py -k nothing_matches",
    )

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_one_unattributable_module_in_the_same_run_still_fails(tmp_path: Path) -> None:
    """The AND control: a run where one import is the change-set's own and another is not.

    The screen originally returned at the first attributable specifier, so one added module excused
    an unrelated missing one — and `probe-test-cmd` runs the whole suite.
    """
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "limits.py").write_text("MAX = 10\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_added.py").write_text(
        "from pkg.limits import MAX\n\n\ndef test_max():\n    assert MAX == 10\n"
    )
    (repo / "tests" / "test_broken.py").write_text(
        "from definitely_absent import THING\n\n\ndef test_thing():\n    assert THING\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_added.py tests/test_broken.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "does not add it" in result.stderr
    assert "definitely_absent" in result.stderr


def test_a_missing_module_the_change_does_not_add_is_still_a_harness_failure(
    tmp_path: Path,
) -> None:
    """The control for the case above: screening must not swallow every import error.

    Without this, `added_module_failure` would be indistinguishable from `|| exit 0` and the probe
    would stop detecting a genuinely broken base tree.
    """
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "limits.py").write_text("MAX = 10\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_limits.py").write_text(
        "from app.notthere import THING\n\n\ndef test_thing():\n    assert THING\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_limits.py")

    assert result.returncode == 2, _diagnostics(result)
    assert "COULD NOT RUN" in result.stderr


def test_an_assertion_failure_still_counts_as_the_probe_biting(tmp_path: Path) -> None:
    """The ordinary case must keep working: the test asserts the fix's new behaviour."""
    repo = _repo(tmp_path)
    (repo / "app.py").write_text("VALUE = 2\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_value.py").write_text(
        "from app import VALUE\n\n\ndef test_value():\n    assert VALUE == 2\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_value.py")

    assert result.returncode == 0, _diagnostics(result)
    assert "the tests fail without the fix" in result.stdout


def test_a_green_test_in_the_base_tree_is_rejected(tmp_path: Path) -> None:
    """A test that passes without the change proves nothing, and the probe must say so."""
    repo = _repo(tmp_path)
    (repo / "app.py").write_text("VALUE = 1\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_value.py").write_text(
        "from app import VALUE\n\n\ndef test_value():\n    assert VALUE == 1\n"
    )

    result = _probe(repo, "python3 -m pytest -q tests/test_value.py")

    assert result.returncode == 1, _diagnostics(result)
    assert "pass without the fix" in result.stderr
