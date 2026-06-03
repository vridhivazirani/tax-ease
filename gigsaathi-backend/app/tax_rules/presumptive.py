"""Presumptive taxation under Section 44ADA for professionals.

Section 44ADA allows eligible professionals with gross receipts up to
a prescribed threshold to declare 50 % of gross receipts as deemed
profit — removing the need to maintain books of account.

Thresholds (FY 2025-26):
    - ₹75,00,000 when ≥ 95 % of receipts are through digital/banking
      channels.
    - ₹50,00,000 otherwise.

References:
    - Section 44ADA of the Income-tax Act, 1961
    - Finance Act 2023 — enhanced limits for digital receipts
"""

from typing import Any

# ---------------------------------------------------------------------------
# 44ADA Thresholds
# ---------------------------------------------------------------------------
THRESHOLD_DIGITAL: float = 75_00_000   # ₹75 lakh — digital receipts ≥ 95 %
THRESHOLD_NON_DIGITAL: float = 50_00_000  # ₹50 lakh — otherwise
DEEMED_PROFIT_RATE: float = 0.50       # 50 % of gross receipts


def is_eligible_44ADA(gross_income: float, is_digital: bool = True) -> bool:
    """Check if a professional is eligible for Section 44ADA.

    Eligibility depends on gross receipts not exceeding the applicable
    threshold.

    Args:
        gross_income: Total gross professional receipts in INR for the
            financial year.  Must be ≥ 0.
        is_digital: ``True`` if ≥ 95 % of receipts are received via
            digital / banking channels (UPI, bank transfer, etc.),
            enabling the higher ₹75 lakh threshold.  Defaults to
            ``True``.

    Returns:
        ``True`` if gross receipts are within the applicable threshold,
        ``False`` otherwise.

    Raises:
        ValueError: If *gross_income* is negative.

    Examples:
        >>> is_eligible_44ADA(40_00_000)
        True
        >>> is_eligible_44ADA(60_00_000, is_digital=False)
        False
    """
    if gross_income < 0:
        raise ValueError("gross_income must be non-negative")

    threshold = THRESHOLD_DIGITAL if is_digital else THRESHOLD_NON_DIGITAL
    return gross_income <= threshold


def apply_44ADA(
    gross_income: float,
    is_digital: bool = True,
) -> dict[str, Any]:
    """Apply Section 44ADA presumptive taxation and return a summary.

    If the professional is eligible, deemed profit is computed at 50 %
    of gross receipts.  Remaining 50 % is treated as deemed expenses
    and no further deductions (other than salary/interest to partners,
    if any) are allowed.

    Args:
        gross_income: Total gross professional receipts in INR.
            Must be ≥ 0.
        is_digital: ``True`` if ≥ 95 % of receipts are through
            digital / banking channels.  Defaults to ``True``.

    Returns:
        A dict with:
            - ``eligible`` (bool): Whether 44ADA can be opted.
            - ``gross_income`` (float): Echo of the input.
            - ``deemed_profit`` (float): 50 % of gross receipts (or 0.0
              if ineligible).
            - ``deemed_expenses`` (float): Remaining 50 % deemed as
              expenses (or 0.0 if ineligible).
            - ``deemed_profit_rate`` (float): The deemed profit rate
              (0.50).
            - ``threshold_used`` (float): The threshold applied based
              on *is_digital*.
            - ``is_digital`` (bool): Echo of the flag.
            - ``note`` (str): Human-readable explanation.

    Raises:
        ValueError: If *gross_income* is negative.

    Examples:
        >>> result = apply_44ADA(30_00_000)
        >>> result["deemed_profit"]
        1500000.0
        >>> result["eligible"]
        True
    """
    if gross_income < 0:
        raise ValueError("gross_income must be non-negative")

    gross_income = float(gross_income)
    threshold = THRESHOLD_DIGITAL if is_digital else THRESHOLD_NON_DIGITAL
    eligible = gross_income <= threshold

    if eligible:
        deemed_profit = round(gross_income * DEEMED_PROFIT_RATE, 2)
        deemed_expenses = round(gross_income - deemed_profit, 2)
        note = (
            f"Under Section 44ADA, 50 % of gross receipts "
            f"(₹{deemed_profit:,.0f}) is deemed as taxable profit. "
            f"No separate expense deductions can be claimed. "
            f"Advance tax must be paid in a single installment by "
            f"March 15 of the financial year."
        )
    else:
        deemed_profit = 0.0
        deemed_expenses = 0.0
        digital_label = "digital" if is_digital else "non-digital"
        note = (
            f"Gross receipts of ₹{gross_income:,.0f} exceed the "
            f"₹{threshold:,.0f} threshold for {digital_label} "
            f"payments. Section 44ADA cannot be opted. You must "
            f"maintain books of account and file under normal "
            f"provisions (ITR-3). Consider consulting a CA."
        )

    return {
        "eligible": eligible,
        "gross_income": gross_income,
        "deemed_profit": deemed_profit,
        "deemed_expenses": deemed_expenses,
        "deemed_profit_rate": DEEMED_PROFIT_RATE,
        "threshold_used": threshold,
        "is_digital": is_digital,
        "note": note,
    }
