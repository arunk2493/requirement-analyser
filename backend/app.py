import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db import Base, engine
from routes import upload, generateStories, generateEpics, generateQA, listFiles, generateTestPlan, getEpics, getStories, getQA, getTestPlan, agents_router, rag_search, auth

logger.info("Starting Requirement Analyzer Backend")
logger.info(f"Database engine available: {bool(engine)}")

# Create tables if engine is available
if engine:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
else:
    logger.error("Database engine not configured!")

app = FastAPI(title="Requirement Analyzer API", version="1.0.0")

# Add CORS middleware - must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "localhost:5173",
        "localhost:5174",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if API is running and database is connected"""
    try:
        if engine:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {
                "status": "healthy",
                "database": "connected",
                "version": "1.0.0"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "not_configured",
                "error": "POSTGRES_URL environment variable not set"
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(generateStories.router)
app.include_router(generateEpics.router)
app.include_router(generateQA.router)
app.include_router(listFiles.router)
app.include_router(generateTestPlan.router)
app.include_router(getEpics.router)
app.include_router(getStories.router)
app.include_router(getQA.router)
app.include_router(getTestPlan.router)
app.include_router(agents_router.router)
app.include_router(rag_search.router)

logger.info("All routers registered successfully")
