"""GigSaathi — Deadline Alert Routes.

Endpoints for checking advance tax deadlines and alerting users.
"""

from fastapi import APIRouter, HTTPException

from app.db.database import mongodb
from app.agent.tools import check_deadlines

router = APIRouter()


@router.get("/deadlines/{user_id}")
async def get_deadlines(user_id: str):
    """Get upcoming advance tax deadlines and amounts due.

    Returns the full advance tax schedule with past/future status,
    days remaining, amount due at each installment, and an alert level
    (urgent/warning/ok).

    Args:
        user_id: The user whose deadlines to check.
    """
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    result = await check_deadlines(user_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
