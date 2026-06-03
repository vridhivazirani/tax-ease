"""Pydantic v2 models for income records, summaries, and breakdowns."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ------------------------------------------------------------------
# Breakdown helpers (defined first so IncomeSummary can reference them)
# ------------------------------------------------------------------


class PlatformBreakdown(BaseModel):
    """Aggregated income figures for a single platform.

    Attributes:
        platform: Platform identifier (e.g. ``swiggy``, ``uber``).
        gross_income: Total gross income from this platform.
        tds_deducted: Total TDS deducted by this platform.
        net_income: Gross minus TDS.
        record_count: Number of income records from this platform.
    """

    platform: str
    gross_income: float
    tds_deducted: float
    net_income: float
    record_count: int


class MonthlyBreakdown(BaseModel):
    """Aggregated income figures for a single calendar month.

    Attributes:
        month: Month string in ``YYYY-MM`` format.
        gross_income: Total gross income in this month.
        tds_deducted: Total TDS deducted in this month.
        net_income: Gross minus TDS.
        record_count: Number of income records in this month.
    """

    month: str  # YYYY-MM
    gross_income: float
    tds_deducted: float
    net_income: float
    record_count: int


# ------------------------------------------------------------------
# Core income models
# ------------------------------------------------------------------


class IncomeRecord(BaseModel):
    """A single income transaction extracted from a payment statement.

    Attributes:
        user_id: Identifier of the user who owns this record.
        platform: Source platform (swiggy, uber, upwork, fiverr, bank, other).
        amount: Gross amount in INR.
        tds_deducted: TDS already withheld at source.
        payment_date: Date/time of the payment.
        source_pdf_name: Original PDF filename the record was extracted from.
        description: Free-text note about this transaction.
        is_duplicate: Whether this record is flagged as a duplicate.
        duplicate_of: ``ObjectId`` string of the primary record if duplicate.
        created_at: Timestamp when the record was created.
    """

    model_config = ConfigDict(populate_by_name=True)

    user_id: str
    platform: str
    amount: float
    tds_deducted: float = 0.0
    payment_date: datetime
    source_pdf_name: str
    description: str = ""
    is_duplicate: bool = False
    duplicate_of: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IncomeRecordResponse(IncomeRecord):
    """Income record enriched with the MongoDB document ``_id``.

    Attributes:
        id: MongoDB ``_id`` serialised as a string.
    """

    id: str  # MongoDB _id as string


class IncomeSummary(BaseModel):
    """Aggregated income summary for a financial year.

    Attributes:
        total_gross_income: Sum of all gross amounts.
        total_tds_deducted: Sum of all TDS deductions.
        total_net_income: Gross minus TDS.
        by_platform: Per-platform breakdown.
        by_month: Per-month breakdown.
        record_count: Total number of income records.
        financial_year: Financial year string (e.g. ``2025-26``).
    """

    total_gross_income: float
    total_tds_deducted: float
    total_net_income: float
    by_platform: list[PlatformBreakdown]
    by_month: list[MonthlyBreakdown]
    record_count: int
    financial_year: str
