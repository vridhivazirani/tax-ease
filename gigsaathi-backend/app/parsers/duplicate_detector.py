"""GigSaathi — Duplicate Transaction Detector.

Detects duplicate transactions when both platform PDFs and bank statements
are uploaded. Platform PDF entries are treated as the source of truth.
Bank statement entries matching a platform entry (same date ±1 day, same amount ±₹1)
are flagged as duplicates.
"""

from datetime import datetime, timedelta

from app.db.database import mongodb


class DuplicateDetector:
    """Cross-references platform PDF entries against bank statement entries
    to prevent double-counting income."""

    # Tolerance for matching
    DATE_TOLERANCE_DAYS = 1
    AMOUNT_TOLERANCE_INR = 1.0

    async def detect_and_flag_duplicates(self, user_id: str) -> dict:
        """Scan all income records for a user and flag bank statement
        entries that duplicate platform entries.

        Args:
            user_id: The user whose records to scan.

        Returns:
            Dictionary with:
                - duplicates_found: Number of duplicates detected
                - duplicates_flagged: List of flagged record IDs
                - total_duplicate_amount: Sum of duplicate amounts
        """
        collection = mongodb.income_records

        # Get all platform entries (source of truth)
        platform_entries = await collection.find(
            {
                "user_id": user_id,
                "platform": {"$ne": "bank_statement"},
                "is_duplicate": False,
            }
        ).to_list(length=None)

        # Get all bank statement entries (candidates for duplicate flagging)
        bank_entries = await collection.find(
            {
                "user_id": user_id,
                "platform": "bank_statement",
                "is_duplicate": False,
                "transaction_type": "credit",  # Only incoming payments
            }
        ).to_list(length=None)

        duplicates_flagged = []
        total_duplicate_amount = 0.0

        for bank_entry in bank_entries:
            bank_date = bank_entry["payment_date"]
            bank_amount = bank_entry["amount"]

            for platform_entry in platform_entries:
                platform_date = platform_entry["payment_date"]
                platform_amount = platform_entry["amount"]

                # Check date match (±1 day)
                date_diff = abs((bank_date - platform_date).days)
                if date_diff > self.DATE_TOLERANCE_DAYS:
                    continue

                # Check amount match (±₹1)
                amount_diff = abs(bank_amount - platform_amount)
                if amount_diff > self.AMOUNT_TOLERANCE_INR:
                    continue

                # Match found — flag bank entry as duplicate
                await collection.update_one(
                    {"_id": bank_entry["_id"]},
                    {
                        "$set": {
                            "is_duplicate": True,
                            "duplicate_of": str(platform_entry["_id"]),
                        }
                    },
                )

                duplicates_flagged.append(str(bank_entry["_id"]))
                total_duplicate_amount += bank_amount
                break  # One match is enough, move to next bank entry

        return {
            "user_id": user_id,
            "duplicates_found": len(duplicates_flagged),
            "duplicates_flagged": duplicates_flagged,
            "total_duplicate_amount": total_duplicate_amount,
            "platform_entries_count": len(platform_entries),
            "bank_entries_scanned": len(bank_entries),
        }

    async def check_single_entry(
        self, user_id: str, amount: float, payment_date: datetime
    ) -> dict | None:
        """Check if a single entry has a potential duplicate.

        Args:
            user_id: The user ID to search within.
            amount: The transaction amount.
            payment_date: The transaction date.

        Returns:
            The matching platform entry if a duplicate is found, None otherwise.
        """
        collection = mongodb.income_records

        date_min = payment_date - timedelta(days=self.DATE_TOLERANCE_DAYS)
        date_max = payment_date + timedelta(days=self.DATE_TOLERANCE_DAYS)
        amount_min = amount - self.AMOUNT_TOLERANCE_INR
        amount_max = amount + self.AMOUNT_TOLERANCE_INR

        match = await collection.find_one(
            {
                "user_id": user_id,
                "platform": {"$ne": "bank_statement"},
                "payment_date": {"$gte": date_min, "$lte": date_max},
                "amount": {"$gte": amount_min, "$lte": amount_max},
                "is_duplicate": False,
            }
        )

        return match


# Singleton instance
duplicate_detector = DuplicateDetector()
