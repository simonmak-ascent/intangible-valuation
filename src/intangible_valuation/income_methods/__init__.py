"""Advanced income-based valuation methods (Chapter 4).

The functions live in their own modules. This package re-exports them so
``intangible_valuation.income_methods.relief_from_royalty`` is one callable rather than a second
implementation that shadows the module of the same name.

That shadowing was a real defect: this file used to define its own ``relief_from_royalty`` (a
constant-revenue annuity with no tax-amortisation benefit) while
``income_methods/relief_from_royalty.py`` defined the period-by-period one with TAB. The MCP surface
and every test import the submodule, so the package attribute was the odd one out — and because
``import intangible_valuation.income_methods.relief_from_royalty`` rebinds the attribute to the
module, the callable/ module question depended on import order.
"""

from __future__ import annotations

from intangible_valuation.income_methods.excess_earnings import (
    contributory_asset_charges,
    mpeem,
    single_period_excess_earnings,
)
from intangible_valuation.income_methods.incremental_cashflow import incremental_cashflow
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

# The spelling the package used before the re-export; kept so an existing import does not break.
incremental_cash_flow = incremental_cashflow

__all__ = [
    "contributory_asset_charges",
    "incremental_cash_flow",
    "incremental_cashflow",
    "mpeem",
    "relief_from_royalty",
    "single_period_excess_earnings",
]
