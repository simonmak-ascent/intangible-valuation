"""The probe's contract, asserted without a socket.

`rollout.sh` requires exactly 200 on `HEALTH_PATH` before it replaces a live container, and it
restores the previous container when the probe fails. So this response is the gate that decides
whether a broken build reaches production, and it is worth a test for the same reason the error
contract is: a check never observed failing is unproven.
"""

from __future__ import annotations

import pytest

from api.index import ROUTES, health_response, is_health_path


@pytest.fixture(autouse=True)
def _no_ambient_digest(monkeypatch: pytest.MonkeyPatch) -> None:
    """`health_response` reports `IMAGE_DIGEST` when it is set, so an exact-body assertion must not
    inherit one from whatever launched the suite — a container run, or an operator's shell."""
    monkeypatch.delenv("IMAGE_DIGEST", raising=False)


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


def test_the_digest_is_reported_when_the_container_sets_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """A fleet check reads this instead of `docker inspect` on three hosts.

    `rollout.sh` passes `-e IMAGE_DIGEST=$DIGEST`, so every deployed container answers with the digest
    it is running. Omitted when unset: a bare `docker run` has no digest to name, and reporting `null`
    would look like an unknown digest rather than an absent one.
    """
    monkeypatch.setenv("IMAGE_DIGEST", "sha256:" + "ab" * 32)
    code, body = health_response({"present-value": object()})

    assert code == 200
    assert body == {"status": "ok", "methods": 1, "digest": "sha256:" + "ab" * 32}


def test_the_digest_is_absent_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMAGE_DIGEST", raising=False)
    code, body = health_response({"present-value": object()})

    assert code == 200
    assert "digest" not in body


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
