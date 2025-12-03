import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

logger.info(f"Database URL configured: {bool(POSTGRES_URL)}")

# create engine (will be None if POSTGRES_URL is not set)
if POSTGRES_URL:
    engine = create_engine(
        POSTGRES_URL,
        echo=False,  # Set to True for SQL debugging
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using them
    )
    logger.info("Database engine created successfully")
else:
    engine = None
    logger.warning("POSTGRES_URL not set - database will not work")

# expire_on_commit=False prevents detached instance errors
if engine:
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )
else:
    SessionLocal = None

Base = declarative_base()

@contextmanager
def get_db():
    """Get database session with proper transaction management"""
    if not SessionLocal:
        raise RuntimeError("Database not configured. Set POSTGRES_URL environment variable.")
    
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
        # Only commit if no exception occurred
        db.commit()
        logger.debug("Database transaction committed")
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction rolled back due to error: {str(e)}")
        raise
    finally:
        db.close()
        logger.debug("Database session closed")
