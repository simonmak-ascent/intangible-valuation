"""The package attribute and the submodule function are the same callable.

`income_methods/__init__.py` used to define its own `relief_from_royalty` — a constant-revenue
annuity with no tax-amortisation benefit — while `income_methods/relief_from_royalty.py` defined the
period-by-period one. Every caller (the MCP surface, the tests) imported the submodule, so the package
attribute was a second formula under one name, and `import intangible_valuation.income_methods.X`
rebound it to the module, making the answer depend on import order.

These tests fail if a duplicate definition comes back.
"""

from __future__ import annotations

import importlib

import pytest

from intangible_valuation import income_methods


def test_package_attribute_is_callable() -> None:
    assert callable(income_methods.relief_from_royalty)
    assert callable(income_methods.incremental_cashflow)


def test_importing_the_submodule_does_not_shadow_the_callable() -> None:
    # This is the order that used to break: package first, then the submodule.
    importlib.import_module("intangible_valuation.income_methods.relief_from_royalty")
    assert callable(income_methods.relief_from_royalty), (
        "importing the submodule rebound the package attribute to the module"
    )


@pytest.mark.parametrize(
    "name",
    ["relief_from_royalty", "incremental_cashflow", "mpeem", "contributory_asset_charges"],
)
def test_reexports_resolve_to_functions(name: str) -> None:
    func = getattr(income_methods, name)
    assert callable(func)


def test_the_two_spellings_are_one_function() -> None:
    assert income_methods.incremental_cash_flow is income_methods.incremental_cashflow


@pytest.mark.parametrize("name", ["relief_from_royalty", "excess_earnings", "incremental_cash_flow"])
def test_no_duplicate_function_definition_in_the_package_root(name: str) -> None:
    """A second `def <name>` in the package root is the defect this file exists for.

    All three of these were defined here *and* in their own module when this file was written;
    guarding only one of them would let the other two come back unnoticed.
    """
    from pathlib import Path

    init = Path(income_methods.__file__).read_text(encoding="utf-8")
    assert f"\ndef {name}" not in init, f"the package root defines {name} again"
