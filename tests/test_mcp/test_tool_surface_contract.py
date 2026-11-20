"""Every tool, method and parameter mapping in the surface must resolve.

The surface is data — `TOOLS` in `mcp_server/tool_surface.py` — and until this file existed nothing
exercised the mapping itself. A typo in a `module` or `function` string, or a mapped parameter the
library function does not take, shipped green: the tool was listed, and the call raised
`AttributeError` or `TypeError` at request time.

These are structural assertions over the same tables the server dispatches from, so they cannot pass
vacuously — and `test_the_surface_is_not_empty` fails if the tables stop looking like themselves.
"""

from __future__ import annotations

import importlib

import pytest

from mcp_server import tool_surface as ts


def _methods() -> list[tuple[str, dict]]:
    return [(tool["name"], method) for tool in ts.TOOLS for method in tool.get("methods", [])]


METHODS = _methods()
METHOD_IDS = [f"{tool}:{m['key']}" for tool, m in METHODS]


def test_the_surface_is_not_empty() -> None:
    # Not `len(TOOLS) == tool_count()` — tool_count() is len(TOOLS), so that comparison is a tautology
    # that cannot fail. These two can.
    assert ts.tool_count() > 0
    assert len(ts.TOOLS) == 14, f"expected 14 folded tools, found {len(ts.TOOLS)}"
    assert len(METHODS) >= 40, f"expected the folded surface, found {len(METHODS)} methods"


@pytest.mark.parametrize(("tool_name", "method"), METHODS, ids=METHOD_IDS)
def test_every_method_names_a_real_function(tool_name: str, method: dict) -> None:
    module = importlib.import_module(method["module"])
    func = getattr(module, method["function"], None)
    assert callable(func), f"{tool_name}/{method['key']}: {method['module']}.{method['function']} is not callable"


@pytest.mark.parametrize(("tool_name", "method"), METHODS, ids=METHOD_IDS)
def test_every_mapped_parameter_is_a_parameter_of_the_function(tool_name: str, method: dict) -> None:
    import inspect

    module = importlib.import_module(method["module"])
    func = getattr(module, method["function"])
    try:
        params = set(inspect.signature(func).parameters)
    except (TypeError, ValueError):  # pragma: no cover - builtins would land here
        pytest.skip(f"{tool_name}/{method['key']} has no inspectable signature")

    mapped = set(method.get("args", [])) | set(method.get("opt", []))
    unknown = mapped - params
    # A function that models its inputs as one object exposes that parameter instead of the fields.
    if len(params) == 1 and unknown:
        pytest.skip(f"{tool_name}/{method['key']} takes a model parameter: {sorted(params)}")
    assert unknown == set(), (
        f"{tool_name}/{method['key']} maps parameters {sorted(unknown)} that "
        f"{method['function']} does not take ({sorted(params)})"
    )


@pytest.mark.parametrize("tool", ts.TOOLS, ids=[t["name"] for t in ts.TOOLS])
def test_an_unknown_method_is_refused(tool: dict) -> None:
    with pytest.raises(ValueError, match="Unknown method"):
        ts.call_tool(tool["name"], {"method": "definitely_not_a_method"})


@pytest.mark.parametrize("tool", ts.TOOLS, ids=[t["name"] for t in ts.TOOLS])
def test_no_method_accepts_an_empty_call_silently(tool: dict) -> None:
    """Every method either computes with no arguments or refuses with the documented ValueError.

    All 50 methods declare at least one required parameter, so the refusal path is the one exercised —
    which is the point: the assertion is that the refusal is a `ValueError`, not an `AttributeError`,
    `TypeError` or `KeyError` from a broken mapping. Resolution and mapping are covered separately by
    the two parametrisations above; this one guards the message contract.
    """
    for method in tool.get("methods", []):
        try:
            ts.call_tool(tool["name"], {"method": method["key"]})
        except ValueError:
            continue  # the documented "requires parameter" / validation path
        except (AttributeError, TypeError, KeyError) as exc:  # pragma: no cover - the defect
            pytest.fail(f"{tool['name']}/{method['key']} raised {type(exc).__name__}: {exc}")


def test_goodwill_impairment_forwards_the_ias36_parameters() -> None:
    """The surface-side regression: `value_in_use` was absent from the `opt` map, so an IAS 36 call
    could only ever return the fair-value comparison. The structural tests pass with the mapping
    absent — this one does not."""
    result = ts.call_tool(
        "valuation_impairment",
        {
            "method": "goodwill_impairment",
            "carrying_value": 1_000,
            "fair_value": 800,
            "value_in_use": 1_200,
            "standard": "IAS36",
        },
    )
    assert result["value"] == 0.0
    assert result["assumptions"]["value_in_use"] == 1_200
