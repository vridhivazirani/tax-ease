"""Pydantic v2 models for user profiles."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    """Full user profile stored in MongoDB.

    Attributes:
        user_id: Unique identifier for the user.
        name: User's display name.
        state: Indian state of residence (for state-specific rules).
        occupation_type: Primary gig category — delivery, rideshare,
            freelancer, or mixed.
        age: User's age (used for senior-citizen slab selection).
        financial_year: Active financial year (default ``2025-26``).
        opted_44ADA: Whether the user has opted for the Section 44ADA
            presumptive taxation scheme.
        pan_number: PAN card number (optional, masked in responses).
        created_at: Timestamp when the profile was created.
    """

    model_config = ConfigDict(populate_by_name=True)

    user_id: str
    name: str
    state: str
    occupation_type: str  # delivery | rideshare | freelancer | mixed
    age: int
    financial_year: str = "2025-26"
    opted_44ADA: bool = True
    pan_number: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfileCreate(BaseModel):
    """Payload accepted when creating a new user profile.

    Contains only the fields that the caller must supply; server-side
    defaults (``created_at``, ``financial_year``) are applied automatically.

    Attributes:
        name: User's display name.
        state: Indian state of residence.
        occupation_type: Primary gig category.
        age: User's age.
        opted_44ADA: Whether to apply Section 44ADA presumptive taxation.
        pan_number: PAN card number (optional).
    """

    name: str
    state: str
    occupation_type: str
    age: int
    opted_44ADA: bool = True
    pan_number: str | None = None


class UserProfileResponse(UserProfile):
    """User profile enriched with the MongoDB document ``_id``.

    Attributes:
        id: MongoDB ``_id`` serialised as a string.
    """

    id: str
