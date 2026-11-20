"""The MCP arm's error contract.

`api/index.py` has had this pinned since #62. The MCP arm did not, and it is the arm that was live
with the leak: `except ValueError` catches pydantic's `ValidationError` too (it subclasses
`ValueError`), so `str(exc)` returned `TVMInputs`, the field name and `input_value=…` to the caller.
Reordering those `except` clauses again would restore it with a green suite — which is why this file
exists rather than a comment saying it must not.
"""

from __future__ import annotations

import pytest

from api import mcp
from intangible_valuation.core.time_value import present_value


def _validation_error() -> Exception:
    """A real pydantic `ValidationError` from the engine, not a hand-built stub."""
    with pytest.raises(Exception) as caught:
        present_value(future_value=1, discount_rate=11.0, periods=5)
    return caught.value


def _tools_call(monkeypatch: pytest.MonkeyPatch, raises: Exception) -> str:
    def boom(_name: str, _args: dict) -> dict:
        raise raises

    monkeypatch.setattr(mcp, "call_tool", boom)
    _code, _headers, body = mcp.handle_request(
        "POST",
        "/",
        '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"x","arguments":{}}}',
    )
    return body.decode()


def test_a_validation_error_reports_a_reference_and_leaks_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _tools_call(monkeypatch, _validation_error())

    assert "Invalid parameters (reference " in payload
    # `-32602`, not `-32603`: the caller's arguments are at fault, and the code is what tells an agent
    # client that retrying the same request is pointless.
    assert "-32602" in payload
    # The three things the old `str(exc)` disclosed.
    assert "TVMInputs" not in payload
    assert "input_value" not in payload
    assert "discount_rate" not in payload


def test_a_plain_value_error_still_names_the_problem(monkeypatch: pytest.MonkeyPatch) -> None:
    # `call_tool`'s own refusals are plain `ValueError` and their text is the client's own input —
    # that is what makes them actionable, so they must survive.
    payload = _tools_call(monkeypatch, ValueError("Unknown method 'nope' for tool 'x'"))

    assert "Unknown method 'nope'" in payload
    assert "-32602" in payload


def test_the_reference_is_a_fresh_twelve_hex_id(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _tools_call(monkeypatch, _validation_error())
    second = _tools_call(monkeypatch, _validation_error())

    def ref(payload: str) -> str:
        return payload.split("reference ")[1].partition(")")[0]

    assert len(ref(first)) == 12
    assert ref(first) != ref(second)
