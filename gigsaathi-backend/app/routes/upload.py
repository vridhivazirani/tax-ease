"""GigSaathi — PDF Upload Routes.

Endpoints for uploading PDF files (earnings statements, invoices, bank statements).
Processes PDFs in parallel using Gemini, stores extracted data in MongoDB,
and runs duplicate detection.
"""

from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from app.config import settings
from app.db.database import mongodb
from app.parsers.pdf_parser import pdf_parser
from app.parsers.duplicate_detector import duplicate_detector

router = APIRouter()


@router.post("/upload/{user_id}")
async def upload_pdfs(
    user_id: str,
    files: list[UploadFile] = File(..., description="PDF files to process"),
):
    """Upload one or more PDF files for income extraction.

    Accepts Swiggy payout statements, Uber trip summaries, Upwork invoices,
    Fiverr earnings reports, bank statements, or any payment PDF.

    The endpoint:
    1. Reads all uploaded PDFs
    2. Sends them to Gemini for parallel extraction
    3. Validates and stores extracted records in MongoDB
    4. Runs duplicate detection against existing records
    5. Returns extraction results and duplicate report

    Args:
        user_id: The user whose income this belongs to.
        files: One or more PDF files.

    Returns:
        Processing results for each file including extracted entries,
        duplicate detection results, and any errors.
    """
    # Validate user exists
    user = await mongodb.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    # Validate file count
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_FILES_PER_UPLOAD} files per upload",
        )

    # Read all files
    file_data = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' is not a PDF",
            )
        content = await f.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
            )
        file_data.append((content, f.filename))

    # Parse all PDFs in parallel via Gemini
    parse_results = await pdf_parser.parse_multiple_pdfs(file_data)

    # Store extracted records in MongoDB
    total_records_stored = 0
    file_results = []

    for result in parse_results:
        filename = result.get("source_pdf_name", "unknown")

        if "error" in result:
            file_results.append({
                "filename": filename,
                "status": "error",
                "error": result["error"],
                "records_stored": 0,
            })
            continue

        entries = result.get("entries", [])
        records_stored = 0

        for entry in entries:
            # Only store credit entries (income) — skip debits from bank statements
            if result.get("platform") == "bank_statement":
                if entry.get("transaction_type") == "debit":
                    continue

            record = {
                "user_id": user_id,
                "platform": result.get("platform", "other"),
                "amount": float(entry.get("amount", 0)),
                "tds_deducted": float(entry.get("tds_deducted", 0)),
                "payment_date": datetime.fromisoformat(entry["date"]),
                "source_pdf_name": filename,
                "description": entry.get("description", ""),
                "transaction_type": entry.get("transaction_type", "credit"),
                "is_duplicate": False,
                "duplicate_of": None,
                "created_at": datetime.utcnow(),
            }

            await mongodb.income_records.insert_one(record)
            records_stored += 1

        total_records_stored += records_stored

        file_results.append({
            "filename": filename,
            "status": "success",
            "platform_detected": result.get("platform", "unknown"),
            "document_type": result.get("document_type", "unknown"),
            "period": result.get("period", {}),
            "entries_found": len(entries),
            "records_stored": records_stored,
            "summary": result.get("summary", {}),
        })

    # Run duplicate detection
    dedup_result = await duplicate_detector.detect_and_flag_duplicates(user_id)

    return {
        "user_id": user_id,
        "files_processed": len(files),
        "total_records_stored": total_records_stored,
        "file_results": file_results,
        "duplicate_detection": dedup_result,
    }


@router.get("/upload/history/{user_id}")
async def get_upload_history(user_id: str):
    """List all PDFs uploaded by a user with processing metadata.

    Args:
        user_id: The user whose upload history to fetch.

    Returns:
        List of uploaded files with record counts per file.
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": "$source_pdf_name",
                "platform": {"$first": "$platform"},
                "record_count": {"$sum": 1},
                "total_amount": {"$sum": "$amount"},
                "total_tds": {"$sum": "$tds_deducted"},
                "duplicates": {"$sum": {"$cond": ["$is_duplicate", 1, 0]}},
                "uploaded_at": {"$min": "$created_at"},
            }
        },
        {"$sort": {"uploaded_at": -1}},
    ]

    results = await mongodb.income_records.aggregate(pipeline).to_list(None)

    return {
        "user_id": user_id,
        "uploads": [
            {
                "filename": r["_id"],
                "platform": r["platform"],
                "record_count": r["record_count"],
                "total_amount": round(r["total_amount"], 2),
                "total_tds": round(r["total_tds"], 2),
                "duplicates_flagged": r["duplicates"],
                "uploaded_at": r["uploaded_at"].isoformat() if r["uploaded_at"] else None,
            }
            for r in results
        ],
        "total_files": len(results),
    }
