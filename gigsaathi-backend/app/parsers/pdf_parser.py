"""GigSaathi — PDF Parsing Service.

Uses Gemini 2.0 Flash to extract structured income data from uploaded PDFs.
Supports Swiggy, Uber, Upwork, Fiverr payout statements and bank statements.
Processes multiple PDFs in parallel using asyncio.gather().
"""

import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

from app.config import settings


# ── Extraction Prompt ───────────────────────────────────────────────

EXTRACTION_PROMPT = """You are a financial document parser specializing in Indian gig economy payment documents.

Analyze this PDF and extract ALL payment/income entries.

Return a JSON object with EXACTLY this structure:
{
    "platform": "swiggy" | "uber" | "upwork" | "fiverr" | "bank_statement" | "other",
    "document_type": "payout_statement" | "invoice" | "bank_statement" | "earnings_report",
    "period": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    },
    "entries": [
        {
            "date": "YYYY-MM-DD",
            "amount": 12345.67,
            "tds_deducted": 123.45,
            "description": "Brief description of payment",
            "transaction_type": "credit" | "debit"
        }
    ],
    "summary": {
        "total_gross": 12345.67,
        "total_tds": 123.45,
        "total_net": 12222.22,
        "entry_count": 5
    }
}

RULES:
1. All amounts must be in Indian Rupees (INR) as numbers, NOT strings.
2. Dates must be in ISO format (YYYY-MM-DD).
3. If TDS is not explicitly mentioned, set tds_deducted to 0.
4. For bank statements: identify the source/counterparty in the description.
5. Only include CREDIT entries (incoming payments) unless this is a bank statement.
6. For bank statements: include both credits and debits but mark transaction_type.
7. If you cannot determine the platform, use "other".
8. Return ONLY valid JSON — no markdown fencing, no explanatory text.
"""


class PDFParser:
    """Gemini-powered PDF parser for gig economy payment documents."""

    def __init__(self):
        """Initialize the parser. Gemini client is lazy-loaded on first use."""
        self._client = None
        self.model = settings.GEMINI_MODEL

    @property
    def client(self):
        """Lazy-initialize the Gemini client on first access."""
        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    async def parse_pdf(self, file_content: bytes, filename: str) -> dict:
        """Parse a single PDF file and extract structured income data.

        Args:
            file_content: Raw PDF file bytes.
            filename: Original filename (used for context).

        Returns:
            Dictionary with extracted payment data in the standard schema.

        Raises:
            ValueError: If Gemini returns invalid JSON or fails to parse.
        """
        # Encode PDF as base64 for Gemini
        pdf_base64 = base64.b64encode(file_content).decode("utf-8")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type="application/pdf",
                                    data=pdf_base64,
                                )
                            ),
                            types.Part(
                                text=f"Filename: {filename}\n\n{EXTRACTION_PROMPT}"
                            ),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_output_tokens=4096,
                ),
            )

            # Parse the JSON response
            raw_text = response.text.strip()

            # Strip markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]  # Remove first line
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

            parsed = json.loads(raw_text)

            # Validate required fields
            if "entries" not in parsed:
                raise ValueError("Response missing 'entries' field")
            if "platform" not in parsed:
                parsed["platform"] = "other"

            # Add metadata
            parsed["source_pdf_name"] = filename
            parsed["parsed_at"] = datetime.utcnow().isoformat()

            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Gemini response as JSON for {filename}: {e}"
            )
        except Exception as e:
            raise ValueError(f"PDF parsing failed for {filename}: {e}")

    async def parse_multiple_pdfs(
        self, files: list[tuple[bytes, str]]
    ) -> list[dict]:
        """Parse multiple PDFs in parallel.

        Args:
            files: List of (file_content, filename) tuples.

        Returns:
            List of parsed results, one per PDF. Failed parses include
            an 'error' key instead of 'entries'.
        """
        tasks = []
        for content, name in files:
            tasks.append(self._safe_parse(content, name))

        results = await asyncio.gather(*tasks)
        return results

    async def _safe_parse(self, content: bytes, name: str) -> dict:
        """Parse a single PDF with error handling.

        Args:
            content: Raw PDF bytes.
            name: Filename.

        Returns:
            Parsed result dict, or error dict if parsing failed.
        """
        try:
            return await self.parse_pdf(content, name)
        except Exception as e:
            return {
                "source_pdf_name": name,
                "error": str(e),
                "entries": [],
                "platform": "unknown",
            }


# Singleton instance
pdf_parser = PDFParser()
