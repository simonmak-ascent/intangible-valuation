"""The probe's contract, asserted without a socket.

`rollout.sh` requires exactly 200 on `HEALTH_PATH` before it replaces a live container, and it
restores the previous container when the probe fails. So this response is the gate that decides
whether a broken build reaches production, and it is worth a test for the same reason the error
contract is: a check never observed failing is unproven.
"""

from __future__ import annotations

import pytest

from api.index import ROUTES, health_response, is_health_path


def test_healthy_answers_200_with_the_route_count() -> None:
    code, body = health_response({"present-value": object(), "capm": object()})

    assert code == 200
    assert body == {"status": "ok", "methods": 2}


def test_an_empty_surface_answers_503_not_200() -> None:
    # The arm that makes the probe a gate rather than a liveness ping.
    code, body = health_response({})

    assert code == 503
    assert body["status"] == "degraded"
    assert "no routes" in body["reason"]


def test_the_live_table_is_the_library_surface() -> None:
    code, body = health_response()

    assert code == 200
    assert body["methods"] == len(ROUTES) == 68


@pytest.mark.parametrize("path", ["/health", "/api/health", "/api/health/"])
def test_the_handler_routes_every_health_spelling(path: str) -> None:
    # Asserted against the predicate the handler calls, not a copy of its expression: a copy cannot
    # fail when the handler changes, and this module's own docstring argues against such a check.
    assert is_health_path(path)


@pytest.mark.parametrize("path", ["/", "/healthz", "/api/health/x", "/api/healthx"])
def test_a_lookalike_path_is_not_a_health_route(path: str) -> None:
    # The catch-all branch answers 200 for any path, so a lookalike that wrongly matched here would
    # be indistinguishable from a healthy service.
    assert not is_health_path(path)
