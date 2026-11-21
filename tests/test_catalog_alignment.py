"""The site's catalog and the MCP tool surface must describe the same call paths.

`lib/valuation/catalog.ts` is what the docs page renders; `mcp_server/tool_surface.py` is what MCP
actually dispatches. They drifted once: every entry carried `mcpTool`, which held the slug in
snake_case rather than a tool, and the page rendered it as callable. Of those 68 values, 24 were real
method selectors presented as tool names, 23 were Python function names no tool accepts as a
`method:` value, and 21 led nowhere — the API-only set this test pins. For a path the catalog gives
an MCP declaration it fails if either side moves alone: wrong tool, wrong method set, a module move,
or a function gaining or losing an MCP path. For an API-only entry it checks that the declared
function resolves and that no surface method dispatches it, which catches a rename but not a
re-pointing to another function that also exists. A surface method no catalog entry mentions is
invisible here; `test_surface_methods_absent_from_catalog_are_known` pins the two that exist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mcp_server import tool_surface

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "lib" / "valuation" / "catalog.ts"

ENTRY = re.compile(
    r'slug:\s*"(?P<slug>[^"]+)".*?mcp:\s*(?P<mcp>null|\{[^}]*\}).*?pythonFunction:\s*"(?P<py>[^"]+)"',
    re.S,
)
MCP = re.compile(r'tool:\s*"(?P<tool>[^"]+)",\s*methods:\s*\[(?P<methods>[^\]]*)\]')

# module.function -> [(tool, method)] for everything MCP can dispatch. Keyed on the full dotted
# path rather than the leaf: `call_tool` resolves `method["module"]` and `method["function"]`
# (`mcp_server/tool_surface.py:1443`, `:1523`), so a leaf key would stay green if a dispatcher
# moved to another module while the catalog's `pythonFunction` did not.
SURFACE: dict[str, list[tuple[str, str]]] = {}
for _tool in tool_surface.TOOLS:
    for _m in _tool.get("methods", []):
        SURFACE.setdefault(f"{_m['module']}.{_m['function']}", []).append((_tool["name"], _m["key"]))


def entries() -> list[tuple[str, str | None, str]]:
    return [
        (m["slug"], m["mcp"], m["py"])
        for m in ENTRY.finditer(CATALOG.read_text())
    ]


def test_every_catalog_entry_is_parsed() -> None:
    # 68 methods; a parse failure here would make the checks below pass vacuously.
    assert len(entries()) == 68


@pytest.mark.parametrize("slug,mcp,python_function", entries())
def test_declared_mcp_path_dispatches_to_the_same_function(
    slug: str, mcp: str, python_function: str
) -> None:
    hits = SURFACE.get(python_function, [])

    if mcp == "null":
        assert not hits, f"{slug}: declared API-only, but MCP dispatches {hits}"
        return

    parsed = MCP.search(mcp)
    assert parsed, f"{slug}: unparseable mcp declaration {mcp!r}"
    tool, methods = parsed["tool"], [m.strip().strip('"') for m in parsed["methods"].split(",")]

    declared_tools = {t for t, _ in hits}
    assert tool in declared_tools, f"{slug}: {tool} does not dispatch {python_function} (real: {declared_tools})"
    real_methods = {k for _, k in hits}
    for method in methods:
        assert method in real_methods, f"{slug}: {tool} has no method {method} (real: {real_methods})"
    assert set(methods) == real_methods, (
        f"{slug}: declares {methods} for {python_function}, MCP exposes {sorted(real_methods)}"
    )


def test_every_declared_python_function_resolves() -> None:
    """A catalog entry naming a function that does not exist would be unrunnable documentation.

    The `mcp: null` branch above only proves that no surface method hits the path; this proves the
    path itself is real, so a rename on the catalog side fails here.
    """
    import importlib

    missing: list[str] = []
    for slug, _mcp, python_function in entries():
        module_name, _, attribute = python_function.rpartition(".")
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001 - the report wants the message
            missing.append(f"{slug}: {module_name} ({exc.__class__.__name__})")
            continue
        if not hasattr(module, attribute):
            missing.append(f"{slug}: {python_function} does not exist")

    assert not missing, missing


def test_surface_methods_absent_from_catalog_are_known() -> None:
    """Pins the coverage gap: surface methods with no catalog entry, so the count cannot go stale."""
    mentioned = {python_function for _, _, python_function in entries()}
    assert {key for key in SURFACE if key not in mentioned} == {
        "intangible_valuation.utils.formulas.estimate_useful_life",
        "intangible_valuation.utils.formulas.sensitivity_analysis",
    }
