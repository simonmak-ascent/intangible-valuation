"""Industry default rates and constants for valuation calculations."""

from typing import Final

# Default rates.
#
# These are FIXED ILLUSTRATIVE VALUES, not market data. A caller valuing at a date should pass the
# rate for that date; the library deliberately performs no network I/O, so nothing here can track the
# market on its own.
#
# Measured 2026-11-21 against the US Treasury par-yield curve (EODHD `ust/yield-rates`, curve dated
# 2026-11-19): the 10-year was 5.04%, against the 4.00% below — a 1.04pp gap. With beta 1.2, Rf 4.00%
# and a 6.00% ERP the rate is 11.20%; holding that ERP while marking Rf to 5.04% — so Rm becomes
# 11.04% — gives 12.24%, and discounting a level five-year stream at 11.20% overstates its present
# value by 2.62%, more on anything with a longer tail. `capm_discount_rate` has no default arguments:
# passing risk_free_rate=0.0504 with market_return=0.10 (the value of DEFAULT_MARKET_RETURN) gives
# 10.99%, not 12.24 — the ERP is what is held fixed above.
#
# Kept as they are on purpose: nothing in this library imports them (callers pass their own rate), so
# changing them would not move an output here; the exposure is a consumer that copied 0.04 and 0.06
# into its own call. To refresh, `GET https://eodhd.com/api/ust/yield-rates?api_token=…`
# and read the latest dated curve; the equity risk premium is a judgement, not a quote.
DEFAULT_RISK_FREE_RATE: Final[float] = 0.04
DEFAULT_EQUITY_RISK_PREMIUM: Final[float] = 0.06
DEFAULT_TAX_RATE: Final[float] = 0.25
DEFAULT_MARKET_RETURN: Final[float] = DEFAULT_RISK_FREE_RATE + DEFAULT_EQUITY_RISK_PREMIUM  # 0.10

# Industry-specific discount rate ranges (WACC ranges by sector)
INDUSTRY_DISCOUNT_RANGES: Final[dict[str, dict[str, float]]] = {
    "technology": {"min": 0.12, "max": 0.20, "median": 0.15},
    "healthcare": {"min": 0.10, "max": 0.18, "median": 0.14},
    "financial_services": {"min": 0.08, "max": 0.14, "median": 0.11},
    "consumer_goods": {"min": 0.08, "max": 0.15, "median": 0.12},
    "industrials": {"min": 0.08, "max": 0.14, "median": 0.11},
    "energy": {"min": 0.09, "max": 0.16, "median": 0.12},
    "real_estate": {"min": 0.07, "max": 0.12, "median": 0.09},
    "telecommunications": {"min": 0.08, "max": 0.14, "median": 0.11},
    "utilities": {"min": 0.06, "max": 0.10, "median": 0.08},
    "materials": {"min": 0.09, "max": 0.15, "median": 0.12},
}

# Asset type default useful lives (years)
DEFAULT_USEFUL_LIVES: Final[dict[str, dict[str, float | None]]] = {
    "patent": {"legal_max": 20, "economic_typical": 10, "tech_obsolescence_rate": 0.10},
    "trademark": {"legal_max": float("inf"), "economic_typical": 20, "tech_obsolescence_rate": 0.02},
    "copyright": {"legal_max": 70, "economic_typical": 25, "tech_obsolescence_rate": 0.05},
    "trade_secret": {"legal_max": float("inf"), "economic_typical": 15, "tech_obsolescence_rate": 0.08},
    "customer_relationship": {"legal_max": float("inf"), "economic_typical": 12, "tech_obsolescence_rate": 0.05},
    "software": {"legal_max": float("inf"), "economic_typical": 5, "tech_obsolescence_rate": 0.15},
    "brand": {"legal_max": float("inf"), "economic_typical": 20, "tech_obsolescence_rate": 0.03},
    "license": {"legal_max": None, "economic_typical": 10, "tech_obsolescence_rate": 0.05},
    "goodwill": {"legal_max": float("inf"), "economic_typical": float("inf"), "tech_obsolescence_rate": 0.0},
}

# Default size premiums (based on company market cap)
SIZE_PREMIUMS: Final[dict[str, float]] = {
    "micro_cap": 0.06,
    "small_cap": 0.04,
    "mid_cap": 0.02,
    "large_cap": 0.0,
}

# Default country risk premiums (selected countries)
COUNTRY_RISK_PREMIUMS: Final[dict[str, float]] = {
    "US": 0.0,
    "UK": 0.01,
    "Germany": 0.01,
    "Japan": 0.01,
    "China": 0.03,
    "India": 0.04,
    "Brazil": 0.05,
    "Russia": 0.06,
    "South_Africa": 0.04,
    "Mexico": 0.03,
    "Canada": 0.005,
    "Australia": 0.01,
    "France": 0.01,
    "South_Korea": 0.02,
    "Singapore": 0.01,
    "Indonesia": 0.04,
    "Thailand": 0.03,
    "Vietnam": 0.05,
    "Philippines": 0.04,
    "Turkey": 0.06,
    "Argentina": 0.08,
    "Nigeria": 0.07,
    "Egypt": 0.05,
    "Saudi_Arabia": 0.03,
    "UAE": 0.02,
    "Poland": 0.02,
    "Czech_Republic": 0.015,
    "Hungary": 0.02,
    "Chile": 0.03,
    "Colombia": 0.04,
    "Peru": 0.03,
}

# Royalty rate benchmarks by industry and IP type
# Source: RoyaltyStat, ktMINE, and industry surveys
ROYALTY_RATE_BENCHMARKS: Final[dict[str, dict[str, dict[str, float | str]]]] = {
    "technology": {
        "patent": {"low": 0.01, "median": 0.03, "high": 0.07, "typical_range": "1-7%"},
        "software": {"low": 0.05, "median": 0.10, "high": 0.20, "typical_range": "5-20%"},
        "trade_secret": {"low": 0.02, "median": 0.05, "high": 0.10, "typical_range": "2-10%"},
        "know_how": {"low": 0.02, "median": 0.04, "high": 0.08, "typical_range": "2-8%"},
    },
    "pharmaceuticals": {
        "patent": {"low": 0.03, "median": 0.08, "high": 0.15, "typical_range": "3-15%"},
        "trade_secret": {"low": 0.02, "median": 0.05, "high": 0.10, "typical_range": "2-10%"},
        "know_how": {"low": 0.03, "median": 0.06, "high": 0.12, "typical_range": "3-12%"},
    },
    "consumer_goods": {
        "trademark": {"low": 0.02, "median": 0.05, "high": 0.10, "typical_range": "2-10%"},
        "brand": {"low": 0.03, "median": 0.06, "high": 0.12, "typical_range": "3-12%"},
        "patent": {"low": 0.01, "median": 0.03, "high": 0.05, "typical_range": "1-5%"},
    },
    "industrial": {
        "patent": {"low": 0.01, "median": 0.03, "high": 0.06, "typical_range": "1-6%"},
        "trade_secret": {"low": 0.01, "median": 0.03, "high": 0.05, "typical_range": "1-5%"},
        "know_how": {"low": 0.01, "median": 0.02, "high": 0.05, "typical_range": "1-5%"},
    },
    "media_entertainment": {
        "copyright": {"low": 0.05, "median": 0.10, "high": 0.20, "typical_range": "5-20%"},
        "trademark": {"low": 0.03, "median": 0.07, "high": 0.15, "typical_range": "3-15%"},
        "brand": {"low": 0.04, "median": 0.08, "high": 0.15, "typical_range": "4-15%"},
    },
    "healthcare_devices": {
        "patent": {"low": 0.02, "median": 0.05, "high": 0.10, "typical_range": "2-10%"},
        "trade_secret": {"low": 0.01, "median": 0.03, "high": 0.07, "typical_range": "1-7%"},
        "know_how": {"low": 0.02, "median": 0.04, "high": 0.08, "typical_range": "2-8%"},
    },
    "automotive": {
        "patent": {"low": 0.01, "median": 0.02, "high": 0.05, "typical_range": "1-5%"},
        "trade_secret": {"low": 0.01, "median": 0.02, "high": 0.04, "typical_range": "1-4%"},
        "trademark": {"low": 0.01, "median": 0.03, "high": 0.05, "typical_range": "1-5%"},
    },
    "food_beverage": {
        "trademark": {"low": 0.02, "median": 0.05, "high": 0.10, "typical_range": "2-10%"},
        "brand": {"low": 0.03, "median": 0.06, "high": 0.12, "typical_range": "3-12%"},
        "patent": {"low": 0.01, "median": 0.02, "high": 0.05, "typical_range": "1-5%"},
    },
}

# Industry average profit margins (operating margin ranges)
INDUSTRY_PROFIT_MARGINS: Final[dict[str, dict[str, float]]] = {
    "software_saas": {"low": 0.10, "median": 0.20, "high": 0.35},
    "technology_hardware": {"low": 0.05, "median": 0.10, "high": 0.18},
    "pharmaceuticals": {"low": 0.15, "median": 0.25, "high": 0.40},
    "biotechnology": {"low": -0.10, "median": 0.05, "high": 0.25},
    "medical_devices": {"low": 0.10, "median": 0.18, "high": 0.30},
    "consumer_goods": {"low": 0.05, "median": 0.10, "high": 0.20},
    "retail": {"low": 0.02, "median": 0.05, "high": 0.10},
    "automotive": {"low": 0.03, "median": 0.07, "high": 0.12},
    "aerospace_defense": {"low": 0.06, "median": 0.10, "high": 0.15},
    "financial_services": {"low": 0.15, "median": 0.25, "high": 0.40},
    "real_estate": {"low": 0.10, "median": 0.20, "high": 0.35},
    "energy_oil_gas": {"low": 0.05, "median": 0.12, "high": 0.25},
    "utilities": {"low": 0.08, "median": 0.15, "high": 0.22},
    "telecommunications": {"low": 0.08, "median": 0.15, "high": 0.25},
    "media_entertainment": {"low": 0.05, "median": 0.12, "high": 0.25},
    "food_beverage": {"low": 0.05, "median": 0.10, "high": 0.18},
    "industrial_manufacturing": {"low": 0.04, "median": 0.08, "high": 0.15},
    "construction": {"low": 0.02, "median": 0.05, "high": 0.10},
    "transportation": {"low": 0.03, "median": 0.07, "high": 0.12},
    "healthcare_services": {"low": 0.05, "median": 0.10, "high": 0.18},
}

# Typical useful life ranges by asset type (refined ranges for amortization)
USEFUL_LIFE_RANGES: Final[dict[str, dict[str, float]]] = {
    "patent_invention": {"min": 5, "max": 20, "typical": 10},
    "patent_design": {"min": 5, "max": 15, "typical": 8},
    "trademark_registered": {"min": 10, "max": float("inf"), "typical": 20},
    "trademark_unregistered": {"min": 3, "max": 15, "typical": 7},
    "copyright_literary": {"min": 10, "max": 50, "typical": 25},
    "copyright_software": {"min": 3, "max": 10, "typical": 5},
    "copyright_media": {"min": 5, "max": 30, "typical": 15},
    "trade_secret_formula": {"min": 5, "max": 25, "typical": 15},
    "trade_secret_process": {"min": 3, "max": 15, "typical": 8},
    "customer_relationship_contractual": {"min": 3, "max": 15, "typical": 7},
    "customer_relationship_non_contractual": {"min": 2, "max": 10, "typical": 5},
    "customer_database": {"min": 2, "max": 8, "typical": 4},
    "brand_established": {"min": 10, "max": float("inf"), "typical": 20},
    "brand_emerging": {"min": 3, "max": 10, "typical": 5},
    "software_developed": {"min": 2, "max": 7, "typical": 4},
    "software_purchased": {"min": 3, "max": 10, "typical": 5},
    "license_exclusive": {"min": 3, "max": 20, "typical": 10},
    "license_non_exclusive": {"min": 2, "max": 10, "typical": 5},
    "assembled_workforce": {"min": 2, "max": 7, "typical": 4},
    "goodwill": {"min": 10, "max": float("inf"), "typical": float("inf")},
    "domain_name": {"min": 3, "max": 15, "typical": 7},
    "data_database": {"min": 2, "max": 8, "typical": 4},
    "permit_license_government": {"min": 1, "max": 20, "typical": 10},
}

# Valuation method identifiers
METHOD_GORDON_GROWTH: Final[str] = "gordon_growth"
METHOD_EXIT_MULTIPLE: Final[str] = "exit_multiple"
METHOD_CAPM: Final[str] = "capm"
METHOD_BUILD_UP: Final[str] = "build_up"
METHOD_WACC: Final[str] = "wacc"
METHOD_FINNERTY: Final[str] = "finnerty"
