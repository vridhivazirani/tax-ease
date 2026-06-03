"""Async MongoDB connection layer using Motor.

Provides a singleton ``MongoDB`` instance that manages the connection
lifecycle and exposes typed collection accessors plus index creation.
"""

from __future__ import annotations

import logging

import certifi
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """Async MongoDB connection manager.

    Attributes:
        client: The underlying Motor client (``None`` until ``connect()``).
    """

    DB_NAME = "gigsaathi"

    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Open a connection to MongoDB using the configured URI.

        Raises:
            ConnectionError: If the server is unreachable.
        """
        logger.info("Connecting to MongoDB …")
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tlsCAFile=certifi.where(),
        )
        # Force a round-trip so we fail fast on bad URI / unreachable server
        await self.client.admin.command("ping")
        logger.info("MongoDB connection established.")

    async def disconnect(self) -> None:
        """Close the active MongoDB connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
            logger.info("MongoDB connection closed.")

    # ------------------------------------------------------------------
    # Database & collection helpers
    # ------------------------------------------------------------------

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Return the main application database.

        Raises:
            RuntimeError: If called before ``connect()``.
        """
        if self.client is None:
            raise RuntimeError("MongoDB client is not connected. Call connect() first.")
        return self.client[self.DB_NAME]

    @property
    def income_records(self) -> AsyncIOMotorCollection:
        """Return the ``income_records`` collection."""
        return self.db["income_records"]

    @property
    def user_profiles(self) -> AsyncIOMotorCollection:
        """Return the ``user_profiles`` collection."""
        return self.db["user_profiles"]

    @property
    def tax_calculations(self) -> AsyncIOMotorCollection:
        """Return the ``tax_calculations`` collection."""
        return self.db["tax_calculations"]

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    async def create_indexes(self) -> None:
        """Create required indexes for all collections.

        Indexes created:
            - ``income_records``: compound (user_id, payment_date),
              compound (user_id, platform)
            - ``user_profiles``: unique on user_id
            - ``tax_calculations``: compound (user_id, financial_year)
        """
        logger.info("Creating MongoDB indexes …")

        # income_records
        await self.income_records.create_index(
            [("user_id", pymongo.ASCENDING), ("payment_date", pymongo.ASCENDING)],
            name="idx_income_user_date",
        )
        await self.income_records.create_index(
            [("user_id", pymongo.ASCENDING), ("platform", pymongo.ASCENDING)],
            name="idx_income_user_platform",
        )

        # user_profiles
        await self.user_profiles.create_index(
            [("user_id", pymongo.ASCENDING)],
            unique=True,
            name="idx_user_profile_uid",
        )

        # tax_calculations
        await self.tax_calculations.create_index(
            [("user_id", pymongo.ASCENDING), ("financial_year", pymongo.ASCENDING)],
            name="idx_tax_user_fy",
        )

        logger.info("All indexes created.")


# Singleton instance — import this wherever DB access is needed.
mongodb = MongoDB()
