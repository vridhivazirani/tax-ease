"""GigSaathi Backend — FastAPI Application Entry Point.

Cloud Run-ready: reads PORT and HOST from environment variables.
Mounts all routers under /api/v1/ prefix.
Manages MongoDB lifecycle via startup/shutdown events.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle — connect/disconnect MongoDB."""
    # Startup
    await mongodb.connect()
    await mongodb.create_indexes()
    print(f"✅ Connected to MongoDB ({settings.DB_NAME})")
    print(f"🤖 Using Gemini model: {settings.GEMINI_MODEL}")

    yield

    # Shutdown
    await mongodb.disconnect()
    print("🔌 Disconnected from MongoDB")


app = FastAPI(
    title="GigSaathi API",
    description="Agentic AI-powered tax & compliance assistant for India's gig workers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origin (Next.js dev server + production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.run.app",  # Cloud Run frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    """Health check endpoint — confirms the API is running."""
    return {
        "status": "healthy",
        "service": "gigsaathi-backend",
        "version": "1.0.0",
        "model": settings.GEMINI_MODEL,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check with dependency status."""
    mongo_ok = mongodb.client is not None
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "mongodb": "connected" if mongo_ok else "disconnected",
        "gemini_model": settings.GEMINI_MODEL,
        "environment": settings.ENV,
    }


# ── Register Routers ───────────────────────────────────────────────
from app.routes import upload, income, tax, chat, deadlines, users

app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(income.router, prefix="/api/v1", tags=["income"])
app.include_router(tax.router, prefix="/api/v1", tags=["tax"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(deadlines.router, prefix="/api/v1", tags=["deadlines"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", settings.PORT))
    host = os.environ.get("HOST", settings.HOST)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.is_development,
    )
