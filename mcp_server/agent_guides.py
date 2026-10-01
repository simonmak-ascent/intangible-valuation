"""MCP prompts and resources for the Intangible Asset Valuation server.

Shared by the stdio FastMCP server and the hosted Streamable HTTP endpoint so both
advertise the same agent-facing surface:

* **Resources** expose the method catalog (every tool, method key, and its required
  and optional parameters) so an agent can plan a calculation without trial calls.
* **Prompts** are guided, multi-step valuation workflows. Each step names the exact
  tool and ``method`` to call; the required/optional parameter lists are generated
  from the canonical tool surface, so the prompts cannot drift from the tools.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

try:  # run from the repo root
    from mcp_server.tool_surface import SERVER_NAME, SERVER_VERSION, TOOLS
except ImportError:  # installed as a top-level module (pip install intangible-valuation-mcp)
    from tool_surface import SERVER_NAME, SERVER_VERSION, TOOLS  # type: ignore[no-redef,import-not-found]

URI_SCHEME = "intangible-valuation"
CATALOG_URI = f"{URI_SCHEME}://methods"


# --------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------


def _method_entry(method: dict[str, Any]) -> dict[str, Any]:
    return {
        "method": method["key"],
        "label": method.get("label", method["key"]),
        "summary": method.get("summary", ""),
        "required": list(method.get("args", {}).values()),
        "optional": list(method.get("opt", {}).values()),
    }


def _tool_entry(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": tool["name"],
        "title": tool["title"],
        "methods": [_method_entry(m) for m in tool["methods"]],
    }


def method_catalog() -> dict[str, Any]:
    """Every tool and method with its parameters, as one JSON document."""
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "tools": [_tool_entry(t) for t in TOOLS],
    }


def list_resources() -> list[dict[str, Any]]:
    resources = [
        {
            "uri": CATALOG_URI,
            "name": "method-catalog",
            "title": "Method catalog",
            "description": "Every tool, method key, and its required and optional parameters.",
            "mimeType": "application/json",
        }
    ]
    for tool in TOOLS:
        resources.append(
            {
                "uri": f"{CATALOG_URI}/{tool['name']}",
                "name": f"methods-{tool['name']}",
                "title": f"{tool['title']} methods",
                "description": f"Methods and parameters of {tool['name']}.",
                "mimeType": "application/json",
            }
        )
    return resources


def read_resource(uri: str) -> dict[str, Any]:
    """Return an MCP ``resources/read`` result. Raises ValueError for unknown URIs."""
    if uri == CATALOG_URI:
        payload: dict[str, Any] = method_catalog()
    else:
        prefix = f"{CATALOG_URI}/"
        tool = next((t for t in TOOLS if uri == prefix + t["name"]), None)
        if tool is None:
            raise ValueError(f"Unknown resource: {uri}")
        payload = _tool_entry(tool)
    return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(payload, indent=2)}]}


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------


def _method_spec(tool_name: str, method_key: str) -> dict[str, Any]:
    tool = next(t for t in TOOLS if t["name"] == tool_name)
    return next(m for m in tool["methods"] if m["key"] == method_key)


def _render_steps(steps: list[tuple[str, str, str]]) -> str:
    lines = []
    for i, (purpose, tool_name, method_key) in enumerate(steps, start=1):
        spec = _method_spec(tool_name, method_key)
        required = ", ".join(spec.get("args", {}).values()) or "none"
        optional = ", ".join(spec.get("opt", {}).values())
        line = f"{i}. {purpose}: call `{tool_name}` with method=`{method_key}` (required: {required}"
        line += f"; optional: {optional})." if optional else ")."
        lines.append(line)
    return "\n".join(lines)


def _build(intro: str, steps: list[tuple[str, str, str]], outro: str) -> str:
    return (
        f"{intro}\n\n"
        "Use only explicit inputs. If an input the method requires is missing, ask the user for it "
        "instead of inventing a number. Rates are decimals (0.10 = 10%).\n\n"
        f"{_render_steps(steps)}\n\n{outro}\n\n"
        "Finish with a table of each method used, its value, key inputs and assumptions, and cite the "
        "formula reference returned by each result."
    )


PROMPTS: list[dict[str, Any]] = [
    {
        "name": "purchase_price_allocation",
        "title": "Purchase price allocation",
        "description": "Allocate an acquisition price to identifiable intangibles and goodwill (ASC 805 / IFRS 3).",
        "arguments": [
            {
                "name": "deal",
                "description": "Target, purchase price, tangible net assets and the intangibles to value.",
                "required": True,
            },
        ],
        "build": lambda a: _build(
            f"Prepare a purchase price allocation for: {a.get('deal', '')}.",
            [
                ("Discount rate for the intangibles (build-up)", "valuation_discount_rate", "build_up"),
                (
                    "Contributory asset charges for the excess-earnings method",
                    "valuation_income_methods",
                    "contributory_asset_charges",
                ),
                ("Customer relationships by multi-period excess earnings", "valuation_income_methods", "mpeem"),
                ("Trade name or technology by relief from royalty", "valuation_income_methods", "relief_from_royalty"),
                (
                    "Assembled workforce, used as a contributory asset only",
                    "valuation_human_capital",
                    "assembled_workforce",
                ),
                ("Tax amortization benefit on each intangible", "valuation_discount_rate", "tax_amortization_benefit"),
                ("Allocate the price and derive goodwill", "valuation_goodwill_ppa", "purchase_price_allocation"),
                ("Useful life of each finite-lived intangible", "valuation_goodwill_ppa", "useful_life"),
            ],
            "The assembled workforce is not recognised separately under ASC 805 / IFRS 3; it is a contributory asset "
            "and is subsumed in goodwill.",
        ),
    },
    {
        "name": "value_ip_asset",
        "title": "Value an IP asset",
        "description": "Value a patent, trademark, copyright or trade secret, with royalty support and a cost cross-check.",
        "arguments": [
            {
                "name": "asset",
                "description": "The IP asset, its revenues, remaining life and any licence comparables.",
                "required": True,
            },
            {"name": "asset_type", "description": "patent, trademark, copyright or trade_secret.", "required": False},
        ],
        "build": lambda a: _build(
            f"Value this intellectual property: {a.get('asset', '')}"
            + (f" (type: {a['asset_type']})" if a.get("asset_type") else "")
            + ".",
            [
                ("Benchmark a royalty range", "valuation_royalty_analysis", "benchmark"),
                ("Adjust the royalty for deal factors", "valuation_royalty_analysis", "adjust"),
                ("Relief-from-royalty value", "valuation_income_methods", "relief_from_royalty"),
                (
                    "Asset-specific method for a patent (use trademark, copyright or trade_secret as fits)",
                    "valuation_ip",
                    "patent",
                ),
                ("Cost-approach cross-check", "valuation_cost_approach", "reproduction_cost"),
                ("Monte Carlo range on the key drivers", "valuation_simulation", "monte_carlo"),
            ],
            "Reconcile the income, asset-specific and cost indications and state the concluded value.",
        ),
    },
    {
        "name": "impairment_test",
        "title": "Impairment test",
        "description": "Test goodwill or an intangible for impairment under ASC 350 or IAS 36, with sensitivity.",
        "arguments": [
            {
                "name": "asset",
                "description": "Reporting unit or asset, carrying value, and the cash-flow forecast.",
                "required": True,
            },
            {
                "name": "standard",
                "description": "Accounting standard, for example ASC 350 or IAS 36.",
                "required": False,
            },
        ],
        "build": lambda a: _build(
            f"Run an impairment test for: {a.get('asset', '')}"
            + (f" under {a['standard']}" if a.get("standard") else "")
            + ".",
            [
                ("Discount rate", "valuation_discount_rate", "wacc"),
                ("Terminal value of the forecast", "valuation_time_value", "terminal_value_gordon_growth"),
                ("Goodwill impairment", "valuation_impairment", "goodwill_impairment"),
                ("Intangible impairment (for a single asset)", "valuation_impairment", "intangible_impairment"),
            ],
            "State the headroom or impairment charge and which assumptions it is most sensitive to.",
        ),
    },
]


def list_prompts() -> list[dict[str, Any]]:
    return [
        {
            "name": p["name"],
            "title": p["title"],
            "description": p["description"],
            "arguments": p["arguments"],
        }
        for p in PROMPTS
    ]


def get_prompt(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return an MCP ``prompts/get`` result. Raises ValueError for unknown prompts."""
    prompt = next((p for p in PROMPTS if p["name"] == name), None)
    if prompt is None:
        raise ValueError(f"Unknown prompt: {name}")
    args = arguments or {}
    for arg in prompt["arguments"]:
        if arg.get("required") and not args.get(arg["name"]):
            raise ValueError(f"prompt '{name}' requires argument '{arg['name']}'")
    builder: Callable[[dict[str, Any]], str] = prompt["build"]
    return {
        "description": prompt["description"],
        "messages": [{"role": "user", "content": {"type": "text", "text": builder(args)}}],
    }


# --------------------------------------------------------------------------
# FastMCP registration (stdio server)
# --------------------------------------------------------------------------


def register(mcp: Any) -> None:
    """Register the resources and prompts on a FastMCP server."""

    @mcp.resource(CATALOG_URI, name="method-catalog", mime_type="application/json")
    def _catalog() -> str:
        return str(read_resource(CATALOG_URI)["contents"][0]["text"])

    for tool in TOOLS:
        uri = f"{CATALOG_URI}/{tool['name']}"

        def _make(u: str) -> Callable[[], str]:
            def _read() -> str:
                return str(read_resource(u)["contents"][0]["text"])

            return _read

        mcp.resource(uri, name=f"methods-{tool['name']}", mime_type="application/json")(_make(uri))

    for prompt in PROMPTS:
        arg_names = [a["name"] for a in prompt["arguments"]]

        def _make_prompt(p: dict[str, Any], names: list[str]) -> Callable[..., str]:
            # FastMCP derives prompt arguments from a real signature, so build one with
            # explicit keyword parameters (required ones have no default).
            required = {a["name"] for a in p["arguments"] if a.get("required")}
            sig = ", ".join((f"{n}: str" if n in required else f"{n}: str = ''") for n in names)
            body = ", ".join(f"{n!r}: {n}" for n in names)
            namespace: dict[str, Any] = {"_render": lambda kw: get_prompt(p["name"], kw)}
            exec(  # noqa: S102 — names come from the static PROMPTS table above
                f"def {p['name']}({sig}) -> str:\n"
                f"    return str(_render({{{body}}})['messages'][0]['content']['text'])\n",
                namespace,
            )
            fn: Callable[..., str] = namespace[p["name"]]
            return fn

        mcp.prompt(name=prompt["name"], title=prompt["title"], description=prompt["description"])(
            _make_prompt(prompt, arg_names)
        )
