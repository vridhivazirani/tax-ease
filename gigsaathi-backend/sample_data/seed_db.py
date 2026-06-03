"""GigSaathi — Database Seeder.

Seeds MongoDB with sample personas and their income records.
Run this script to populate the database for demo/testing:

    cd gigsaathi-backend
    python -m sample_data.seed_db
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.db.database import mongodb
from sample_data.personas import ALL_PROFILES, ALL_INCOME


async def seed_database(clear_existing: bool = True):
    """Seed the database with sample personas and income records.

    Args:
        clear_existing: If True, drops existing data before seeding.
    """
    print("🌱 GigSaathi Database Seeder")
    print(f"   MongoDB: {settings.MONGODB_URI[:30]}...")
    print(f"   Database: {settings.DB_NAME}")
    print()

    # Connect
    await mongodb.connect()
    await mongodb.create_indexes()

    if clear_existing:
        print("🗑️  Clearing existing data...")
        await mongodb.user_profiles.delete_many({})
        await mongodb.income_records.delete_many({})
        await mongodb.tax_calculations.delete_many({})
        print("   Done.\n")

    # Seed user profiles
    print("👤 Seeding user profiles...")
    for profile in ALL_PROFILES:
        doc = {**profile, "created_at": datetime.utcnow()}
        await mongodb.user_profiles.insert_one(doc)
        print(f"   ✅ {profile['name']} ({profile['user_id']}) — {profile['state']}, {profile['occupation_type']}")

    print()

    # Seed income records
    print("💰 Seeding income records...")
    total_records = 0

    for user_id, income_records in ALL_INCOME.items():
        count = 0
        total_amount = 0
        total_tds = 0

        for record in income_records:
            doc = {
                **record,
                "user_id": user_id,
                "is_duplicate": False,
                "duplicate_of": None,
                "transaction_type": "credit",
                "created_at": datetime.utcnow(),
            }
            await mongodb.income_records.insert_one(doc)
            count += 1
            total_amount += record["amount"]
            total_tds += record["tds_deducted"]

        print(f"   ✅ {user_id}: {count} records, ₹{total_amount:,.0f} gross, ₹{total_tds:,.0f} TDS")
        total_records += count

    print(f"\n   Total: {total_records} income records seeded.")
    print()

    # Summary
    print("📊 Database Summary:")
    profiles_count = await mongodb.user_profiles.count_documents({})
    records_count = await mongodb.income_records.count_documents({})
    print(f"   User profiles: {profiles_count}")
    print(f"   Income records: {records_count}")
    print(f"   Tax calculations: 0 (will be computed on first query)")

    print("\n✅ Seeding complete! You can now start the server.")

    # Disconnect
    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_database())
