"""Deductions and TDS rates relevant to Indian gig workers.

Provides occupation-specific deduction catalogues and TDS rate
look-ups for common platform payment structures.

Note:
    Under Section 44ADA (presumptive taxation), 50 % of gross receipts
    are *already* deemed as expenses.  Therefore individual expense
    deductions listed here **cannot** be claimed separately when 44ADA
    is opted.
"""

from typing import Any

# ---------------------------------------------------------------------------
# Deduction Catalogues by Occupation Type
# ---------------------------------------------------------------------------
# Each entry: (name, category, description, estimated_annual_amount)

_DELIVERY_DEDUCTIONS: list[tuple[str, str, str, float]] = [
    (
        "Fuel / Charging",
        "vehicle",
        "Petrol, diesel, or EV charging costs for delivery runs",
        48_000,
    ),
    (
        "Vehicle Maintenance",
        "vehicle",
        "Servicing, tyre replacement, oil changes, minor repairs",
        12_000,
    ),
    (
        "Mobile Phone Bill",
        "communication",
        "Postpaid/prepaid recharge used for delivery app & navigation",
        6_000,
    ),
    (
        "Rain Gear & Safety Equipment",
        "equipment",
        "Raincoat, helmet visor, gloves, reflective vest",
        3_000,
    ),
    (
        "Delivery Bag / Hot-Box",
        "equipment",
        "Insulated bag or box for food/parcel delivery",
        2_500,
    ),
    (
        "Mobile Phone (Depreciation)",
        "depreciation",
        "Depreciation on smartphone used primarily for work",
        5_000,
    ),
]

_RIDESHARE_DEDUCTIONS: list[tuple[str, str, str, float]] = [
    (
        "Fuel / Charging",
        "vehicle",
        "Petrol, diesel, CNG, or EV charging for ride trips",
        96_000,
    ),
    (
        "Vehicle EMI Interest",
        "finance",
        "Interest component of vehicle loan EMI (not principal)",
        36_000,
    ),
    (
        "Vehicle Insurance",
        "insurance",
        "Commercial / comprehensive motor insurance premium",
        15_000,
    ),
    (
        "Vehicle Maintenance & Repairs",
        "vehicle",
        "Servicing, tyre, brake pad, body work, cleaning",
        18_000,
    ),
    (
        "Mobile Phone Bill",
        "communication",
        "Recharge / plan used for ride-hailing app & GPS",
        6_000,
    ),
    (
        "GPS / Dash-cam Device",
        "equipment",
        "Dedicated GPS tracker or dashboard camera for safety",
        3_000,
    ),
    (
        "Toll & Parking Charges",
        "vehicle",
        "Toll fees and parking charges incurred during rides",
        12_000,
    ),
]

_FREELANCER_DEDUCTIONS: list[tuple[str, str, str, float]] = [
    (
        "Internet / Broadband",
        "communication",
        "Home broadband or mobile data plan for work",
        12_000,
    ),
    (
        "Laptop / Computer (Depreciation)",
        "depreciation",
        "40 % WDV depreciation on laptop/desktop used for work",
        16_000,
    ),
    (
        "Software Subscriptions",
        "software",
        "SaaS tools — design, dev, project management, cloud hosting",
        18_000,
    ),
    (
        "Co-working Space",
        "workspace",
        "Monthly co-working desk or meeting room rental",
        30_000,
    ),
    (
        "Mobile Phone Bill",
        "communication",
        "Postpaid plan or recharge used for client calls & work",
        6_000,
    ),
    (
        "Professional Courses & Certifications",
        "education",
        "Online courses, certifications, and books for skill-building",
        10_000,
    ),
    (
        "Office Supplies & Peripherals",
        "equipment",
        "Monitor, keyboard, mouse, headset, stationery",
        8_000,
    ),
]

# Mapping of occupation type to its deduction list
_OCCUPATION_DEDUCTIONS: dict[str, list[tuple[str, str, str, float]]] = {
    "delivery": _DELIVERY_DEDUCTIONS,
    "rideshare": _RIDESHARE_DEDUCTIONS,
    "freelancer": _FREELANCER_DEDUCTIONS,
}

# 44ADA advisory note
_44ADA_NOTE: str = (
    "Under Section 44ADA, 50% of gross receipts are already deemed as "
    "expenses. These individual deductions CANNOT be claimed separately "
    "if you opt for presumptive taxation. They are listed here for "
    "reference to help you decide whether normal provisions (ITR-3) "
    "with actual expense claims might be more beneficial."
)


def get_applicable_deductions(
    occupation_type: str,
    annual_income: float,
) -> dict[str, Any]:
    """Return a catalogue of common deductions for a gig worker.

    Deductions are categorised by occupation type with reasonable
    annual estimates.  Actual amounts will vary based on geography,
    usage patterns, and documentation.

    Args:
        occupation_type: One of ``"delivery"``, ``"rideshare"``,
            ``"freelancer"``, or ``"mixed"``.
        annual_income: Gross annual income in INR.  Used to provide
            context on whether 44ADA might be more beneficial.
            Must be ≥ 0.

    Returns:
        A dict with:
            - ``occupation_type`` (str): Echo of input.
            - ``annual_income`` (float): Echo of input.
            - ``deductions`` (list[dict]): Each dict has ``name``,
              ``category``, ``description``,
              ``estimated_annual_amount``.
            - ``total_estimated_deductions`` (float): Sum of all
              estimated amounts.
            - ``deemed_expenses_44ADA`` (float): 50 % of income —
              what 44ADA would allow.
            - ``recommendation`` (str): Quick guidance on 44ADA vs
              actual expenses.
            - ``is_44ADA_note`` (str): Important caveat about 44ADA.

    Raises:
        ValueError: If *occupation_type* is not recognised or
            *annual_income* is negative.

    Examples:
        >>> result = get_applicable_deductions("delivery", 6_00_000)
        >>> len(result["deductions"]) > 0
        True
    """
    if annual_income < 0:
        raise ValueError("annual_income must be non-negative")

    occupation_type = occupation_type.strip().lower()
    valid_types = {"delivery", "rideshare", "freelancer", "mixed"}
    if occupation_type not in valid_types:
        raise ValueError(
            f"occupation_type must be one of {sorted(valid_types)}, "
            f"got '{occupation_type}'"
        )

    annual_income = float(annual_income)

    # Build deduction list
    if occupation_type == "mixed":
        # Combine unique deductions from all categories, de-duped by name
        seen_names: set[str] = set()
        raw: list[tuple[str, str, str, float]] = []
        for deductions_list in _OCCUPATION_DEDUCTIONS.values():
            for item in deductions_list:
                if item[0] not in seen_names:
                    seen_names.add(item[0])
                    raw.append(item)
    else:
        raw = _OCCUPATION_DEDUCTIONS[occupation_type]

    deductions: list[dict[str, Any]] = [
        {
            "name": name,
            "category": category,
            "description": description,
            "estimated_annual_amount": amount,
        }
        for name, category, description, amount in raw
    ]

    total_estimated = sum(d["estimated_annual_amount"] for d in deductions)
    deemed_44ADA = round(annual_income * 0.50, 2)

    # Recommendation
    if deemed_44ADA >= total_estimated:
        recommendation = (
            f"Section 44ADA deemed expenses (₹{deemed_44ADA:,.0f}) are "
            f"higher than your estimated actual expenses "
            f"(₹{total_estimated:,.0f}). Opting for 44ADA is likely "
            f"more beneficial — simpler compliance and higher deduction."
        )
    else:
        recommendation = (
            f"Your estimated actual expenses (₹{total_estimated:,.0f}) "
            f"exceed the 44ADA deemed amount (₹{deemed_44ADA:,.0f}). "
            f"Filing under normal provisions (ITR-3) with books of "
            f"account may save more tax — but consult a CA to confirm."
        )

    return {
        "occupation_type": occupation_type,
        "annual_income": annual_income,
        "deductions": deductions,
        "total_estimated_deductions": total_estimated,
        "deemed_expenses_44ADA": deemed_44ADA,
        "recommendation": recommendation,
        "is_44ADA_note": _44ADA_NOTE,
    }


# ---------------------------------------------------------------------------
# TDS Rates by Platform / Section
# ---------------------------------------------------------------------------
_TDS_RATES: dict[str, dict[str, Any]] = {
    "194C": {
        "section": "194C",
        "description": "TDS on payments to contractors",
        "rate_individual": 0.01,
        "rate_display": "1%",
        "applicable_platforms": [
            "Swiggy", "Zomato", "Uber", "Ola", "Dunzo",
            "Porter", "Shadowfax",
        ],
        "note": (
            "Applicable when platforms classify gig workers as "
            "contractors. TDS is deducted on each payment."
        ),
    },
    "194J": {
        "section": "194J",
        "description": "TDS on professional / technical service fees",
        "rate_individual": 0.10,
        "rate_display": "10%",
        "applicable_platforms": [
            "Upwork", "Fiverr", "Toptal", "Freelancer.com",
            "99designs",
        ],
        "note": (
            "Applicable for professional services. Indian payers "
            "deduct 10 % TDS under this section."
        ),
    },
    "194-O": {
        "section": "194-O",
        "description": "TDS on e-commerce participant payments",
        "rate_individual": 0.001,
        "rate_display": "0.1%",
        "applicable_platforms": [
            "Amazon Seller", "Flipkart Seller", "Meesho",
            "Etsy (Indian entity)",
        ],
        "note": (
            "E-commerce operators deduct 0.1 % on gross amount of "
            "sale or service facilitated through the platform."
        ),
    },
}


def get_tds_rates() -> dict[str, Any]:
    """Return TDS rates applicable to common gig-worker platforms.

    Covers three key TDS sections relevant to gig economy:
        - **194C** — Contractors (delivery / rideshare platforms)
        - **194J** — Professional fees (freelancing platforms)
        - **194-O** — E-commerce participants (marketplace sellers)

    Returns:
        A dict keyed by section number (``"194C"``, ``"194J"``,
        ``"194-O"``), each containing:
            - ``section`` (str)
            - ``description`` (str)
            - ``rate_individual`` (float): Decimal rate.
            - ``rate_display`` (str): Human-readable rate.
            - ``applicable_platforms`` (list[str])
            - ``note`` (str): Additional context.

    Examples:
        >>> rates = get_tds_rates()
        >>> rates["194C"]["rate_display"]
        '1%'
        >>> "Swiggy" in rates["194C"]["applicable_platforms"]
        True
    """
    # Return a deep-ish copy so callers can't mutate the module-level data
    return {
        section: {
            "section": info["section"],
            "description": info["description"],
            "rate_individual": info["rate_individual"],
            "rate_display": info["rate_display"],
            "applicable_platforms": list(info["applicable_platforms"]),
            "note": info["note"],
        }
        for section, info in _TDS_RATES.items()
    }
