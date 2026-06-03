"""Income tax slabs and calculation for FY 2025-26 (AY 2026-27) — New Tax Regime.

This module implements the new tax regime slabs as applicable for
Financial Year 2025-26 including Section 87A rebate and Health &
Education Cess.

References:
    - Finance Act 2025 — Section 115BAC
    - Section 87A rebate for income up to ₹12,00,000
"""

from typing import Any

# ---------------------------------------------------------------------------
# FY 2025-26 New Tax Regime Slabs
# ---------------------------------------------------------------------------
# Each tuple: (lower_bound, upper_bound_or_None, rate, label)
SLABS: list[tuple[float, float | None, float, str]] = [
    (0,         4_00_000,  0.00, "₹0 – ₹4,00,000"),
    (4_00_000,  8_00_000,  0.05, "₹4,00,001 – ₹8,00,000"),
    (8_00_000,  12_00_000, 0.10, "₹8,00,001 – ₹12,00,000"),
    (12_00_000, 16_00_000, 0.15, "₹12,00,001 – ₹16,00,000"),
    (16_00_000, 20_00_000, 0.20, "₹16,00,001 – ₹20,00,000"),
    (20_00_000, 24_00_000, 0.25, "₹20,00,001 – ₹24,00,000"),
    (24_00_000, None,      0.30, "Above ₹24,00,000"),
]

# Section 87A rebate — max ₹60,000 for taxable income up to ₹12,00,000
REBATE_87A_LIMIT: float = 12_00_000
REBATE_87A_MAX: float = 60_000

# Health & Education Cess
CESS_RATE: float = 0.04

FINANCIAL_YEAR: str = "2025-26"
ASSESSMENT_YEAR: str = "2026-27"


def calculate_tax_on_income(taxable_income: float) -> dict[str, Any]:
    """Calculate income tax under the New Tax Regime for FY 2025-26.

    Applies the seven-slab structure, Section 87A rebate (for income
    up to ₹12 lakh), and 4 % Health & Education Cess.

    Args:
        taxable_income: Total taxable income in INR (after all
            applicable deductions).  Must be ≥ 0.

    Returns:
        A dict containing:
            - ``tax_before_cess`` (float): Tax after rebate, before cess.
            - ``cess`` (float): 4 % Health & Education Cess.
            - ``total_tax`` (float): Final tax payable (rounded to nearest ₹).
            - ``effective_rate`` (float): Effective tax rate as a percentage.
            - ``rebate_87A`` (float): Rebate amount applied under Sec 87A.
            - ``slab_breakdown`` (list[dict]): Per-slab detail with keys
              ``slab``, ``rate``, ``taxable_amount``, ``tax``.
            - ``financial_year`` (str): ``"2025-26"``.
            - ``assessment_year`` (str): ``"2026-27"``.

    Raises:
        ValueError: If *taxable_income* is negative.

    Examples:
        >>> result = calculate_tax_on_income(10_00_000)
        >>> result["total_tax"]
        0.0
        >>> result = calculate_tax_on_income(15_00_000)
        >>> result["total_tax"] > 0
        True
    """
    if taxable_income < 0:
        raise ValueError("taxable_income must be non-negative")

    taxable_income = float(taxable_income)

    # ---- Step 1: compute slab-wise tax ----
    slab_breakdown: list[dict[str, Any]] = []
    gross_tax: float = 0.0

    for lower, upper, rate, label in SLABS:
        if taxable_income <= lower:
            # Income does not reach this slab
            slab_breakdown.append({
                "slab": label,
                "rate": rate,
                "taxable_amount": 0.0,
                "tax": 0.0,
            })
            continue

        if upper is None:
            # Last (uncapped) slab
            taxable_in_slab = taxable_income - lower
        else:
            taxable_in_slab = min(taxable_income, upper) - lower

        tax_in_slab = round(taxable_in_slab * rate, 2)
        gross_tax += tax_in_slab

        slab_breakdown.append({
            "slab": label,
            "rate": rate,
            "taxable_amount": round(taxable_in_slab, 2),
            "tax": tax_in_slab,
        })

    # ---- Step 2: Section 87A rebate ----
    rebate: float = 0.0
    if taxable_income <= REBATE_87A_LIMIT:
        rebate = min(gross_tax, REBATE_87A_MAX)

    tax_after_rebate = round(gross_tax - rebate, 2)

    # ---- Step 3: Health & Education Cess ----
    cess = round(tax_after_rebate * CESS_RATE, 2)
    total_tax = round(tax_after_rebate + cess)

    # ---- Step 4: effective rate ----
    effective_rate = round((total_tax / taxable_income) * 100, 2) if taxable_income > 0 else 0.0

    return {
        "tax_before_cess": tax_after_rebate,
        "cess": cess,
        "total_tax": total_tax,
        "effective_rate": effective_rate,
        "rebate_87A": rebate,
        "gross_tax_before_rebate": round(gross_tax, 2),
        "slab_breakdown": slab_breakdown,
        "financial_year": FINANCIAL_YEAR,
        "assessment_year": ASSESSMENT_YEAR,
    }
