"""Market approach valuation methods.

Implements comparable transactions and royalty capitalization methods
from Chapter 3.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from intangible_valuation.core import ValuationResult


class MarketApproachResult(BaseModel):
    """Result of a market approach valuation."""

    value: float = Field(..., description="Estimated value")
    method: str = Field(..., description="Valuation method name")
    formula_reference: str = Field(..., description="Reference to formula in textbook")
    steps: list[str] = Field(default_factory=list, description="Calculation steps")
    assumptions: list[str] = Field(default_factory=list, description="Key assumptions")


class ComparableInput(BaseModel):
    """Validated comparable transaction input."""

    sale_price: float = Field(..., gt=0, description="Transaction sale price")
    revenue: float = Field(..., gt=0, description="Revenue associated with the asset")
    asset_type: str = Field(..., min_length=1, description="Type of intangible asset")


def market_approach_comparables(
    comparables: list[dict],
    subject_revenue: float,
    adjustments: dict | None = None,
) -> ValuationResult:
    """Valuation based on comparable market transactions.

    Applies revenue multiples from comparable transactions to the subject
    asset's revenue, with optional adjustments for size, risk, or other factors.

    Formula:
        Multiple_i = sale_price_i / revenue_i
        Adjusted_Multiple_i = Multiple_i * (1 + adjustment_i)
        Implied_Value_i = Adjusted_Multiple_i * subject_revenue
        Value = median(Implied_Value_i)

    Args:
        comparables: List of dicts with 'sale_price', 'revenue', 'asset_type' keys.
            Each comparable must have positive sale_price and revenue.
        subject_revenue: Revenue of the subject asset. Must be positive.
        adjustments: Optional dict mapping comparable index (0-based) to
            adjustment factor (e.g., {0: 0.10, 1: -0.05}). Defaults to no adjustments.

    Returns:
        ValuationResult with:
            - value: Median implied value from comparables
            - method: 'Market Approach - Comparables'
            - formula_reference: 'Chapter 3: Market Approach - Comparable Transactions'
            - multiples: List of calculated multiples per comparable
            - implied_values: List of implied values per comparable
            - range: (min, max) of implied values
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If comparables is empty, subject_revenue is non-positive,
            or comparable data is invalid.

    Example:
        >>> comps = [
        ...     {"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"},
        ...     {"sale_price": 8000000, "revenue": 3000000, "asset_type": "trademark"},
        ...     {"sale_price": 12000000, "revenue": 4000000, "asset_type": "trademark"},
        ... ]
        >>> result = market_approach_comparables(comps, subject_revenue=2500000)
        >>> round(result.value, 2)
        6666666.67
    """
    if not comparables:
        raise ValueError("comparables list cannot be empty")
    if subject_revenue <= 0:
        raise ValueError(f"subject_revenue must be positive, got {subject_revenue}")

    steps = [
        f"Subject asset revenue: ${subject_revenue:,.2f}",
        f"Number of comparables: {len(comparables)}",
    ]

    multiples = []
    implied_values = []

    for i, comp_data in enumerate(comparables):
        comp = ComparableInput(**comp_data)
        multiple = comp.sale_price / comp.revenue

        adjustment = 0.0
        if adjustments:
            # JSON object keys are always strings, so a caller arriving over HTTP or MCP sends
            # {"0": 0.10}. Accept both forms: an int-only lookup silently ignored every adjustment
            # sent through either surface, returning an unadjusted median with no error.
            adjustment = adjustments.get(i, adjustments.get(str(i), 0.0))

        adjusted_multiple = multiple * (1 + adjustment)
        implied_value = adjusted_multiple * subject_revenue

        multiples.append(
            {
                "index": i,
                "asset_type": comp.asset_type,
                "sale_price": comp.sale_price,
                "revenue": comp.revenue,
                "multiple": multiple,
                "adjustment": adjustment,
                "adjusted_multiple": adjusted_multiple,
                "implied_value": implied_value,
            }
        )
        implied_values.append(implied_value)

        steps.append(
            f"Comparable {i} ({comp.asset_type}): multiple={multiple:.2f}x, "
            f"adjustment={adjustment:.1%}, implied value=${implied_value:,.2f}"
        )

    sorted_values = sorted(implied_values)
    n = len(sorted_values)
    median_value = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2 if n % 2 == 0 else sorted_values[n // 2]

    steps.append(f"Implied value range: ${min(implied_values):,.2f} - ${max(implied_values):,.2f}")
    steps.append(f"Median implied value: ${median_value:,.2f}")

    assumptions = [
        "Comparable transactions are arm's length and recent",
        "Revenue multiples are appropriate for the asset type",
        "Market conditions are similar between comparables and subject",
        "Adjustments reflect identifiable differences",
    ]

    return ValuationResult(value=median_value, method="Market Approach - Comparables", formula_reference="Chapter 3: Market Approach - Comparable Transactions", multiples=multiples, implied_values=implied_values, range=(min(implied_values), max(implied_values)), steps=steps, assumptions=assumptions)


def royalty_capitalization(
    revenue: float,
    royalty_rate: float,
    discount_rate: float,
) -> ValuationResult:
    """Valuation using the royalty capitalization method.

    Capitalizes a perpetual royalty stream into a present value.
    Appropriate for mature assets with stable, predictable revenue.

    Formula:
        Value = (revenue * royalty_rate) / discount_rate
              = annual_royalty / discount_rate

    Args:
        revenue: Annual revenue attributable to the asset. Must be positive.
        royalty_rate: Royalty rate as decimal (e.g., 0.04 for 4%). Must be between 0 and 1.
        discount_rate: Discount rate as decimal. Must be positive.

    Returns:
        ValuationResult with:
            - value: Capitalized royalty value
            - method: 'Royalty Capitalization'
            - formula_reference: 'Chapter 3: Market Approach - Royalty Capitalization'
            - annual_royalty: revenue * royalty_rate
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If inputs are out of valid range.

    Example:
        >>> result = royalty_capitalization(
        ...     revenue=10_000_000,
        ...     royalty_rate=0.04,
        ...     discount_rate=0.15
        ... )
        >>> result.value
        2666666.6666666665
    """
    if revenue <= 0:
        raise ValueError(f"revenue must be positive, got {revenue}")
    if not (0 < royalty_rate < 1):
        raise ValueError(f"royalty_rate must be between 0 and 1 (exclusive), got {royalty_rate}")
    if discount_rate <= 0:
        raise ValueError(f"discount_rate must be positive, got {discount_rate}")

    annual_royalty = revenue * royalty_rate
    value = annual_royalty / discount_rate

    steps = [
        f"Annual revenue: ${revenue:,.2f}",
        f"Royalty rate: {royalty_rate:.2%}",
        f"Annual royalty payment: ${annual_royalty:,.2f}",
        f"Discount rate: {discount_rate:.2%}",
        f"Capitalized value: ${value:,.2f}",
    ]

    assumptions = [
        "Revenue is perpetual and stable",
        "Royalty rate reflects arm's length market rate",
        "Discount rate appropriately reflects risk of royalty stream",
        "No growth in revenue is assumed (perpetuity)",
    ]

    return ValuationResult(value=value, method="Royalty Capitalization", formula_reference="Chapter 3: Market Approach - Royalty Capitalization", annual_royalty=annual_royalty, steps=steps, assumptions=assumptions)
