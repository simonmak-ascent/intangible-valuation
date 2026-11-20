"""Goodwill and intangible asset impairment testing.

Implements Section 10.4 and Appendix A.9:
- ASC 350: Goodwill impairment = Carrying Value - Fair Value (one-step test)
- IAS 36: Uses recoverable amount (higher of FV less costs to sell and value in use)
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from intangible_valuation.core import ValuationResult, present_value, terminal_value


class GoodwillImpairmentInput(BaseModel):
    carrying_value: float = Field(gt=0, description="Reporting unit carrying value including goodwill")
    fair_value: float = Field(ge=0, description="Reporting unit fair value")
    # IAS 36 only. Validated here rather than trusted from the two new keyword arguments, because
    # the sibling FVLCTSInputs validates the same quantity and a negative cost silently *increases*
    # the fair-value leg.
    value_in_use: float | None = Field(default=None, ge=0, description="Value in use (IAS 36 only)")
    costs_to_sell: float = Field(default=0.0, ge=0, description="Costs to sell (IAS 36 only)")
    reporting_unit: str = Field(default="", description="Name of the reporting unit")
    standard: str = Field(default="ASC350", pattern="^(ASC350|IAS36)$", description="Accounting standard")


class IntangibleImpairmentInput(BaseModel):
    carrying_value: float = Field(gt=0, description="Asset carrying value")
    fair_value: float | None = Field(default=None, ge=0, description="Fair value (required for ASC350)")
    recoverable_amount: float | None = Field(default=None, ge=0, description="Recoverable amount (required for IAS36)")
    standard: str = Field(default="ASC350", pattern="^(ASC350|IAS36)$", description="Accounting standard")


def goodwill_impairment_test(
    carrying_value: float,
    fair_value: float,
    reporting_unit: str = "",
    standard: str = "ASC350",
    value_in_use: float | None = None,
    costs_to_sell: float = 0.0,
) -> ValuationResult:
    """Test goodwill for impairment per ASC 350 or IAS 36.

    ASC 350 (US GAAP):
        Impairment = Carrying Value - Fair Value (if FV < CV, else 0)
        Single-step quantitative test.

    IAS 36 (IFRS):
        Impairment = Carrying Value - Recoverable Amount
        Recoverable amount = higher of (FV less costs to sell, value in use)
        For goodwill, the reporting unit is the cash-generating unit (CGU).

    The IAS 36 branch used to take `fair_value` as the recoverable amount. That is the *lower* of
    the two components whenever value in use exceeds fair value less costs to sell, so it overstated
    the impairment by exactly the gap — and the module already has `value_in_use()` and
    `fair_value_less_costs_to_sell()` to compute both. `value_in_use` is optional because callers
    that only have fair value still work; when it is absent the steps say so rather than implying
    the comparison was made.

    Args:
        carrying_value: Carrying value of the reporting unit (including goodwill).
        fair_value: Fair value of the reporting unit.
        reporting_unit: Name of the reporting unit being tested.
        standard: "ASC350" for US GAAP, "IAS36" for IFRS.

    Returns:
        ValuationResult with impairment amount (0 if no impairment).

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = goodwill_impairment_test(50_000_000, 40_000_000, "Tech Division")
        >>> result.value
        10000000.0
    """
    GoodwillImpairmentInput(
        carrying_value=carrying_value,
        fair_value=fair_value,
        value_in_use=value_in_use,
        costs_to_sell=costs_to_sell,
        reporting_unit=reporting_unit,
        standard=standard,
    )

    if standard == "ASC350":
        if fair_value < carrying_value:
            impairment = carrying_value - fair_value
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {
                "step": 1,
                "description": "Standard: ASC 350 (US GAAP) - One-step goodwill impairment test",
            },
            {"step": 2, "description": f"Reporting Unit: {reporting_unit or 'N/A'}"},
            {"step": 3, "description": "Carrying Value", "value": carrying_value},
            {"step": 4, "description": "Fair Value", "value": fair_value},
            {
                "step": 5,
                "description": "Impairment = max(0, CV - FV)",
                "calculation": f"max(0, {carrying_value} - {fair_value})",
            },
            {"step": 6, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, ASC 350-20-35"

    elif standard == "IAS36":
        # IAS 36.18: recoverable amount is the HIGHER of fair value less costs to sell and value in
        # use. Taking fair value alone is the lower bound, so it overstates the impairment whenever
        # value in use is greater.
        # Clamped at zero: fair value less costs to sell cannot be negative in substance, and an
        # unclamped negative would make the impairment exceed the carrying value — writing the asset
        # below zero, which no accounting standard permits.
        fair_value_less_costs = max(0.0, fair_value - costs_to_sell)
        recoverable_amount = (
            max(fair_value_less_costs, value_in_use) if value_in_use is not None else fair_value_less_costs
        )
        if recoverable_amount < carrying_value:
            impairment = carrying_value - recoverable_amount
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {
                "step": 1,
                "description": "Standard: IAS 36 (IFRS) - Impairment of Assets",
            },
            {"step": 2, "description": f"Reporting Unit (CGU): {reporting_unit or 'N/A'}"},
            {"step": 3, "description": "Carrying Value", "value": carrying_value},
            {
                "step": 4,
                "description": "Fair Value Less Costs to Sell",
                "value": round(fair_value_less_costs, 2),
                "calculation": f"{fair_value} - {costs_to_sell}",
            },
            {
                "step": 5,
                "description": (
                    "Recoverable Amount = max(FV less costs to sell, value in use)"
                    if value_in_use is not None
                    else "Recoverable Amount — value in use not supplied, using fair value less costs to sell"
                ),
                "value": round(recoverable_amount, 2),
            },
            {
                "step": 6,
                "description": "Impairment = max(0, CV - Recoverable Amount)",
                "calculation": f"max(0, {carrying_value} - {recoverable_amount})",
            },
            {"step": 7, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, IAS 36"
    else:
        raise ValueError(f"Unsupported standard: {standard}. Use 'ASC350' or 'IAS36'.")

    return ValuationResult(
        value=round(impairment, 2),
        method=f"Goodwill Impairment Test ({standard})",
        formula_reference=formula_ref,
        steps=steps,
        assumptions={
            "carrying_value": carrying_value,
            "fair_value": fair_value,
            "value_in_use": value_in_use,
            "costs_to_sell": costs_to_sell,
            "reporting_unit": reporting_unit,
            "standard": standard,
            "impaired": impaired,
        },
    )


def intangible_impairment_test(
    carrying_value: float,
    fair_value: float | None = None,
    recoverable_amount: float | None = None,
    standard: str = "ASC350",
) -> ValuationResult:
    """Test intangible asset for impairment per ASC 350 or IAS 36.

    ASC 350 (US GAAP):
        For indefinite-lived intangibles: Compare carrying value to fair value.
        Impairment = CV - FV (if FV < CV).

    IAS 36 (IFRS):
        Compare carrying value to recoverable amount.
        Recoverable amount = higher of (FV less costs to sell, value in use).
        Impairment = CV - Recoverable Amount (if RA < CV).

    Args:
        carrying_value: Carrying value of the intangible asset.
        fair_value: Fair value of the asset (required for ASC350).
        recoverable_amount: Recoverable amount (required for IAS36).
        standard: "ASC350" for US GAAP, "IAS36" for IFRS.

    Returns:
        ValuationResult with impairment amount (0 if no impairment).

    Raises:
        ValueError: If required parameters are missing for the chosen standard.

    Example:
        >>> result = intangible_impairment_test(20_000_000, fair_value=15_000_000)
        >>> result.value
        5000000.0
    """
    IntangibleImpairmentInput(
        carrying_value=carrying_value,
        fair_value=fair_value,
        recoverable_amount=recoverable_amount,
        standard=standard,
    )

    if standard == "ASC350":
        if fair_value is None:
            raise ValueError("fair_value is required for ASC350 impairment test")

        if fair_value < carrying_value:
            impairment = carrying_value - fair_value
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {
                "step": 1,
                "description": "Standard: ASC 350 - Indefinite-lived intangible impairment test",
            },
            {"step": 2, "description": "Carrying Value", "value": carrying_value},
            {"step": 3, "description": "Fair Value", "value": fair_value},
            {
                "step": 4,
                "description": "Impairment = max(0, CV - FV)",
                "calculation": f"max(0, {carrying_value} - {fair_value})",
            },
            {"step": 5, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, ASC 350-30-35"

    elif standard == "IAS36":
        if recoverable_amount is None:
            raise ValueError("recoverable_amount is required for IAS36 impairment test")

        if recoverable_amount < carrying_value:
            impairment = carrying_value - recoverable_amount
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {
                "step": 1,
                "description": "Standard: IAS 36 - Impairment of Assets",
            },
            {"step": 2, "description": "Carrying Value", "value": carrying_value},
            {"step": 3, "description": "Recoverable Amount", "value": recoverable_amount},
            {
                "step": 4,
                "description": "Impairment = max(0, CV - Recoverable Amount)",
                "calculation": f"max(0, {carrying_value} - {recoverable_amount})",
            },
            {"step": 5, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, IAS 36"
    else:
        raise ValueError(f"Unsupported standard: {standard}. Use 'ASC350' or 'IAS36'.")

    return ValuationResult(
        value=round(impairment, 2),
        method=f"Intangible Impairment Test ({standard})",
        formula_reference=formula_ref,
        steps=steps,
        assumptions={
            "carrying_value": carrying_value,
            "fair_value": fair_value,
            "recoverable_amount": recoverable_amount,
            "standard": standard,
            "impaired": impaired,
        },
    )


class ValueInUseInputs(BaseModel):
    """Inputs for IAS 36 value in use calculation."""

    cash_flow_projections: list[float] = Field(min_length=1, description="Projected future cash flows")
    terminal_growth_rate: float = Field(description="Perpetual growth rate for terminal value (decimal)")
    discount_rate: float = Field(gt=0, description="Pre-tax discount rate (decimal)")

    @field_validator("cash_flow_projections")
    @classmethod
    def cash_flows_valid(cls, v: list[float]) -> list[float]:
        if any(cf < 0 for cf in v):
            raise ValueError("Cash flow projections must be non-negative")
        return v


def value_in_use(
    cash_flow_projections: list[float],
    terminal_growth_rate: float,
    discount_rate: float,
) -> ValuationResult:
    """Calculate value in use per IAS 36 using discounted cash flows.

    Value in use is the present value of future cash flows expected to be
    derived from an asset or cash-generating unit, including a terminal value.

    Formula:
        VIU = sum(CF_t / (1+r)^t) + Terminal Value / (1+r)^n
        Terminal Value = CF_n x (1+g) / (r - g)

    Where:
        CF_t = cash flow in period t
        r = pre-tax discount rate
        g = terminal growth rate
        n = number of explicit projection periods

    Args:
        cash_flow_projections: Projected future cash flows (must be non-negative).
        terminal_growth_rate: Perpetual growth rate for terminal value (decimal).
        discount_rate: Pre-tax discount rate reflecting current market assessment.

    Returns:
        ValuationResult with value in use, calculation steps, and assumptions.

    Raises:
        ValueError: If inputs are invalid (e.g., discount_rate <= terminal_growth_rate).

    Example:
        >>> result = value_in_use(
        ...     cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
        ...     terminal_growth_rate=0.02,
        ...     discount_rate=0.10,
        ... )
        >>> result.value > 0
        True

    Reference:
        IAS 36.57-59: Value in use calculation requirements.
    """
    inputs = ValueInUseInputs(
        cash_flow_projections=cash_flow_projections,
        terminal_growth_rate=terminal_growth_rate,
        discount_rate=discount_rate,
    )

    if inputs.discount_rate <= inputs.terminal_growth_rate:
        raise ValueError(
            "Discount rate must exceed terminal growth rate. "
            f"Got discount_rate={inputs.discount_rate}, "
            f"terminal_growth_rate={inputs.terminal_growth_rate}"
        )

    steps: list[dict] = []
    pv_explicit = 0.0
    n = len(inputs.cash_flow_projections)

    steps.append({"step": 1, "description": "IAS 36 Value in Use Calculation"})
    steps.append({"step": 2, "description": f"Projection periods: {n}"})
    steps.append({"step": 3, "description": f"Discount rate: {inputs.discount_rate:.2%}"})
    steps.append({"step": 4, "description": f"Terminal growth rate: {inputs.terminal_growth_rate:.2%}"})

    for t, cf in enumerate(inputs.cash_flow_projections, start=1):
        pv = present_value(cf, inputs.discount_rate, t)
        pv_explicit += pv
        steps.append(
            {
                "step": t + 4,
                "description": f"Year {t} cash flow",
                "value": cf,
                "pv": round(pv, 2),
            }
        )

    # Terminal value using Gordon Growth Model
    final_cf = inputs.cash_flow_projections[-1]
    terminal_val = terminal_value(final_cf, inputs.terminal_growth_rate, inputs.discount_rate)
    pv_terminal = present_value(terminal_val, inputs.discount_rate, n)

    calc = f"{final_cf} x (1+{inputs.terminal_growth_rate}) / ({inputs.discount_rate} - {inputs.terminal_growth_rate})"
    steps.append(
        {
            "step": n + 5,
            "description": "Terminal Value (Gordon Growth)",
            "calculation": calc,
            "value": round(terminal_val, 2),
            "pv": round(pv_terminal, 2),
        }
    )

    viu = pv_explicit + pv_terminal

    steps.append(
        {
            "step": n + 6,
            "description": "Value in Use",
            "calculation": f"PV(explicit) + PV(terminal) = {pv_explicit:,.0f} + {pv_terminal:,.0f}",
            "value": round(viu, 2),
        }
    )

    return ValuationResult(
        value=round(viu, 2),
        method="IAS 36 Value in Use",
        formula_reference="IAS 36.30, VIU = sum(CF_t/(1+r)^t) + TV/(1+r)^n",
        steps=steps,
        assumptions={
            "cash_flow_projections": inputs.cash_flow_projections,
            "terminal_growth_rate": inputs.terminal_growth_rate,
            "discount_rate": inputs.discount_rate,
            "pv_explicit_cash_flows": round(pv_explicit, 2),
            "terminal_value": round(terminal_val, 2),
            "pv_terminal_value": round(pv_terminal, 2),
        },
    )


class FVLCTSInputs(BaseModel):
    """Inputs for fair value less costs to sell."""

    fair_value: float = Field(ge=0, description="Fair value of the asset")
    disposal_costs: float = Field(ge=0, description="Costs to sell/dispose")


def fair_value_less_costs_to_sell(
    fair_value: float,
    disposal_costs: float,
) -> ValuationResult:
    """Calculate fair value less costs to sell per IAS 36.

    Fair value less costs to sell (FVLCTS) is the amount obtainable from
    the sale of an asset in an arm's length transaction, less costs of disposal.

    Formula:
        FVLCTS = Fair Value - Costs to Sell

    Args:
        fair_value: Fair value of the asset in an arm's length transaction.
        disposal_costs: Incremental costs directly attributable to disposal
            (legal costs, stamp duty, transaction taxes, removal costs).

    Returns:
        ValuationResult with FVLCTS amount, steps, and assumptions.

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        >>> result.value
        9500000.0

    Reference:
        IAS 36.6-7: Definition of fair value less costs of disposal.
        IFRS 13: Fair Value Measurement.
    """
    inputs = FVLCTSInputs(fair_value=fair_value, disposal_costs=disposal_costs)

    fvlcts = inputs.fair_value - inputs.disposal_costs

    steps: list[dict] = [
        {"step": 1, "description": "IAS 36 Fair Value Less Costs to Sell"},
        {"step": 2, "description": "Fair Value", "value": inputs.fair_value},
        {"step": 3, "description": "Costs to Sell", "value": inputs.disposal_costs},
        {
            "step": 4,
            "description": "FVLCTS = Fair Value - Costs to Sell",
            "calculation": f"{inputs.fair_value} - {inputs.disposal_costs}",
        },
        {"step": 5, "description": "FVLCTS", "value": round(fvlcts, 2)},
    ]

    return ValuationResult(
        value=round(fvlcts, 2),
        method="Fair Value Less Costs to Sell (IAS 36)",
        formula_reference="IAS 36.6, FVLCTS = FV - Costs to Sell",
        steps=steps,
        assumptions={
            "fair_value": inputs.fair_value,
            "disposal_costs": inputs.disposal_costs,
        },
    )


class CGUImpairmentInputs(BaseModel):
    """Inputs for CGU-level impairment allocation."""

    cgu_carrying_value: float = Field(gt=0, description="CGU carrying value including goodwill")
    cgu_recoverable_amount: float = Field(ge=0, description="CGU recoverable amount")
    goodwill_allocated: float = Field(ge=0, description="Goodwill allocated to CGU")
    other_assets: list[dict] = Field(description="Other assets in CGU with 'name' and 'carrying_value'")


def cash_generating_unit_impairment(
    cgu_carrying_value: float,
    cgu_recoverable_amount: float,
    goodwill_allocated: float,
    other_assets: list[dict],
) -> ValuationResult:
    """Allocate impairment loss at the CGU level per IAS 36.

    When a CGU is impaired, the loss is allocated:
    1. First to reduce goodwill allocated to the CGU
    2. Then pro rata to other assets based on carrying amounts

    No asset is reduced below the highest of:
    - Its fair value less costs to sell
    - Its value in use
    - Zero

    Args:
        cgu_carrying_value: Total carrying value of the CGU (including goodwill).
        cgu_recoverable_amount: Recoverable amount of the CGU.
        goodwill_allocated: Amount of goodwill allocated to this CGU.
        other_assets: List of dicts with 'name' and 'carrying_value' for
            each non-goodwill asset in the CGU.

    Returns:
        ValuationResult with total impairment, allocation details, and
            post-impairment carrying values.

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = cash_generating_unit_impairment(
        ...     cgu_carrying_value=100_000_000,
        ...     cgu_recoverable_amount=80_000_000,
        ...     goodwill_allocated=15_000_000,
        ...     other_assets=[
        ...         {"name": "Patents", "carrying_value": 40_000_000},
        ...         {"name": "Equipment", "carrying_value": 45_000_000},
        ...     ],
        ... )
        >>> result.value  # Total impairment
        20000000.0

    Reference:
        IAS 36.104-108: Impairment loss allocation to a CGU.
    """
    if not other_assets:
        raise ValueError("other_assets list cannot be empty")

    for i, asset in enumerate(other_assets):
        if "name" not in asset:
            raise ValueError(f"Asset {i} missing 'name' key")
        if "carrying_value" not in asset:
            raise ValueError(f"Asset {i} missing 'carrying_value' key")
        if asset["carrying_value"] < 0:
            raise ValueError(f"Asset {i} carrying_value must be non-negative")

    inputs = CGUImpairmentInputs(
        cgu_carrying_value=cgu_carrying_value,
        cgu_recoverable_amount=cgu_recoverable_amount,
        goodwill_allocated=goodwill_allocated,
        other_assets=other_assets,
    )

    steps: list[dict] = []

    total_impairment = max(0, inputs.cgu_carrying_value - inputs.cgu_recoverable_amount)
    remaining_impairment = total_impairment

    steps.append({"step": 1, "description": "IAS 36 CGU Impairment Allocation"})
    steps.append(
        {
            "step": 2,
            "description": "CGU Carrying Value",
            "value": inputs.cgu_carrying_value,
        }
    )
    steps.append(
        {
            "step": 3,
            "description": "CGU Recoverable Amount",
            "value": inputs.cgu_recoverable_amount,
        }
    )
    steps.append(
        {
            "step": 4,
            "description": "Total Impairment Loss",
            "value": round(total_impairment, 2),
        }
    )

    allocation_details: list[dict] = []
    if total_impairment == 0:
        steps.append(
            {
                "step": 5,
                "description": "No impairment - recoverable amount exceeds carrying value",
            }
        )
    else:
        # Step 1: Allocate to goodwill first
        gw_impairment = min(remaining_impairment, inputs.goodwill_allocated)
        remaining_impairment -= gw_impairment
        remaining_goodwill = inputs.goodwill_allocated - gw_impairment

        allocation_details.append(
            {
                "asset": "Goodwill",
                "carrying_value": inputs.goodwill_allocated,
                "impairment": round(gw_impairment, 2),
                "post_impairment": round(remaining_goodwill, 2),
            }
        )
        steps.append(
            {
                "step": 5,
                "description": "Allocate to goodwill",
                "impairment": round(gw_impairment, 2),
                "remaining": round(remaining_goodwill, 2),
            }
        )

        # Step 2: Allocate remaining to other assets pro rata
        total_other_cv = sum(a["carrying_value"] for a in inputs.other_assets)
        for asset in inputs.other_assets:
            proportion = 0.0
            if total_other_cv > 0 and remaining_impairment > 0:
                proportion = asset["carrying_value"] / total_other_cv
                asset_impairment = remaining_impairment * proportion
            else:
                asset_impairment = 0.0

            post_impairment = asset["carrying_value"] - asset_impairment
            allocation_details.append(
                {
                    "asset": asset["name"],
                    "carrying_value": asset["carrying_value"],
                    "impairment": round(asset_impairment, 2),
                    "post_impairment": round(post_impairment, 2),
                }
            )
            steps.append(
                {
                    "step": len(steps) + 1,
                    "description": f"Allocate to {asset['name']}",
                    "proportion": f"{proportion:.1%}" if total_other_cv > 0 else "0%",
                    "impairment": round(asset_impairment, 2),
                    "post_impairment": round(post_impairment, 2),
                }
            )

    return ValuationResult(
        value=round(total_impairment, 2),
        method="CGU Impairment Allocation (IAS 36)",
        formula_reference="IAS 36.104-108: Goodwill first, then pro rata",
        steps=steps,
        assumptions={
            "cgu_carrying_value": inputs.cgu_carrying_value,
            "cgu_recoverable_amount": inputs.cgu_recoverable_amount,
            "goodwill_allocated": inputs.goodwill_allocated,
            "total_impairment": round(total_impairment, 2),
            "allocation": allocation_details,
        },
    )
