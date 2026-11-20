"""Tests for impairment testing (TASK-036)."""

import pytest

from intangible_valuation.advanced.impairment_testing import (
    cash_generating_unit_impairment,
    fair_value_less_costs_to_sell,
    goodwill_impairment_test,
    intangible_impairment_test,
    value_in_use,
)


class TestGoodwillImpairment:
    def test_impairment_asc350(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=40_000_000,
            reporting_unit="Tech Division",
            standard="ASC350",
        )
        assert result.value == 10_000_000.0
        assert result.assumptions["impaired"] is True

    def test_no_impairment_asc350(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=55_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0
        assert result.assumptions["impaired"] is False

    def test_no_impairment_at_par(self):
        result = goodwill_impairment_test(
            carrying_value=50_000_000,
            fair_value=50_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0

    def test_ias36_impairment(self):
        result = goodwill_impairment_test(
            carrying_value=30_000_000,
            fair_value=25_000_000,
            standard="IAS36",
        )
        assert result.value == 5_000_000.0
        assert result.assumptions["impaired"] is True

    def test_ias36_no_impairment(self):
        result = goodwill_impairment_test(
            carrying_value=30_000_000,
            fair_value=35_000_000,
            standard="IAS36",
        )
        assert result.value == 0.0

    def test_default_standard_is_asc350(self):
        result = goodwill_impairment_test(50_000_000, 40_000_000)
        assert "ASC350" in result.method

    def test_ias36_uses_the_higher_of_fair_value_and_value_in_use(self):
        # IAS 36.18. Fair value is below carrying value here, which the old implementation used as the
        # recoverable amount — it reported a 2m impairment where the standard says there is none,
        # because value in use (12m) exceeds carrying value.
        result = goodwill_impairment_test(
            carrying_value=10_000_000,
            fair_value=8_000_000,
            value_in_use=12_000_000,
            standard="IAS36",
        )
        assert result.value == 0.0
        assert result.assumptions["impaired"] is False

    def test_ias36_impairment_is_measured_against_the_higher_component(self):
        # Both components are below carrying value; recoverable amount is the higher of the two, so
        # the impairment is 3m, not the 4m that fair value alone would give.
        result = goodwill_impairment_test(
            carrying_value=10_000_000,
            fair_value=6_000_000,
            value_in_use=7_000_000,
            standard="IAS36",
        )
        assert result.value == 3_000_000.0
        assert result.assumptions["value_in_use"] == 7_000_000

    def test_ias36_applies_costs_to_sell_to_the_fair_value_leg(self):
        # FV less costs to sell is 5.5m, value in use is 7m: recoverable is 7m, impairment 3m.
        result = goodwill_impairment_test(
            carrying_value=10_000_000,
            fair_value=6_000_000,
            costs_to_sell=500_000,
            value_in_use=7_000_000,
            standard="IAS36",
        )
        assert result.value == 3_000_000.0
        assert result.assumptions["costs_to_sell"] == 500_000

    def test_ias36_without_value_in_use_says_so_in_the_steps(self):
        # Callers that only hold a fair value still work, but the working must not imply the
        # comparison was made.
        result = goodwill_impairment_test(carrying_value=10_000_000, fair_value=8_000_000, standard="IAS36")
        assert result.value == 2_000_000.0
        step = next(s for s in result.steps if s["step"] == 5)
        assert "value in use not supplied" in step["description"]

    def test_invalid_standard_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(50_000_000, 40_000_000, standard="INVALID")

    def test_negative_carrying_value_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(-50_000_000, 40_000_000)

    def test_negative_fair_value_raises(self):
        with pytest.raises(ValueError):
            goodwill_impairment_test(50_000_000, -40_000_000)


class TestIntangibleImpairment:
    def test_asc350_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            fair_value=15_000_000,
            standard="ASC350",
        )
        assert result.value == 5_000_000.0
        assert result.assumptions["impaired"] is True

    def test_asc350_no_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            fair_value=25_000_000,
            standard="ASC350",
        )
        assert result.value == 0.0

    def test_asc350_missing_fair_value_raises(self):
        with pytest.raises(ValueError, match="fair_value is required"):
            intangible_impairment_test(carrying_value=20_000_000, standard="ASC350")

    def test_ias36_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            recoverable_amount=16_000_000,
            standard="IAS36",
        )
        assert result.value == 4_000_000.0
        assert result.assumptions["impaired"] is True

    def test_ias36_no_impairment(self):
        result = intangible_impairment_test(
            carrying_value=20_000_000,
            recoverable_amount=22_000_000,
            standard="IAS36",
        )
        assert result.value == 0.0

    def test_ias36_missing_recoverable_amount_raises(self):
        with pytest.raises(ValueError, match="recoverable_amount is required"):
            intangible_impairment_test(carrying_value=20_000_000, standard="IAS36")

    def test_invalid_standard_raises(self):
        with pytest.raises(ValueError):
            intangible_impairment_test(20_000_000, standard="INVALID")

    def test_negative_carrying_value_raises(self):
        with pytest.raises(ValueError):
            intangible_impairment_test(-20_000_000, fair_value=15_000_000)

    def test_returns_steps(self):
        result = intangible_impairment_test(20_000_000, fair_value=15_000_000)
        assert len(result.steps) >= 4


class TestValueInUse:
    """Tests for value_in_use function."""

    def test_happy_path_basic(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert result.value > 0
        assert "IAS 36 Value in Use" in result.method

    def test_happy_path_single_period(self):
        result = value_in_use(
            cash_flow_projections=[10_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert result.value > 0

    def test_happy_path_zero_growth(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_000_000, 5_000_000],
            terminal_growth_rate=0.0,
            discount_rate=0.10,
        )
        assert result.value > 0

    def test_error_discount_not_exceeding_growth(self):
        with pytest.raises(ValueError, match="Discount rate must exceed"):
            value_in_use(
                cash_flow_projections=[5_000_000],
                terminal_growth_rate=0.10,
                discount_rate=0.10,
            )

    def test_error_negative_cash_flow(self):
        with pytest.raises(ValueError):
            value_in_use(
                cash_flow_projections=[-5_000_000],
                terminal_growth_rate=0.02,
                discount_rate=0.10,
            )

    def test_error_empty_projections(self):
        with pytest.raises(ValueError):
            value_in_use(
                cash_flow_projections=[],
                terminal_growth_rate=0.02,
                discount_rate=0.10,
            )

    def test_returns_terminal_value(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert "terminal_value" in result.assumptions
        assert "pv_terminal_value" in result.assumptions


class TestFairValueLessCostsToSell:
    """Tests for fair_value_less_costs_to_sell function."""

    def test_happy_path_basic(self):
        result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        assert result.value == 9_500_000.0
        assert "Fair Value Less Costs" in result.method

    def test_happy_path_zero_costs(self):
        result = fair_value_less_costs_to_sell(10_000_000, 0)
        assert result.value == 10_000_000.0

    def test_happy_path_high_costs(self):
        result = fair_value_less_costs_to_sell(10_000_000, 2_000_000)
        assert result.value == 8_000_000.0

    def test_error_negative_fair_value(self):
        with pytest.raises(ValueError):
            fair_value_less_costs_to_sell(-10_000_000, 500_000)

    def test_error_negative_disposal_costs(self):
        with pytest.raises(ValueError):
            fair_value_less_costs_to_sell(10_000_000, -500_000)

    def test_returns_steps(self):
        result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        assert len(result.steps) >= 4


class TestCGUImpairment:
    """Tests for cash_generating_unit_impairment function."""

    def test_happy_path_impairment(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=80_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert result.value == 20_000_000.0
        assert "CGU Impairment" in result.method

    def test_happy_path_no_impairment(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=110_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
            ],
        )
        assert result.value == 0.0

    def test_happy_path_goodwill_fully_written_off(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=70_000_000,
            goodwill_allocated=10_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 45_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert result.value == 30_000_000.0
        allocation = result.assumptions["allocation"]
        gw_alloc = next(a for a in allocation if a["asset"] == "Goodwill")
        assert gw_alloc["impairment"] == 10_000_000.0

    def test_goodwill_absorbs_all_impairment_no_crash(self):
        # Regression: goodwill absorbing the entire impairment left `proportion`
        # unbound in the pro-rata step (UnboundLocalError). This case must not crash.
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=90_000_000,  # impairment = 10M
            goodwill_allocated=10_000_000,  # goodwill absorbs all 10M
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
            ],
        )
        assert result.value == 10_000_000.0
        allocation = result.assumptions["allocation"]
        patents = next(a for a in allocation if a["asset"] == "Patents")
        assert patents["impairment"] == 0.0

    def test_error_empty_assets(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[],
            )

    def test_error_missing_asset_name(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[{"carrying_value": 40_000_000}],
            )

    def test_error_negative_carrying_value(self):
        with pytest.raises(ValueError):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=15_000_000,
                other_assets=[{"name": "X", "carrying_value": -100}],
            )

    def test_returns_allocation_details(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=80_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert "allocation" in result.assumptions
        assert len(result.assumptions["allocation"]) == 3

    def test_negative_costs_to_sell_raises(self):
        # `ge=0` on GoodwillImpairmentInput.costs_to_sell is the control: a negative cost would
        # otherwise *add* to the fair-value leg and understate the impairment.
        with pytest.raises(ValueError):
            goodwill_impairment_test(10_000_000, 8_000_000, costs_to_sell=-1, standard="IAS36")

    def test_costs_above_fair_value_cannot_impair_more_than_the_carrying_value(self):
        # The clamp at 0: unclamped, FV less costs to sell is negative and the impairment exceeds the
        # carrying value, writing the asset below zero.
        result = goodwill_impairment_test(
            carrying_value=1_000, fair_value=100, costs_to_sell=500, standard="IAS36"
        )
        assert result.value == 1_000.0


class TestOneVocabulary:
    """`disposal_costs` and `costs_to_sell` are the same IAS 36 quantity.

    Measured 2026-11-20: a caller reading the standard says "costs to sell", which
    `goodwill_impairment_test` also uses, while this function named it `disposal_costs` — so the same
    payload succeeded on one method and returned 400 on another. Both names are accepted; supplying
    both is refused rather than silently preferring one.
    """

    def test_the_two_names_agree(self):
        positional = fair_value_less_costs_to_sell(800.0, 50.0)
        aliased = fair_value_less_costs_to_sell(800.0, costs_to_sell=50.0)

        assert positional.value == aliased.value == 750.0

    def test_both_names_is_refused(self):
        with pytest.raises(ValueError, match="exactly one of"):
            fair_value_less_costs_to_sell(800.0, 50.0, costs_to_sell=50.0)

    def test_neither_name_is_refused(self):
        with pytest.raises(ValueError, match="exactly one of"):
            fair_value_less_costs_to_sell(800.0)
