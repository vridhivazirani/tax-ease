# GigSaathi — Devpost Submission

## Inspiration

India has over **15 crore gig economy workers** — Swiggy delivery partners, Uber drivers, Upwork freelancers, Fiverr designers, and millions more earning across multiple platforms. These workers face a unique financial challenge: they earn from 4-5 different platforms, each generating income in different formats, with different TDS deductions, different payout cycles, and **zero unified view** of their total earnings.

The consequences are real:
- **Overpaying tax** because they don't know about Section 44ADA presumptive taxation
- **Missing advance tax deadlines** (June 15, September 15, December 15, March 15) and paying interest penalties
- **Receiving IT notices** they don't understand
- **Paying CAs ₹3,000-5,000+** just to file a basic ITR-4 — money they can't afford

We built GigSaathi because **every gig worker deserves a tax assistant that understands their unique situation** — and agentic AI makes that possible at zero cost.

## What It Does

GigSaathi (गिग साथी — "Gig Companion") is an **agentic AI-powered tax assistant** that:

1. **📄 Ingests Multi-Platform Income**: Workers upload earnings PDFs from Swiggy, Uber, Upwork, Fiverr, or any platform. The system uses Gemini's multimodal capabilities to extract structured income data from unstructured PDFs.

2. **🔗 Normalizes & Deduplicates**: Fivetran MCP orchestrates the data pipeline. Duplicate transactions (same payment appearing in both a platform PDF and bank statement) are automatically detected and flagged.

3. **📊 Unified Dashboard**: All earnings displayed in one view — broken down by platform, month, with TDS tracking across every source.

4. **💰 Accurate Tax Calculation**: Real Indian tax math — FY 2025-26 new regime slabs, Section 44ADA presumptive taxation (50% deemed profit), 4% cess, TDS credits, and net payable computation.

5. **💬 Agentic AI Chat**: Not a chatbot — an **agent**. When a worker asks "How much tax do I owe?", the agent autonomously decides to call `get_income_summary()` → `calculate_tax()`, executes them, reasons over results, and responds with a specific rupee amount.

6. **📋 ITR-4 Ready Output**: Generates a structured ITR-4 (Sugam) field mapping that the worker can file directly or hand to any CA.

7. **⏰ Proactive Deadline Alerts**: Advance tax reminders with exact amounts due and countdown timers.

## How We Built It

### Architecture
```
Frontend (Next.js) → Backend (FastAPI) → Gemini Agent (5 Tools) → MongoDB Atlas
                                              ↕
                                       Fivetran MCP Server
```

### Agentic AI (The Core Innovation)

Unlike traditional chatbots that answer from static knowledge, GigSaathi's Gemini agent has **5 callable tools**:

| Tool | Purpose |
|------|---------|
| `get_income_summary()` | Fetches real earnings from MongoDB |
| `calculate_tax()` | Applies 44ADA + new regime slabs |
| `find_deductions()` | Surfaces occupation-specific deductions |
| `generate_itr_summary()` | Produces ITR-4 field mapping |
| `check_deadlines()` | Alerts on advance tax dates |

The agent decides which tools to call, in what order, based on the user's natural language question. It chains tools when needed — asking about "total tax after deductions" triggers `get_income_summary()` → `find_deductions()` → `calculate_tax()` automatically.

### Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Agent | Google Gemini 2.5 Flash + Function Calling |
| Backend | Python FastAPI |
| Database | MongoDB Atlas |
| Data Pipeline | Fivetran MCP Server |
| Frontend | Next.js (App Router) |
| PDF Parsing | Gemini Multimodal Vision |
| Deployment | Google Cloud Run |

### Tax Rules Implementation

We hardcoded India's complete FY 2025-26 tax rules as a Python module:
- 7-slab new tax regime (0% to 30%)
- Section 87A rebate (₹60,000 for income ≤ ₹12L)
- Section 44ADA presumptive taxation (₹75L threshold, 50% deemed profit)
- 4 advance tax deadlines with cumulative percentages
- Platform-specific TDS rates (194C: 1%, 194J: 10%, 194-O: 0.1%)

## Challenges We Ran Into

1. **Multi-format PDF Parsing**: Every platform's payout statement looks different. We solved this with a carefully crafted Gemini extraction prompt that handles any format.

2. **Duplicate Detection**: When a user uploads both their Swiggy PDF and bank statement, the same ₹22,000 payment appears twice. We built a cross-reference system (±1 day, ±₹1 tolerance) with platform PDFs as source of truth.

3. **Accurate Tax Math**: Indian tax law is complex. Getting 44ADA + new regime slabs + cess + rebate + TDS credits right required careful implementation and verification against manual calculations.

4. **Agent Tool Orchestration**: Teaching the agent when to chain tools (e.g., needing income data before computing tax) vs. calling a single tool required precise system prompting.

## Accomplishments We're Proud Of

- **Real math, not estimates**: Every rupee amount the agent shows is computed from actual data, not hallucinated
- **Zero-cost tax filing prep**: A gig worker who would pay ₹5,000 for a CA can now get the same ITR-4 output for free
- **True agentic behavior**: The agent reasons about which tools to use, not just pattern-matching keywords
- **Production-ready architecture**: Cloud Run deployment, async MongoDB, streaming responses

## What We Learned

- **MCP Protocol**: How Model Context Protocol enables AI agents to interact with external services
- **Indian Tax Code**: The intricacies of presumptive taxation, advance tax, and TDS for gig workers
- **Agentic AI Patterns**: Function calling loops, tool chaining, and grounding responses in real data
- **Gemini Multimodal**: Using vision capabilities for structured data extraction from unstructured documents

## What's Next

- **🏦 Account Aggregator (AA) Integration**: Auto-fetch bank statements via India Stack — no manual upload
- **🌐 Multi-language Support**: Hindi, Telugu, Tamil, Kannada — reaching non-English-speaking gig workers
- **📱 WhatsApp Bot**: Chat with GigSaathi on WhatsApp for maximum accessibility
- **🧾 GST Compliance**: For freelancers crossing the ₹20L GST threshold
- **💳 UPI AutoPay**: Schedule advance tax payments directly from the app

## Built With

`gemini` `google-cloud` `agent-builder` `fivetran` `mcp` `mongodb` `fastapi` `nextjs` `python` `javascript`
