"""The two error contracts, and the DLOM limit, are pinned here.

Each of these was a live defect with no test:

* `dlom_finnerty` divided by `r*t`, so `risk_free_rate=0` raised `ZeroDivisionError` — a legitimate
  input, answered by `/api/*` as a 400 and by MCP as `-32603`. The fix evaluates the limit; without a
  test the branch could be dropped again and the failure would be *less* diagnosable than before,
  because the handler now answers a generic message.
* `api/index.py` returned `str(e)`, leaking pydantic `ValidationError` text and Python `TypeError`
  strings. Binding is now checked before the call, so the two cases are distinguishable — and this
  file pins both responses.
"""

from __future__ import annotations

import pytest

from api.index import ROUTES, calculate_response
from intangible_valuation.core.discount_rates import dlom_finnerty


class TestDlomAtZeroRiskFreeRate:
    def test_zero_rate_is_the_finite_limit(self) -> None:
        # limit = 2*Phi(sigma*sqrt(t)/2) - 1 for sigma=0.35, t=2
        result = dlom_finnerty(restricted_period=2.0, volatility=0.35, risk_free_rate=0.0)
        assert result.value == pytest.approx(0.195469, abs=1e-6)

    def test_a_rate_just_outside_the_guard_is_continuous(self) -> None:
        # 1e-8 is OUTSIDE the 1e-12 guard, so this is the closed form and not the limit branch —
        # 1e-15 would be inside it and would compare the limit with itself. The result is rounded to
        # six decimals, so the tolerance is bounded by that grid, not by the arithmetic.
        zero = dlom_finnerty(restricted_period=2.0, volatility=0.35, risk_free_rate=0.0).value
        tiny = dlom_finnerty(restricted_period=2.0, volatility=0.35, risk_free_rate=1e-8).value
        assert tiny == pytest.approx(zero, abs=1e-6)

    def test_a_normal_rate_is_unchanged(self) -> None:
        result = dlom_finnerty(restricted_period=2.0, volatility=0.35, risk_free_rate=0.04)
        assert result.value == pytest.approx(0.17894, abs=1e-5)


class TestCalculationResponses:
    def test_a_valid_call_answers_200_with_the_value(self) -> None:
        code, body = calculate_response(
            ROUTES["present-value"],
            {"future_value": 100_000, "discount_rate": 0.1, "periods": 5},
        )
        assert code == 200
        assert body["value"] == pytest.approx(62_092.13)

    def test_a_wrong_parameter_name_lists_the_expected_ones(self) -> None:
        code, body = calculate_response(ROUTES["present-value"], {"future_val": 1})
        assert code == 400
        assert body["error"] == "Invalid parameters"
        assert body["expected_params"] == ["future_value", "discount_rate", "periods"]

    def test_a_bad_value_reports_a_reference_and_leaks_nothing(self) -> None:
        # The old handler returned str(e) here: "2 validation errors for TVMInputs …".
        code, body = calculate_response(
            ROUTES["present-value"],
            {"future_value": "abc", "discount_rate": 0.1, "periods": 5},
        )
        assert code == 400
        assert body["error"] == "Calculation failed"
        assert len(body["reference"]) == 12
        assert "validation error" not in str(body).lower()
        assert "TVMInputs" not in str(body)
