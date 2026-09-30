"""Tests for the folded MCP server surface and tool discovery."""

from __future__ import annotations

import asyncio

import pytest

from mcp_server.server import mcp
from mcp_server.tool_surface import call_tool, list_tools, tool_count

EXPECTED_TOOLS = {
    "valuation_time_value",
    "valuation_discount_rate",
    "valuation_cost_approach",
    "valuation_market_approach",
    "valuation_income_methods",
    "valuation_ip",
    "valuation_technology",
    "valuation_customer",
    "valuation_human_capital",
    "valuation_goodwill_ppa",
    "valuation_impairment",
    "valuation_royalty_analysis",
    "valuation_simulation",
    "valuation_compliance",
}


def _registered_tool_names() -> set[str]:
    """Get set of registered tool names from the stdio server."""
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


class TestServerToolDiscovery:
    """Test that the MCP server exposes the folded family surface."""

    def test_server_has_name(self):
        assert mcp.name == "intangible-valuation"

    def test_exactly_folded_tools_registered(self):
        assert _registered_tool_names() == EXPECTED_TOOLS

    def test_tool_count_in_glama_band(self):
        # Glama scores Tool Count Appropriateness 5/5 only in the 3-15 band.
        assert 3 <= tool_count() <= 15
        assert tool_count() == len(EXPECTED_TOOLS)

    def test_every_tool_has_description_schema_and_annotations(self):
        for tool in list_tools():
            assert tool["description"], f"Tool '{tool['name']}' has no description"
            assert tool["title"]
            assert tool["tags"]
            assert tool["inputSchema"]["required"] == ["method"]
            assert tool["outputSchema"]["required"] == ["value"]
            assert tool["annotations"]["readOnlyHint"] is True
            assert tool["annotations"]["destructiveHint"] is False

    def test_descriptions_carry_tdqs_signals(self):
        for tool in list_tools():
            desc = tool["description"]
            assert "Method selects the formula" in desc
            assert "leave the rest unset" in desc
            assert "returns an error instead of a value" in desc
            assert "side-effect-free" in desc

    def test_every_parameter_is_documented(self):
        for tool in list_tools():
            for name, spec in tool["inputSchema"]["properties"].items():
                assert spec.get("description"), f"{tool['name']}.{name} missing description"

    def test_parameter_names_are_unique_across_tool(self):
        for tool in list_tools():
            props = tool["inputSchema"]["properties"]
            assert len(props) == len(set(props))


class TestDispatch:
    """Test canonical dispatch: method routing, errors, and serialization."""

    def test_call_present_value(self):
        result = call_tool(
            "valuation_time_value",
            {"method": "present_value", "future_value": 500_000, "discount_rate": 0.10, "periods": 8},
        )
        assert result["value"] == pytest.approx(233_253.69)
        assert "Present Value" in result["method"]

    def test_call_relief_from_royalty(self):
        result = call_tool(
            "valuation_income_methods",
            {
                "method": "relief_from_royalty",
                "revenue_projections": [1_000_000] * 5,
                "royalty_rate": 0.05,
                "discount_rate": 0.12,
                "tax_rate": 0.25,
                "useful_life": 5,
            },
        )
        assert result["value"] > 0

    def test_terminal_value_exit_multiple(self):
        result = call_tool(
            "valuation_time_value",
            {"method": "terminal_value_exit_multiple", "final_year_cashflow": 100_000, "exit_multiple": 8.0},
        )
        assert result["value"] == pytest.approx(800_000)

    def test_trademark_brand_method_routing(self):
        result = call_tool(
            "valuation_ip",
            {
                "method": "trademark",
                "revenue": 5_000_000,
                "profit_margin": 0.25,
                "brand_strength_index": 75,
                "discount_rate": 0.12,
                "useful_life": 10,
                "brand_method": "excess_earnings",
            },
        )
        assert result["value"] > 0

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            call_tool("valuation_time_value", {"method": "not_a_method"})

    def test_missing_required_param_raises(self):
        with pytest.raises(ValueError, match="requires parameter"):
            call_tool("valuation_income_methods", {"method": "relief_from_royalty", "royalty_rate": 0.05})

    def test_unknown_tool_raises(self):
        with pytest.raises(ValueError, match="Tool not found"):
            call_tool("not_a_tool", {"method": "present_value"})

    def test_monte_carlo_serializes_numpy(self):
        result = call_tool(
            "valuation_simulation",
            {
                "method": "monte_carlo",
                "input_distributions": [{"name": "a", "distribution": "normal", "params": {"mean": 1.0, "std": 0.1}}],
                "iterations": 1000,
                "seed": 7,
            },
        )
        assert isinstance(result["value"], (int, float))


class TestProtocolStructuredOutput:
    """Regression: structured output must satisfy the declared outputSchema.

    The shared ``OUTPUT_SCHEMA`` previously declared ``steps`` as an array of
    objects while results carry ``list[str]``, so every protocol-level
    ``tools/call`` (e.g. on Glama) failed with
    "Structured content does not match the tool's output schema".
    """

    @staticmethod
    def _call(name: str, args: dict):
        from fastmcp import Client

        async def run():
            async with Client(mcp) as client:
                return await client.call_tool(name, args)

        return asyncio.run(run())

    @staticmethod
    def _data(result):
        return getattr(result, "structured_content", None) or getattr(result, "data", None)

    def test_time_value_validates_against_output_schema(self):
        from mcp_server.tool_surface import OUTPUT_SCHEMA

        result = self._call(
            "valuation_time_value",
            {"method": "present_value", "future_value": 500_000, "discount_rate": 0.10, "periods": 8},
        )
        data = self._data(result)
        assert data is not None
        assert data["value"] == pytest.approx(233_253.69)
        assert isinstance(data["steps"], list)
        assert all(isinstance(step, str) for step in data["steps"])

        jsonschema = pytest.importorskip("jsonschema")
        jsonschema.validate(instance=data, schema=OUTPUT_SCHEMA)

    def test_simulation_validates_against_output_schema(self):
        from mcp_server.tool_surface import OUTPUT_SCHEMA

        result = self._call(
            "valuation_simulation",
            {
                "method": "monte_carlo",
                "input_distributions": [{"name": "a", "distribution": "normal", "params": {"mean": 1.0, "std": 0.1}}],
                "iterations": 1000,
                "seed": 7,
            },
        )
        data = self._data(result)
        assert data is not None
        assert isinstance(data["value"], (int, float))

        jsonschema = pytest.importorskip("jsonschema")
        jsonschema.validate(instance=data, schema=OUTPUT_SCHEMA)


class TestServerImport:
    """Test that server module imports correctly."""

    def test_server_import(self):
        from mcp_server import server

        assert hasattr(server, "mcp")
        assert hasattr(server, "main")
