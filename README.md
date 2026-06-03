# GigSaathi

> **Agentic AI-powered tax & compliance assistant for India's gig economy workers**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)

---

##  The Problem

India has **15 crore+ gig workers** — Swiggy delivery partners, Uber drivers, Upwork freelancers, Fiverr designers — many earning from 4-5 platforms simultaneously. Each platform generates income in different formats, with different TDS deductions, different payout cycles, and **zero unified view** of total earnings.

The result? Workers **overpay tax**, miss advance tax deadlines, receive IT notices they don't understand, or pay CAs they can't afford — just to file a basic ITR.

##  The Solution

GigSaathi lets workers upload their earnings PDFs from any platform, and the system does everything else automatically:

- ** Upload PDFs** — Swiggy payout statements, Uber trip summaries, Upwork invoices, bank statements
- ** AI Extraction** — Gemini parses PDFs and extracts structured income data
- ** Deduplication** — Detects duplicate transactions across platform PDFs and bank statements
- ** Unified Dashboard** — See all earnings in one place, broken down by platform and month
- ** Tax Calculation** — Accurate FY 2025-26 tax computation with Section 44ADA presumptive taxation
- ** ITR-4 Ready** — Generates a field-by-field ITR-4 (Sugam) summary for filing
- ** AI Chat** — Ask anything about your tax situation in natural language
- ** Deadline Alerts** — Proactive advance tax deadline reminders

##  Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend (Next.js)              │
│   Dashboard │ Chat │ ITR Summary │ PDF Upload    │
└──────────────────────┬──────────────────────────┘
                       │ REST API
┌──────────────────────┴──────────────────────────┐
│              Backend (Python FastAPI)             │
│                                                   │
│  ┌──────────┐  ┌───────────────┐  ┌───────────┐ │
│  │PDF Parser│  │ Gemini Agent  │  │  API      │ │
│  │(Gemini)  │  │ + 5 Tools     │  │  Routes   │ │
│  └────┬─────┘  └───────┬───────┘  └─────┬─────┘ │
│       │                │                │        │
│  ┌────┴────────────────┴────────────────┴─────┐ │
│  │           MongoDB Atlas                     │ │
│  │  income_records │ user_profiles │ tax_calc  │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
         │
    ┌────┴────┐
    │ Fivetran│  (Pipeline orchestration)
    │  MCP    │
    └─────────┘
```

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Agent** | Google Gemini 2.0 Flash / 2.5 Flash |
| **Agent Framework** | Gemini Function Calling (google-genai SDK) |
| **Backend** | Python FastAPI |
| **Database** | MongoDB Atlas |
| **Data Pipeline** | Fivetran MCP Server |
| **Frontend** | Next.js (App Router) |
| **PDF Parsing** | Gemini Multimodal (Vision) |
| **Deployment** | Google Cloud Run |

##  Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (free tier works)
- Google Cloud project with Gemini API key

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/gigsaathi.git
cd gigsaathi/gigsaathi-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your actual credentials

# Seed the database with sample data
python -m sample_data.seed_db

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`.
API docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd gigsaathi/frontend

# Install dependencies
bun install

# Run dev server
bun run dev 
```

The frontend will be at `http://localhost:3000`.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `GEMINI_MODEL` | Model name (gemini-2.0-flash or gemini-2.5-flash) | ✅ |
| `MONGODB_URI` | MongoDB Atlas connection string | ✅ |
| `FIVETRAN_API_KEY` | Fivetran API key | Optional |
| `FIVETRAN_API_SECRET` | Fivetran API secret | Optional |
| `PORT` | Server port (default: 8000) | Optional |
| `HOST` | Server host (default: 0.0.0.0) | Optional |
| `ENV` | Environment (development/production) | Optional |

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload/{user_id}` | Upload PDFs for income extraction |
| `GET` | `/api/v1/income/{user_id}` | Get income summary |
| `GET` | `/api/v1/tax/{user_id}` | Calculate tax liability |
| `GET` | `/api/v1/tax/{user_id}/itr` | Generate ITR-4 summary |
| `GET` | `/api/v1/tax/{user_id}/deductions` | Get applicable deductions |
| `POST` | `/api/v1/chat` | Chat with the AI agent |
| `POST` | `/api/v1/chat/stream` | Chat with SSE streaming |
| `GET` | `/api/v1/deadlines/{user_id}` | Check advance tax deadlines |
| `POST` | `/api/v1/users` | Create a user profile |
| `GET` | `/api/v1/users/{user_id}` | Get user profile |

##  Agent Tools

The Gemini agent has 5 callable tools:

1. **`get_income_summary()`** — Fetches real earnings from MongoDB
2. **`calculate_tax()`** — Runs actual tax math (44ADA, new regime slabs)
3. **`find_deductions()`** — Surfaces claimable expenses
4. **`generate_itr_summary()`** — Produces ITR-4 field mapping
5. **`check_deadlines()`** — Alerts on advance tax dates

##  Future Scope

- **Account Aggregator (AA) Integration** — Auto-fetch bank statements via India Stack
- **Multi-language Support** — Hindi, Telugu, Tamil, Kannada
- **WhatsApp Bot** — Chat with GigSaathi via WhatsApp
- **GST Compliance** — For freelancers crossing ₹20L threshold
- **UPI AutoPay** — Schedule advance tax payments

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

## 👥 Team

Built for hackathon by the GigSaathi team.
