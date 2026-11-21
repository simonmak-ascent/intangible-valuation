"""Tests for market approach valuation methods."""

import pytest

from intangible_valuation.approaches.market_approach import market_approach_comparables, royalty_capitalization


class TestMarketApproachComparables:
    """Tests for market_approach_comparables function."""

    def test_basic_comparables(self):
        """Basic comparable transactions without adjustments."""
        comps = [
            {"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"},
            {"sale_price": 8000000, "revenue": 3000000, "asset_type": "trademark"},
            {"sale_price": 12000000, "revenue": 4000000, "asset_type": "trademark"},
        ]
        result = market_approach_comparables(comps, subject_revenue=2500000)
        assert result["value"] == pytest.approx(6666666.67, rel=1e-4)
        assert result["range"] == pytest.approx((6250000.0, 7500000.0), rel=1e-4)

    def test_with_adjustments(self):
        """Adjustments should modify implied values."""
        comps = [
            {"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"},
            {"sale_price": 8000000, "revenue": 3000000, "asset_type": "trademark"},
        ]
        result = market_approach_comparables(
            comps, subject_revenue=2500000, adjustments={0: 0.10}
        )
        assert result["multiples"][0]["adjustment"] == 0.10

    def test_empty_comparables_raises(self):
        """Empty comparables list should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            market_approach_comparables([], subject_revenue=1000000)

    def test_negative_revenue_raises(self):
        """Non-positive subject_revenue should raise ValueError."""
        comps = [{"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"}]
        with pytest.raises(ValueError, match="must be positive"):
            market_approach_comparables(comps, subject_revenue=0)

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        comps = [
            {"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"},
        ]
        result = market_approach_comparables(comps, subject_revenue=2500000)
        expected_keys = (
            "value", "method", "formula_reference", "multiples",
            "implied_values", "range", "steps", "assumptions",
        )
        for key in expected_keys:
            assert key in result


class TestRoyaltyCapitalization:
    """Tests for royalty_capitalization function."""

    def test_book_example_10m_revenue_4pct_royalty_15pct_discount(self):
        """Book example: $10M revenue, 4% royalty, 15% discount = $2,666,667."""
        result = royalty_capitalization(
            revenue=10_000_000,
            royalty_rate=0.04,
            discount_rate=0.15,
        )
        assert result["value"] == pytest.approx(2_666_666.67, rel=1e-4)
        assert result["annual_royalty"] == 400_000.0
        assert result["method"] == "Royalty Capitalization"

    def test_basic_calculation(self):
        """Basic royalty capitalization calculation."""
        result = royalty_capitalization(
            revenue=5_000_000,
            royalty_rate=0.05,
            discount_rate=0.10,
        )
        assert result["value"] == pytest.approx(2_500_000.0, rel=1e-6)

    def test_zero_revenue_raises(self):
        """Zero revenue should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            royalty_capitalization(revenue=0, royalty_rate=0.05, discount_rate=0.10)

    def test_zero_royalty_rate_raises(self):
        """Zero royalty rate should raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            royalty_capitalization(revenue=1000000, royalty_rate=0, discount_rate=0.10)

    def test_zero_discount_rate_raises(self):
        """Zero discount rate should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            royalty_capitalization(revenue=1000000, royalty_rate=0.05, discount_rate=0)

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = royalty_capitalization(revenue=1000000, royalty_rate=0.05, discount_rate=0.10)
        for key in ("value", "method", "formula_reference", "annual_royalty", "steps", "assumptions"):
            assert key in result

def test_adjustments_accept_string_keys_from_json() -> None:
    """A JSON object cannot carry integer keys, so {"0": 0.10} must mean the same as {0: 0.10}.

    Before this, the lookup was `i in adjustments` with an integer index: an adjustment sent over
    HTTP or MCP was ignored and the caller got the unadjusted median with no error.
    """
    comparables = [
        {"sale_price": 1_200_000, "revenue": 1_000_000, "asset_type": "software"},
        {"sale_price": 1_500_000, "revenue": 1_000_000, "asset_type": "software"},
    ]
    as_int = market_approach_comparables(comparables=comparables, subject_revenue=1_000_000,
                                         adjustments={0: 0.10})
    as_str = market_approach_comparables(comparables=comparables, subject_revenue=1_000_000,
                                         adjustments={"0": 0.10})
    assert as_str.value == as_int.value
    assert as_str.value != market_approach_comparables(
        comparables=comparables, subject_revenue=1_000_000
    ).value

