"""GigSaathi — India Tax Rules Module (FY 2025-26 / AY 2026-27).

Provides pure-Python tax computation utilities for Indian gig workers
covering income-tax slabs (New Regime), presumptive taxation under
Section 44ADA, advance tax scheduling, occupation-specific deductions,
and TDS rate look-ups.

Usage::

    from app.tax_rules import calculate_tax_on_income, apply_44ADA

    result = calculate_tax_on_income(12_00_000)
    print(result["total_tax"])

Submodules:
    - ``slabs``        — FY 2025-26 New Regime slab rates & tax calc
    - ``presumptive``  — Section 44ADA eligibility & deemed profit
    - ``advance_tax``  — Quarterly / single-installment schedules
    - ``deductions``   — Occupation-wise deductions & TDS rates
"""

# -- slabs.py ---------------------------------------------------------------
from app.tax_rules.slabs import (
    ASSESSMENT_YEAR,
    CESS_RATE,
    FINANCIAL_YEAR,
    REBATE_87A_LIMIT,
    REBATE_87A_MAX,
    SLABS,
    calculate_tax_on_income,
)

# -- presumptive.py ---------------------------------------------------------
from app.tax_rules.presumptive import (
    DEEMED_PROFIT_RATE,
    THRESHOLD_DIGITAL,
    THRESHOLD_NON_DIGITAL,
    apply_44ADA,
    is_eligible_44ADA,
)

# -- advance_tax.py ---------------------------------------------------------
from app.tax_rules.advance_tax import (
    ADVANCE_TAX_THRESHOLD,
    INTEREST_234B_RATE,
    INTEREST_234C_RATE,
    get_advance_tax_schedule,
)

# -- deductions.py ----------------------------------------------------------
from app.tax_rules.deductions import (
    get_applicable_deductions,
    get_tds_rates,
)

__all__ = [
    # slabs
    "SLABS",
    "REBATE_87A_LIMIT",
    "REBATE_87A_MAX",
    "CESS_RATE",
    "FINANCIAL_YEAR",
    "ASSESSMENT_YEAR",
    "calculate_tax_on_income",
    # presumptive
    "THRESHOLD_DIGITAL",
    "THRESHOLD_NON_DIGITAL",
    "DEEMED_PROFIT_RATE",
    "is_eligible_44ADA",
    "apply_44ADA",
    # advance tax
    "ADVANCE_TAX_THRESHOLD",
    "INTEREST_234B_RATE",
    "INTEREST_234C_RATE",
    "get_advance_tax_schedule",
    # deductions
    "get_applicable_deductions",
    "get_tds_rates",
]
