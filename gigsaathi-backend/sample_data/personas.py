"""GigSaathi — Sample User Personas.

Three realistic gig worker personas for demo purposes:
1. Ravi Kumar — Uber driver + Fiverr graphic designer
2. Priya Sharma — Swiggy delivery + Upwork content writer
3. Arjun Reddy — Multi-platform freelancer (Upwork + Fiverr + Toptal)

Each persona has 6-8 months of realistic earnings data.
"""

from datetime import datetime, timedelta
import random

random.seed(42)  # Reproducible sample data


def _date(month: int, day: int, year: int = 2025) -> datetime:
    """Helper to create a datetime for FY 2025-26 (Apr 2025 - Mar 2026)."""
    return datetime(year, month, day)


# ════════════════════════════════════════════════════════════════════
# PERSONA 1: Ravi Kumar — Uber Driver + Fiverr Designer
# ════════════════════════════════════════════════════════════════════

RAVI_PROFILE = {
    "user_id": "ravi_kumar",
    "name": "Ravi Kumar",
    "state": "Karnataka",
    "occupation_type": "mixed",
    "age": 28,
    "financial_year": "2025-26",
    "opted_44ADA": True,
    "pan_number": "ABCPK1234A",
}

RAVI_INCOME = [
    # Uber earnings (monthly payouts, TDS 1% under 194C)
    {"platform": "uber", "amount": 32000, "tds_deducted": 320, "payment_date": _date(4, 30), "source_pdf_name": "ravi_uber_apr.pdf", "description": "Uber April 2025 payout - 142 trips"},
    {"platform": "uber", "amount": 35500, "tds_deducted": 355, "payment_date": _date(5, 31), "source_pdf_name": "ravi_uber_may.pdf", "description": "Uber May 2025 payout - 158 trips"},
    {"platform": "uber", "amount": 28000, "tds_deducted": 280, "payment_date": _date(6, 30), "source_pdf_name": "ravi_uber_jun.pdf", "description": "Uber June 2025 payout - 125 trips"},
    {"platform": "uber", "amount": 38000, "tds_deducted": 380, "payment_date": _date(7, 31), "source_pdf_name": "ravi_uber_jul.pdf", "description": "Uber July 2025 payout - 170 trips"},
    {"platform": "uber", "amount": 34000, "tds_deducted": 340, "payment_date": _date(8, 31), "source_pdf_name": "ravi_uber_aug.pdf", "description": "Uber August 2025 payout - 152 trips"},
    {"platform": "uber", "amount": 36500, "tds_deducted": 365, "payment_date": _date(9, 30), "source_pdf_name": "ravi_uber_sep.pdf", "description": "Uber September 2025 payout - 163 trips"},
    {"platform": "uber", "amount": 40000, "tds_deducted": 400, "payment_date": _date(10, 31), "source_pdf_name": "ravi_uber_oct.pdf", "description": "Uber October 2025 payout - 180 trips"},
    {"platform": "uber", "amount": 37000, "tds_deducted": 370, "payment_date": _date(11, 30), "source_pdf_name": "ravi_uber_nov.pdf", "description": "Uber November 2025 payout - 165 trips"},

    # Fiverr earnings (monthly, TDS 10% under 194J)
    {"platform": "fiverr", "amount": 22000, "tds_deducted": 2200, "payment_date": _date(4, 25), "source_pdf_name": "ravi_fiverr_apr.pdf", "description": "Fiverr April - 8 logo design orders"},
    {"platform": "fiverr", "amount": 28000, "tds_deducted": 2800, "payment_date": _date(5, 25), "source_pdf_name": "ravi_fiverr_may.pdf", "description": "Fiverr May - 11 design orders"},
    {"platform": "fiverr", "amount": 18000, "tds_deducted": 1800, "payment_date": _date(6, 25), "source_pdf_name": "ravi_fiverr_jun.pdf", "description": "Fiverr June - 6 design orders"},
    {"platform": "fiverr", "amount": 25000, "tds_deducted": 2500, "payment_date": _date(7, 25), "source_pdf_name": "ravi_fiverr_jul.pdf", "description": "Fiverr July - 9 design orders"},
    {"platform": "fiverr", "amount": 30000, "tds_deducted": 3000, "payment_date": _date(8, 25), "source_pdf_name": "ravi_fiverr_aug.pdf", "description": "Fiverr August - 12 design + branding orders"},
    {"platform": "fiverr", "amount": 24000, "tds_deducted": 2400, "payment_date": _date(9, 25), "source_pdf_name": "ravi_fiverr_sep.pdf", "description": "Fiverr September - 9 design orders"},
    {"platform": "fiverr", "amount": 27000, "tds_deducted": 2700, "payment_date": _date(10, 25), "source_pdf_name": "ravi_fiverr_oct.pdf", "description": "Fiverr October - 10 design orders"},
    {"platform": "fiverr", "amount": 20000, "tds_deducted": 2000, "payment_date": _date(11, 25), "source_pdf_name": "ravi_fiverr_nov.pdf", "description": "Fiverr November - 7 design orders"},
]
# Ravi total: Uber ~₹2,81,000 + Fiverr ~₹1,94,000 = ~₹4,75,000 (8 months)
# Annualized ~₹7,12,500

# ════════════════════════════════════════════════════════════════════
# PERSONA 2: Priya Sharma — Swiggy Delivery + Upwork Writer
# ════════════════════════════════════════════════════════════════════

PRIYA_PROFILE = {
    "user_id": "priya_sharma",
    "name": "Priya Sharma",
    "state": "Maharashtra",
    "occupation_type": "mixed",
    "age": 24,
    "financial_year": "2025-26",
    "opted_44ADA": True,
    "pan_number": "DEFPS5678B",
}

PRIYA_INCOME = [
    # Swiggy earnings (weekly payouts aggregated monthly, TDS 1% under 194C)
    {"platform": "swiggy", "amount": 18500, "tds_deducted": 185, "payment_date": _date(4, 28), "source_pdf_name": "priya_swiggy_apr.pdf", "description": "Swiggy April - 210 deliveries"},
    {"platform": "swiggy", "amount": 21000, "tds_deducted": 210, "payment_date": _date(5, 28), "source_pdf_name": "priya_swiggy_may.pdf", "description": "Swiggy May - 240 deliveries"},
    {"platform": "swiggy", "amount": 24500, "tds_deducted": 245, "payment_date": _date(6, 28), "source_pdf_name": "priya_swiggy_jun.pdf", "description": "Swiggy June - 280 deliveries (monsoon bonus)"},
    {"platform": "swiggy", "amount": 22000, "tds_deducted": 220, "payment_date": _date(7, 28), "source_pdf_name": "priya_swiggy_jul.pdf", "description": "Swiggy July - 250 deliveries"},
    {"platform": "swiggy", "amount": 19000, "tds_deducted": 190, "payment_date": _date(8, 28), "source_pdf_name": "priya_swiggy_aug.pdf", "description": "Swiggy August - 215 deliveries"},
    {"platform": "swiggy", "amount": 23000, "tds_deducted": 230, "payment_date": _date(9, 28), "source_pdf_name": "priya_swiggy_sep.pdf", "description": "Swiggy September - 260 deliveries"},
    {"platform": "swiggy", "amount": 26000, "tds_deducted": 260, "payment_date": _date(10, 28), "source_pdf_name": "priya_swiggy_oct.pdf", "description": "Swiggy October - 295 deliveries (festive rush)"},
    {"platform": "swiggy", "amount": 20000, "tds_deducted": 200, "payment_date": _date(11, 28), "source_pdf_name": "priya_swiggy_nov.pdf", "description": "Swiggy November - 230 deliveries"},

    # Upwork earnings (monthly invoices, TDS 10% under 194J)
    {"platform": "upwork", "amount": 38000, "tds_deducted": 3800, "payment_date": _date(4, 15), "source_pdf_name": "priya_upwork_apr.pdf", "description": "Upwork April - 3 content writing projects"},
    {"platform": "upwork", "amount": 42000, "tds_deducted": 4200, "payment_date": _date(5, 15), "source_pdf_name": "priya_upwork_may.pdf", "description": "Upwork May - 4 blog + copywriting projects"},
    {"platform": "upwork", "amount": 35000, "tds_deducted": 3500, "payment_date": _date(6, 15), "source_pdf_name": "priya_upwork_jun.pdf", "description": "Upwork June - 3 content projects"},
    {"platform": "upwork", "amount": 45000, "tds_deducted": 4500, "payment_date": _date(7, 15), "source_pdf_name": "priya_upwork_jul.pdf", "description": "Upwork July - 4 projects + long-term contract"},
    {"platform": "upwork", "amount": 40000, "tds_deducted": 4000, "payment_date": _date(8, 15), "source_pdf_name": "priya_upwork_aug.pdf", "description": "Upwork August - 3 content + SEO projects"},
    {"platform": "upwork", "amount": 48000, "tds_deducted": 4800, "payment_date": _date(9, 15), "source_pdf_name": "priya_upwork_sep.pdf", "description": "Upwork September - 5 projects (best month!)"},
    {"platform": "upwork", "amount": 43000, "tds_deducted": 4300, "payment_date": _date(10, 15), "source_pdf_name": "priya_upwork_oct.pdf", "description": "Upwork October - 4 content writing projects"},
    {"platform": "upwork", "amount": 36000, "tds_deducted": 3600, "payment_date": _date(11, 15), "source_pdf_name": "priya_upwork_nov.pdf", "description": "Upwork November - 3 projects"},
]
# Priya total: Swiggy ~₹1,74,000 + Upwork ~₹3,27,000 = ~₹5,01,000 (8 months)
# Annualized ~₹7,51,500

# ════════════════════════════════════════════════════════════════════
# PERSONA 3: Arjun Reddy — Multi-platform Freelancer
# ════════════════════════════════════════════════════════════════════

ARJUN_PROFILE = {
    "user_id": "arjun_reddy",
    "name": "Arjun Reddy",
    "state": "Telangana",
    "occupation_type": "freelancer",
    "age": 32,
    "financial_year": "2025-26",
    "opted_44ADA": True,
    "pan_number": "GHIPR9012C",
}

ARJUN_INCOME = [
    # Upwork earnings (high-value software projects, TDS 10%)
    {"platform": "upwork", "amount": 65000, "tds_deducted": 6500, "payment_date": _date(4, 10), "source_pdf_name": "arjun_upwork_apr.pdf", "description": "Upwork April - React dashboard project"},
    {"platform": "upwork", "amount": 58000, "tds_deducted": 5800, "payment_date": _date(5, 10), "source_pdf_name": "arjun_upwork_may.pdf", "description": "Upwork May - API integration project"},
    {"platform": "upwork", "amount": 72000, "tds_deducted": 7200, "payment_date": _date(6, 10), "source_pdf_name": "arjun_upwork_jun.pdf", "description": "Upwork June - Full-stack web app"},
    {"platform": "upwork", "amount": 55000, "tds_deducted": 5500, "payment_date": _date(7, 10), "source_pdf_name": "arjun_upwork_jul.pdf", "description": "Upwork July - Mobile app backend"},
    {"platform": "upwork", "amount": 68000, "tds_deducted": 6800, "payment_date": _date(8, 10), "source_pdf_name": "arjun_upwork_aug.pdf", "description": "Upwork August - E-commerce platform"},
    {"platform": "upwork", "amount": 61000, "tds_deducted": 6100, "payment_date": _date(9, 10), "source_pdf_name": "arjun_upwork_sep.pdf", "description": "Upwork September - Cloud migration project"},
    {"platform": "upwork", "amount": 70000, "tds_deducted": 7000, "payment_date": _date(10, 10), "source_pdf_name": "arjun_upwork_oct.pdf", "description": "Upwork October - AI chatbot project"},
    {"platform": "upwork", "amount": 63000, "tds_deducted": 6300, "payment_date": _date(11, 10), "source_pdf_name": "arjun_upwork_nov.pdf", "description": "Upwork November - SaaS dashboard"},

    # Fiverr earnings (smaller projects, TDS 10%)
    {"platform": "fiverr", "amount": 28000, "tds_deducted": 2800, "payment_date": _date(4, 20), "source_pdf_name": "arjun_fiverr_apr.pdf", "description": "Fiverr April - 5 web development gigs"},
    {"platform": "fiverr", "amount": 32000, "tds_deducted": 3200, "payment_date": _date(5, 20), "source_pdf_name": "arjun_fiverr_may.pdf", "description": "Fiverr May - 6 dev gigs"},
    {"platform": "fiverr", "amount": 25000, "tds_deducted": 2500, "payment_date": _date(6, 20), "source_pdf_name": "arjun_fiverr_jun.pdf", "description": "Fiverr June - 4 dev gigs"},
    {"platform": "fiverr", "amount": 35000, "tds_deducted": 3500, "payment_date": _date(7, 20), "source_pdf_name": "arjun_fiverr_jul.pdf", "description": "Fiverr July - 7 dev gigs (busy month)"},
    {"platform": "fiverr", "amount": 30000, "tds_deducted": 3000, "payment_date": _date(8, 20), "source_pdf_name": "arjun_fiverr_aug.pdf", "description": "Fiverr August - 5 dev gigs"},
    {"platform": "fiverr", "amount": 27000, "tds_deducted": 2700, "payment_date": _date(9, 20), "source_pdf_name": "arjun_fiverr_sep.pdf", "description": "Fiverr September - 4 dev gigs"},
    {"platform": "fiverr", "amount": 33000, "tds_deducted": 3300, "payment_date": _date(10, 20), "source_pdf_name": "arjun_fiverr_oct.pdf", "description": "Fiverr October - 6 dev gigs"},
    {"platform": "fiverr", "amount": 29000, "tds_deducted": 2900, "payment_date": _date(11, 20), "source_pdf_name": "arjun_fiverr_nov.pdf", "description": "Fiverr November - 5 dev gigs"},

    # Toptal earnings (premium freelancing, TDS 10%)
    {"platform": "toptal", "amount": 48000, "tds_deducted": 4800, "payment_date": _date(4, 5), "source_pdf_name": "arjun_toptal_apr.pdf", "description": "Toptal April - 80hrs @ $7.5/hr React project"},
    {"platform": "toptal", "amount": 42000, "tds_deducted": 4200, "payment_date": _date(5, 5), "source_pdf_name": "arjun_toptal_may.pdf", "description": "Toptal May - 70hrs consulting"},
    {"platform": "toptal", "amount": 54000, "tds_deducted": 5400, "payment_date": _date(6, 5), "source_pdf_name": "arjun_toptal_jun.pdf", "description": "Toptal June - 90hrs full-stack project"},
    {"platform": "toptal", "amount": 45000, "tds_deducted": 4500, "payment_date": _date(7, 5), "source_pdf_name": "arjun_toptal_jul.pdf", "description": "Toptal July - 75hrs backend project"},
    {"platform": "toptal", "amount": 50000, "tds_deducted": 5000, "payment_date": _date(8, 5), "source_pdf_name": "arjun_toptal_aug.pdf", "description": "Toptal August - 83hrs DevOps project"},
    {"platform": "toptal", "amount": 46000, "tds_deducted": 4600, "payment_date": _date(9, 5), "source_pdf_name": "arjun_toptal_sep.pdf", "description": "Toptal September - 77hrs API project"},
    {"platform": "toptal", "amount": 52000, "tds_deducted": 5200, "payment_date": _date(10, 5), "source_pdf_name": "arjun_toptal_oct.pdf", "description": "Toptal October - 87hrs platform build"},
    {"platform": "toptal", "amount": 44000, "tds_deducted": 4400, "payment_date": _date(11, 5), "source_pdf_name": "arjun_toptal_nov.pdf", "description": "Toptal November - 73hrs consulting"},
]
# Arjun total: Upwork ~₹5,12,000 + Fiverr ~₹2,39,000 + Toptal ~₹3,81,000 = ~₹11,32,000 (8 months)
# Annualized ~₹16,98,000


# ── All personas in one list ───────────────────────────────────────

ALL_PROFILES = [RAVI_PROFILE, PRIYA_PROFILE, ARJUN_PROFILE]
ALL_INCOME = {
    "ravi_kumar": RAVI_INCOME,
    "priya_sharma": PRIYA_INCOME,
    "arjun_reddy": ARJUN_INCOME,
}
