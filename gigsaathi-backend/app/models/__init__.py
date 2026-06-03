"""Pydantic models package — re-exports all domain models for convenience.

Usage::

    from app.models import IncomeRecord, UserProfile, TaxCalculation
"""

from app.models.income import (
    IncomeRecord,
    IncomeRecordResponse,
    IncomeSummary,
    MonthlyBreakdown,
    PlatformBreakdown,
)
from app.models.tax import TaxCalculation, TaxSummaryResponse
from app.models.user import UserProfile, UserProfileCreate, UserProfileResponse

__all__ = [
    # Income
    "IncomeRecord",
    "IncomeRecordResponse",
    "IncomeSummary",
    "MonthlyBreakdown",
    "PlatformBreakdown",
    # Tax
    "TaxCalculation",
    "TaxSummaryResponse",
    # User
    "UserProfile",
    "UserProfileCreate",
    "UserProfileResponse",
]
