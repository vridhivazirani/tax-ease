"""Pydantic v2 models for tax calculations and summaries."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaxCalculation(BaseModel):
    """Detailed tax computation for a user in a given financial year.

    Attributes:
        user_id: Identifier of the user.
        financial_year: Financial year string (e.g. ``2025-26``).
        gross_income: Total gross income for the year.
        presumptive_income: 50 % of gross if Section 44ADA applies, else ``None``.
        total_deductions: Sum of all deductions (Chapter VI-A, etc.).
        taxable_income: Income on which tax is computed.
        tax_before_cess: Tax amount before health & education cess.
        cess: 4 % health & education cess.
        total_tax_liability: Tax after cess.
        tds_already_deducted: TDS credited from income records.
        advance_tax_paid: Any advance tax the user has already paid.
        net_payable: Final amount payable (negative means refund).
        section_44ADA_applied: Whether 44ADA was used in this computation.
        regime: Tax regime — ``new`` or ``old``.
        slab_breakdown: Ordered list of slab dicts with ``range``, ``rate``,
            ``amount`` keys.
        last_updated: Timestamp of the latest recalculation.
    """

    model_config = ConfigDict(populate_by_name=True)

    user_id: str
    financial_year: str = "2025-26"
    gross_income: float
    presumptive_income: float | None = None
    total_deductions: float = 0.0
    taxable_income: float
    tax_before_cess: float
    cess: float  # 4 %
    total_tax_liability: float
    tds_already_deducted: float
    advance_tax_paid: float = 0.0
    net_payable: float  # negative ⇒ refund
    section_44ADA_applied: bool = False
    regime: str = "new"
    slab_breakdown: list[dict]
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class TaxSummaryResponse(BaseModel):
    """Simplified tax summary returned by the API.

    Provides the key numbers a user cares about without the full slab
    detail.

    Attributes:
        user_id: Identifier of the user.
        financial_year: Financial year string.
        gross_income: Total gross income.
        taxable_income: Income on which tax is computed.
        total_tax_liability: Tax payable after cess.
        tds_already_deducted: TDS already credited.
        advance_tax_paid: Advance tax paid.
        net_payable: Remaining amount to pay (negative ⇒ refund).
        regime: Tax regime used.
        section_44ADA_applied: Whether 44ADA was applied.
    """

    user_id: str
    financial_year: str
    gross_income: float
    taxable_income: float
    total_tax_liability: float
    tds_already_deducted: float
    advance_tax_paid: float = 0.0
    net_payable: float
    regime: str = "new"
    section_44ADA_applied: bool = False
