"""
FastAPI main application entry point.
Initializes the API server with all routes, middleware, and configurations.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api import trades, chat, calculations
from app.core.config import settings

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Brazilian Financial Assistant backend...")
    from app.storage.database import create_tables
    create_tables()
    logger.info("Database tables ready.")

    from app.vector_db.chroma_client import get_chroma_client
    chroma = get_chroma_client()
    if chroma:
        chroma.load_initial_regulations()
    else:
        logger.warning("ChromaDB unavailable — RAG context will not be used.")

    yield
    # Shutdown
    logger.info("Shutting down Brazilian Financial Assistant backend...")


# Create FastAPI app
app = FastAPI(
    title="Brazilian Financial Assistant",
    description="Intelligent chatbot for Brazilian financial market tax calculations",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(calculations.router, prefix="/api/calculations", tags=["calculations"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring and deployment."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/hello", tags=["test"])
async def hello():
    """Test endpoint to verify infrastructure connectivity."""
    return {
        "message": "Olá! Backend is running!",
        "timestamp": "2026-04-27",
        "status": "success"
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Brazilian Financial Assistant",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
