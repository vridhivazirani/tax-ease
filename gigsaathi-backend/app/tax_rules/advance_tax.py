"""Advance tax schedule, deadlines, and interest provisions.

Implements quarterly advance tax installments for regular taxpayers
and the single-installment rule for professionals under Section 44ADA.

Interest provisions:
    - **Section 234B**: 1 % per month (simple) if less than 90 % of
      assessed tax is paid as advance tax by 31 March.
    - **Section 234C**: 1 % per month (simple) for shortfall /
      deferment at each quarterly installment.

References:
    - Sections 208, 210, 211 of the Income-tax Act, 1961
    - Sections 234B, 234C — interest on defaults
"""

import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Advance Tax Configuration — FY 2025-26
# ---------------------------------------------------------------------------
ADVANCE_TAX_THRESHOLD: float = 10_000  # ₹10,000

# Regular quarterly schedule: (label, month, day, cumulative %)
REGULAR_SCHEDULE: list[tuple[str, int, int, float]] = [
    ("1st Installment", 6, 15, 0.15),   # June 15 — 15 %
    ("2nd Installment", 9, 15, 0.45),   # September 15 — 45 %
    ("3rd Installment", 12, 15, 0.75),  # December 15 — 75 %
    ("4th Installment", 3, 15, 1.00),   # March 15 — 100 %
]

# 44ADA presumptive: single installment
PRESUMPTIVE_SCHEDULE: list[tuple[str, int, int, float]] = [
    ("Single Installment (44ADA)", 3, 15, 1.00),  # March 15 — 100 %
]

# Interest rates
INTEREST_234B_RATE: float = 0.01  # 1 % per month
INTEREST_234C_RATE: float = 0.01  # 1 % per month


def _build_deadline(
    label: str,
    month: int,
    day: int,
    cumulative_pct: float,
    total_liability: float,
    fy_start_year: int,
    today: datetime.date,
) -> dict[str, Any]:
    """Build a single deadline entry.

    Args:
        label: Human-readable installment label.
        month: Calendar month of the due date.
        day: Calendar day of the due date.
        cumulative_pct: Cumulative percentage due by this date.
        total_liability: Total advance tax liability in INR.
        fy_start_year: Calendar year in which the FY starts (e.g. 2025
            for FY 2025-26).
        today: Reference date for past/future checks.

    Returns:
        Dict with deadline details.
    """
    # FY runs April → March.  Months Apr-Dec fall in fy_start_year,
    # Jan-Mar fall in fy_start_year + 1.
    year = fy_start_year if month >= 4 else fy_start_year + 1
    due_date = datetime.date(year, month, day)

    is_past = today > due_date
    days_remaining = max((due_date - today).days, 0) if not is_past else 0

    return {
        "label": label,
        "due_date": due_date.isoformat(),
        "cumulative_pct": cumulative_pct,
        "cumulative_pct_display": f"{cumulative_pct * 100:.0f}%",
        "amount_due": round(total_liability * cumulative_pct, 2),
        "is_past": is_past,
        "days_remaining": days_remaining,
    }


def get_advance_tax_schedule(
    total_liability: float,
    financial_year: str = "2025-26",
    opted_44ADA: bool = False,
) -> dict[str, Any]:
    """Generate the advance tax payment schedule for a financial year.

    For regular taxpayers the schedule has four quarterly installments.
    For professionals under Section 44ADA, a single installment
    (100 %) is due by 15 March.

    Advance tax is not required if total tax liability for the year is
    below ₹10,000 (after TDS).

    Args:
        total_liability: Total estimated tax liability for the year
            in INR (after TDS deductions).  Must be ≥ 0.
        financial_year: FY in ``"YYYY-YY"`` format, e.g. ``"2025-26"``.
            Defaults to ``"2025-26"``.
        opted_44ADA: ``True`` if the taxpayer has opted for presumptive
            taxation under Section 44ADA.  Defaults to ``False``.

    Returns:
        A dict with:
            - ``financial_year`` (str): The FY string.
            - ``total_liability`` (float): Echo of input.
            - ``threshold`` (float): ₹10,000.
            - ``threshold_met`` (bool): ``True`` if liability ≥ threshold.
            - ``is_presumptive`` (bool): Whether 44ADA schedule applies.
            - ``deadlines`` (list[dict]): Ordered list of installment
              deadlines, each containing ``label``, ``due_date``,
              ``cumulative_pct``, ``cumulative_pct_display``,
              ``amount_due``, ``is_past``, ``days_remaining``.
            - ``interest_provisions`` (dict): Summary of Sec 234B and
              234C interest rules.
            - ``note`` (str): Human-readable guidance.

    Raises:
        ValueError: If *total_liability* is negative or
            *financial_year* format is invalid.

    Examples:
        >>> schedule = get_advance_tax_schedule(50_000)
        >>> len(schedule["deadlines"])
        4
        >>> schedule["threshold_met"]
        True

        >>> schedule = get_advance_tax_schedule(50_000, opted_44ADA=True)
        >>> len(schedule["deadlines"])
        1
    """
    if total_liability < 0:
        raise ValueError("total_liability must be non-negative")

    # Parse financial year
    parts = financial_year.split("-")
    if len(parts) != 2:
        raise ValueError(
            f"financial_year must be in 'YYYY-YY' format, got '{financial_year}'"
        )
    try:
        fy_start_year = int(parts[0])
    except ValueError as exc:
        raise ValueError(
            f"Invalid financial_year format: '{financial_year}'"
        ) from exc

    total_liability = float(total_liability)
    threshold_met = total_liability >= ADVANCE_TAX_THRESHOLD
    today = datetime.date.today()

    # Choose schedule
    schedule = PRESUMPTIVE_SCHEDULE if opted_44ADA else REGULAR_SCHEDULE

    deadlines: list[dict[str, Any]] = []
    for label, month, day, cum_pct in schedule:
        deadlines.append(
            _build_deadline(
                label=label,
                month=month,
                day=day,
                cumulative_pct=cum_pct,
                total_liability=total_liability,
                fy_start_year=fy_start_year,
                today=today,
            )
        )

    # Interest provisions (informational)
    interest_provisions = {
        "section_234B": {
            "description": (
                "Interest at 1% per month (simple) on shortfall if "
                "less than 90% of assessed tax is paid as advance tax "
                "by 31 March."
            ),
            "rate_per_month": INTEREST_234B_RATE,
            "trigger": "Advance tax paid < 90% of assessed tax",
        },
        "section_234C": {
            "description": (
                "Interest at 1% per month (simple) for shortfall or "
                "deferment at each quarterly installment due date."
            ),
            "rate_per_month": INTEREST_234C_RATE,
            "trigger": "Shortfall at any installment due date",
        },
    }

    # Human-readable note
    if not threshold_met:
        note = (
            f"Your estimated tax liability of ₹{total_liability:,.0f} "
            f"is below the ₹{ADVANCE_TAX_THRESHOLD:,.0f} threshold. "
            f"Advance tax is not required — you can pay the entire "
            f"amount as self-assessment tax at the time of filing."
        )
    elif opted_44ADA:
        note = (
            f"As a 44ADA taxpayer, you must pay 100% of your advance "
            f"tax (₹{total_liability:,.0f}) in a single installment "
            f"by 15 March {fy_start_year + 1}. Missing this deadline "
            f"attracts interest under Sec 234B and 234C."
        )
    else:
        next_deadline = next(
            (d for d in deadlines if not d["is_past"]),
            None,
        )
        if next_deadline:
            note = (
                f"Your next advance tax installment of "
                f"₹{next_deadline['amount_due']:,.0f} "
                f"({next_deadline['cumulative_pct_display']} cumulative) "
                f"is due on {next_deadline['due_date']}. "
                f"You have {next_deadline['days_remaining']} day(s) remaining."
            )
        else:
            note = (
                "All advance tax installments for this financial year "
                "are past due. Please pay any outstanding amount "
                "immediately to minimise interest under Sec 234B/234C."
            )

    return {
        "financial_year": financial_year,
        "total_liability": total_liability,
        "threshold": ADVANCE_TAX_THRESHOLD,
        "threshold_met": threshold_met,
        "is_presumptive": opted_44ADA,
        "deadlines": deadlines,
        "interest_provisions": interest_provisions,
        "note": note,
    }
