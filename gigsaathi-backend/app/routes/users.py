"""GigSaathi — User Profile Routes.

Endpoints for managing user profiles (create, read, update).
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.database import mongodb

router = APIRouter()


class UserProfileCreate(BaseModel):
    """Request body for creating a user profile."""
    user_id: str
    name: str
    state: str
    occupation_type: str  # delivery, rideshare, freelancer, mixed
    age: int
    opted_44ADA: bool = True
    pan_number: str | None = None


@router.post("/users")
async def create_user(profile: UserProfileCreate):
    """Create a new user profile.

    Args:
        profile: User profile data including name, state, occupation type.
    """
    # Check if user already exists
    existing = await mongodb.user_profiles.find_one({"user_id": profile.user_id})
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"User '{profile.user_id}' already exists",
        )

    doc = {
        **profile.model_dump(),
        "financial_year": "2025-26",
        "created_at": datetime.utcnow(),
    }

    await mongodb.user_profiles.insert_one(doc)

    return {"message": f"User '{profile.user_id}' created successfully", "user": doc}


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get a user's profile.

    Args:
        user_id: The user's unique identifier.
    """
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    user["_id"] = str(user["_id"])
    return user


@router.get("/users")
async def list_users():
    """List all user profiles (for demo/admin purposes)."""
    users = await mongodb.user_profiles.find().to_list(length=100)
    for u in users:
        u["_id"] = str(u["_id"])
    return {"users": users, "count": len(users)}
