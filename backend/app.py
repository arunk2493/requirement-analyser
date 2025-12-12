import sys
import os
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend directory to path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db import Base, engine, dispose_db_connections
from routes import upload, generateStories, generateEpics, generateQA, listFiles, generateTestPlan, getEpics, getStories, getQA, getTestPlan, agents_router, rag_search, rag_vectorstore_search, auth, jira

logger.info("Starting Requirement Analyzer Backend")
logger.info(f"Database engine available: {bool(engine)}")


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    else:
        logger.error("Database engine not configured!")
    
    logger.info("Application startup completed")
    yield
    
    # Shutdown
    logger.info("Application shutting down")
    dispose_db_connections()
    logger.info("Database connections closed")


app = FastAPI(
    title="Requirement Analyzer API",
    version="1.0.0",
    description="AI-powered requirement analysis and document processing",
    lifespan=lifespan
)

# CORS Configuration - environment-aware
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Define CORS origins based on environment
if ENVIRONMENT == "production":
    CORS_ORIGINS = [
        os.getenv("FRONTEND_URL", "https://your-frontend-domain.com"),
    ]
else:
    # Development: Allow common development URLs
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ]
    # In development, also allow all localhost variants with different ports
    if DEBUG:
        CORS_ORIGINS.extend([
            "http://localhost:*",
            "http://127.0.0.1:*",
        ])

logger.info(f"CORS Configuration: Environment={ENVIRONMENT}, Origins={CORS_ORIGINS}")

# Security: Add trusted hosts middleware (relaxed in development)
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            os.getenv("ALLOWED_HOSTS", "localhost").split(",")
        ]
    )
else:
    # Development: Allow all localhost variants
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "*.localhost",
        ]
    )

# Add CORS middleware - must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range", "Content-Type"],
    max_age=3600,
)


# Health check endpoint with database connectivity check
@app.get("/health", tags=["System"])
async def health_check():
    """Check if API is running and database is connected"""
    try:
        health_status = {
            "status": "healthy",
            "version": "1.0.0"
        }
        
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                health_status["database"] = "connected"
            except Exception as e:
                logger.warning(f"Database connection check failed: {str(e)}")
                health_status["database"] = "error"
                health_status["error"] = str(e)
                return health_status
        else:
            health_status["database"] = "not_configured"
            health_status["warning"] = "POSTGRES_URL environment variable not set"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/version", tags=["System"])
async def version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "name": "Requirement Analyzer API"
    }


# Register routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(upload.router, prefix="/api", tags=["Files"])
app.include_router(generateStories.router, prefix="/api", tags=["Content Generation"])
app.include_router(generateEpics.router, prefix="/api", tags=["Content Generation"])
app.include_router(generateQA.router, prefix="/api", tags=["Content Generation"])
app.include_router(generateTestPlan.router, prefix="/api", tags=["Content Generation"])
app.include_router(listFiles.router, prefix="/api", tags=["Files"])
app.include_router(getEpics.router, prefix="/api", tags=["Content Retrieval"])
app.include_router(getStories.router, prefix="/api", tags=["Content Retrieval"])
app.include_router(getQA.router, prefix="/api", tags=["Content Retrieval"])
app.include_router(getTestPlan.router, prefix="/api", tags=["Content Retrieval"])
app.include_router(agents_router.router, prefix="/api", tags=["Agents"])
app.include_router(rag_search.router, prefix="/api", tags=["RAG Search"])
app.include_router(rag_vectorstore_search.router, prefix="/api", tags=["RAG Search"])
app.include_router(jira.router, prefix="/api", tags=["Jira Integration"])

logger.info("All routers registered successfully")


if __name__ == "__main__":
    import uvicorn
    
    # Use environment variables for configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
