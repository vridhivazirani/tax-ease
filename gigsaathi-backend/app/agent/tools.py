"""GigSaathi — Agent Tools.

Five callable functions that the Gemini agent uses to fetch real data
and perform calculations. Each function has clear type hints and Google-style
docstrings so Gemini understands when and how to call them.

Tools:
    1. get_income_summary() — Fetch user's income breakdown
    2. calculate_tax() — Compute tax liability
    3. find_deductions() — Surface claimable deductions
    4. generate_itr_summary() — Produce ITR-4 field mapping
    5. check_deadlines() — Alert on advance tax deadlines
"""

from datetime import datetime

from app.db.database import mongodb
from app.tax_rules.slabs import calculate_tax_on_income
from app.tax_rules.presumptive import apply_44ADA, is_eligible_44ADA
from app.tax_rules.advance_tax import get_advance_tax_schedule
from app.tax_rules.deductions import get_applicable_deductions


# ════════════════════════════════════════════════════════════════════
# Tool 1: get_income_summary
# ════════════════════════════════════════════════════════════════════

async def get_income_summary(user_id: str, financial_year: str = "2025-26") -> dict:
    """Fetches the user's complete income breakdown by platform and month.

    Use this tool when the user asks about their earnings, income,
    how much they made, or anything related to their payment history.

    Args:
        user_id: The unique identifier of the user.
        financial_year: The financial year to query. Defaults to 2025-26.

    Returns:
        A dictionary containing:
        - total_gross_income: Total income across all platforms in INR
        - total_tds_deducted: Total TDS deducted across all platforms in INR
        - total_net_income: Gross minus TDS in INR
        - by_platform: Breakdown by platform with subtotals
        - by_month: Monthly income breakdown
        - record_count: Total number of income records
    """
    collection = mongodb.income_records

    # Aggregate by platform (exclude duplicates)
    platform_pipeline = [
        {"$match": {"user_id": user_id, "is_duplicate": False}},
        {
            "$group": {
                "_id": "$platform",
                "total_amount": {"$sum": "$amount"},
                "total_tds": {"$sum": "$tds_deducted"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"total_amount": -1}},
    ]

    # Aggregate by month
    monthly_pipeline = [
        {"$match": {"user_id": user_id, "is_duplicate": False}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$payment_date"},
                    "month": {"$month": "$payment_date"},
                },
                "total_amount": {"$sum": "$amount"},
                "total_tds": {"$sum": "$tds_deducted"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]

    platform_results = await collection.aggregate(platform_pipeline).to_list(None)
    monthly_results = await collection.aggregate(monthly_pipeline).to_list(None)

    # Calculate totals
    total_gross = sum(p["total_amount"] for p in platform_results)
    total_tds = sum(p["total_tds"] for p in platform_results)
    total_count = sum(p["count"] for p in platform_results)

    by_platform = [
        {
            "platform": p["_id"],
            "gross_income": round(p["total_amount"], 2),
            "tds_deducted": round(p["total_tds"], 2),
            "net_income": round(p["total_amount"] - p["total_tds"], 2),
            "record_count": p["count"],
        }
        for p in platform_results
    ]

    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    by_month = [
        {
            "month": month_names[m["_id"]["month"]],
            "year": m["_id"]["year"],
            "gross_income": round(m["total_amount"], 2),
            "tds_deducted": round(m["total_tds"], 2),
            "record_count": m["count"],
        }
        for m in monthly_results
    ]

    return {
        "user_id": user_id,
        "financial_year": financial_year,
        "total_gross_income": round(total_gross, 2),
        "total_tds_deducted": round(total_tds, 2),
        "total_net_income": round(total_gross - total_tds, 2),
        "by_platform": by_platform,
        "by_month": by_month,
        "record_count": total_count,
    }


# ════════════════════════════════════════════════════════════════════
# Tool 2: calculate_tax
# ════════════════════════════════════════════════════════════════════

async def calculate_tax(user_id: str) -> dict:
    """Calculates the user's total tax liability for the current financial year.

    Use this tool when the user asks how much tax they owe, their tax
    liability, whether they need to pay tax, or anything about tax computation.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dictionary containing:
        - gross_income: Total gross income in INR
        - presumptive_income: Income after 44ADA deduction (if applicable)
        - taxable_income: Final taxable amount in INR
        - tax_by_slab: Breakdown showing tax at each slab rate
        - cess: 4% health & education cess in INR
        - total_tax: Tax + cess in INR
        - tds_credit: Total TDS already deducted in INR
        - net_payable: Amount still owed, negative means refund due
        - section_44ADA_applied: Whether presumptive taxation was used
    """
    # Fetch user profile
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        return {"error": f"User {user_id} not found. Please set up your profile first."}

    # Fetch income summary
    income = await get_income_summary(user_id, user.get("financial_year", "2025-26"))
    gross_income = income["total_gross_income"]
    total_tds = income["total_tds_deducted"]

    # Determine taxable income
    opted_44ADA = user.get("opted_44ADA", False)
    presumptive_income = None
    section_44ADA_applied = False

    if opted_44ADA and is_eligible_44ADA(gross_income):
        presumptive_result = apply_44ADA(gross_income, is_digital=True)
        taxable_income = presumptive_result["deemed_profit"]
        presumptive_income = taxable_income
        section_44ADA_applied = True
    else:
        # Without 44ADA, full income is taxable (no deductions calculated here)
        taxable_income = gross_income

    # Calculate tax using slabs
    tax_result = calculate_tax_on_income(taxable_income)

    # Net payable after TDS credit
    net_payable = tax_result["total_tax"] - total_tds

    result = {
        "user_id": user_id,
        "financial_year": user.get("financial_year", "2025-26"),
        "gross_income": round(gross_income, 2),
        "presumptive_income": round(presumptive_income, 2) if presumptive_income else None,
        "taxable_income": round(taxable_income, 2),
        "tax_before_cess": round(tax_result["tax_before_cess"], 2),
        "cess": round(tax_result["cess"], 2),
        "total_tax": round(tax_result["total_tax"], 2),
        "slab_breakdown": tax_result["slab_breakdown"],
        "effective_rate": round(tax_result["effective_rate"], 2),
        "tds_credit": round(total_tds, 2),
        "net_payable": round(net_payable, 2),
        "refund_due": net_payable < 0,
        "section_44ADA_applied": section_44ADA_applied,
        "regime": "new",
    }

    # Save/update tax calculation in DB
    await mongodb.tax_calculations.update_one(
        {"user_id": user_id, "financial_year": user.get("financial_year", "2025-26")},
        {"$set": {**result, "last_updated": datetime.utcnow()}},
        upsert=True,
    )

    return result


# ════════════════════════════════════════════════════════════════════
# Tool 3: find_deductions
# ════════════════════════════════════════════════════════════════════

async def find_deductions(user_id: str) -> dict:
    """Identifies claimable deductions based on the user's occupation and income.

    Use this tool when the user asks about deductions, expenses they can claim,
    ways to reduce tax, or tax-saving options.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dictionary containing:
        - applicable_deductions: List of deduction items with name and estimated amount
        - total_estimated_savings: Total estimated deduction amount in INR
        - occupation_type: The user's occupation type
        - note: Important caveats (especially about 44ADA)
    """
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        return {"error": f"User {user_id} not found."}

    income = await get_income_summary(user_id)
    occupation = user.get("occupation_type", "mixed")
    annual_income = income["total_gross_income"]
    opted_44ADA = user.get("opted_44ADA", False)

    deductions = get_applicable_deductions(occupation, annual_income)

    # Add 44ADA context
    if opted_44ADA:
        deductions["note"] = (
            "⚠️ You have opted for Section 44ADA (Presumptive Taxation). "
            "Under 44ADA, 50% of your gross receipts are automatically treated as expenses. "
            "You CANNOT claim these individual deductions separately — they are already "
            "covered by the 50% deemed expense deduction. The deductions listed below "
            "are shown for informational purposes only and would apply if you switch "
            "to regular taxation."
        )
        deductions["44ADA_opted"] = True
        deductions["deemed_expenses"] = round(annual_income * 0.50, 2)
    else:
        deductions["note"] = (
            "These deductions can be claimed against your professional income. "
            "Keep receipts and records for all claimed expenses."
        )
        deductions["44ADA_opted"] = False

    return deductions


# ════════════════════════════════════════════════════════════════════
# Tool 4: generate_itr_summary
# ════════════════════════════════════════════════════════════════════

async def generate_itr_summary(user_id: str) -> dict:
    """Generates a structured ITR-4 (Sugam) field mapping ready for filing.

    Use this tool when the user asks about filing ITR, wants their ITR summary,
    or asks for a tax return document.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dictionary with ITR-4 Sugam field mappings including:
        - personal_info: Name, PAN, address details
        - income_details: Business/profession income under 44ADA
        - tax_computation: Detailed tax calculation
        - tax_paid: TDS and advance tax details
        - refund_or_payable: Final amount due or refund
    """
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        return {"error": f"User {user_id} not found."}

    # Get fresh tax calculation
    tax = await calculate_tax(user_id)
    income = await get_income_summary(user_id)

    # Build ITR-4 Sugam field mapping
    itr_summary = {
        "form_type": "ITR-4 (Sugam)",
        "assessment_year": "2026-27",
        "financial_year": "2025-26",

        "part_a_general": {
            "name": user.get("name", ""),
            "pan": user.get("pan_number", "XXXXX0000X"),
            "dob": "",
            "state": user.get("state", ""),
            "filing_status": "Original",
            "return_type": "139(1) — On or before due date",
            "tax_regime": "New Tax Regime u/s 115BAC",
        },

        "schedule_bp_profession_income": {
            "nature_of_business": "Freelance / Gig Work",
            "business_code": "16019 — Other professionals",
            "gross_receipts": round(tax.get("gross_income", 0), 2),
            "presumptive_income_44ADA": round(tax.get("presumptive_income", 0) or 0, 2),
            "section_44ADA_applicable": tax.get("section_44ADA_applied", False),
            "platform_wise_receipts": income.get("by_platform", []),
        },

        "part_b_total_income": {
            "income_from_business_profession": round(tax.get("taxable_income", 0), 2),
            "gross_total_income": round(tax.get("taxable_income", 0), 2),
            "total_deductions_via": "None (New Regime)" if tax.get("regime") == "new" else "",
            "total_taxable_income": round(tax.get("taxable_income", 0), 2),
        },

        "part_b_tti_tax_computation": {
            "tax_on_total_income": round(tax.get("tax_before_cess", 0), 2),
            "rebate_87A": round(
                min(tax.get("tax_before_cess", 0), 60000)
                if tax.get("taxable_income", 0) <= 1200000
                else 0,
                2,
            ),
            "tax_after_rebate": round(
                max(
                    tax.get("tax_before_cess", 0)
                    - (
                        min(tax.get("tax_before_cess", 0), 60000)
                        if tax.get("taxable_income", 0) <= 1200000
                        else 0
                    ),
                    0,
                ),
                2,
            ),
            "health_education_cess_4pct": round(tax.get("cess", 0), 2),
            "total_tax_liability": round(tax.get("total_tax", 0), 2),
            "slab_breakdown": tax.get("slab_breakdown", []),
        },

        "schedule_tds": {
            "total_tds_deducted": round(tax.get("tds_credit", 0), 2),
            "tds_by_platform": [
                {
                    "deductor": p["platform"].title(),
                    "amount_paid": p["gross_income"],
                    "tds_deducted": p["tds_deducted"],
                }
                for p in income.get("by_platform", [])
            ],
        },

        "tax_paid_and_verification": {
            "advance_tax_paid": 0,
            "tds_claimed": round(tax.get("tds_credit", 0), 2),
            "total_taxes_paid": round(tax.get("tds_credit", 0), 2),
            "tax_payable": round(max(tax.get("net_payable", 0), 0), 2),
            "refund_due": round(abs(min(tax.get("net_payable", 0), 0)), 2),
        },

        "filing_recommendation": (
            "You are eligible to file ITR-4 (Sugam) under Section 44ADA. "
            "Your presumptive income is 50% of gross receipts."
            if tax.get("section_44ADA_applied")
            else "You should file ITR-4 (Sugam) with actual income details."
        ),
    }

    return itr_summary


# ════════════════════════════════════════════════════════════════════
# Tool 5: check_deadlines
# ════════════════════════════════════════════════════════════════════

async def check_deadlines(user_id: str) -> dict:
    """Checks upcoming advance tax deadlines and amounts due.

    Use this tool when the user asks about deadlines, when to pay tax,
    advance tax dates, or if they have any upcoming tax obligations.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dictionary containing:
        - upcoming_deadlines: List of upcoming deadlines with amounts
        - next_deadline: The immediate next deadline details
        - days_remaining: Days until next deadline
        - alert_level: "urgent" (< 15 days), "warning" (< 30 days), or "ok"
        - total_annual_liability: Full year tax estimate in INR
    """
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        return {"error": f"User {user_id} not found."}

    # Get current tax calculation
    tax = await calculate_tax(user_id)
    total_liability = tax.get("total_tax", 0)
    opted_44ADA = user.get("opted_44ADA", False)

    # Get advance tax schedule
    schedule = get_advance_tax_schedule(
        total_liability=total_liability,
        financial_year=user.get("financial_year", "2025-26"),
        opted_44ADA=opted_44ADA,
    )

    # Find next upcoming deadline
    next_deadline = None
    for d in schedule["deadlines"]:
        if not d["is_past"]:
            next_deadline = d
            break

    # Determine alert level
    alert_level = "ok"
    if next_deadline:
        days = next_deadline["days_remaining"]
        if days <= 15:
            alert_level = "urgent"
        elif days <= 30:
            alert_level = "warning"

    return {
        "user_id": user_id,
        "financial_year": user.get("financial_year", "2025-26"),
        "total_annual_liability": round(total_liability, 2),
        "tds_already_deducted": round(tax.get("tds_credit", 0), 2),
        "net_payable": round(tax.get("net_payable", 0), 2),
        "threshold_met": schedule["threshold_met"],
        "is_presumptive": schedule["is_presumptive"],
        "deadlines": schedule["deadlines"],
        "next_deadline": next_deadline,
        "days_remaining": next_deadline["days_remaining"] if next_deadline else None,
        "alert_level": alert_level,
        "advice": (
            f"⚠️ Your next advance tax payment of ₹{next_deadline['amount_due']:,.2f} "
            f"is due on {next_deadline['due_date']}. You have {next_deadline['days_remaining']} days remaining."
            if next_deadline and alert_level != "ok"
            else "✅ No urgent tax deadlines at the moment."
        ),
    }
