import os
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import contextmanager
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

logger.info(f"Database URL configured: {bool(POSTGRES_URL)}")

# Create engine with optimized connection pooling
if POSTGRES_URL:
    # Use QueuePool for production, NullPool for testing
    pool_class = QueuePool
    
    engine = create_engine(
        POSTGRES_URL,
        echo=False,  # Set to True for SQL debugging
        poolclass=pool_class,
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Maximum overflow connections
        pool_pre_ping=True,  # Test connections before using them (avoids stale connections)
        pool_recycle=3600,  # Recycle connections after 1 hour to avoid timeout
        connect_args={
            "connect_timeout": 10,
            "application_name": "requirement-analyser"
        }
    )
    logger.info("Database engine created with optimized connection pooling")
    
    # Add listener for connection pool events
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Set connection parameters on connect"""
        try:
            cursor = dbapi_conn.cursor()
            cursor.execute("SET statement_timeout = 30000")  # 30 second timeout per statement
            cursor.close()
        except Exception as e:
            logger.warning(f"Could not set connection timeout: {e}")
else:
    engine = None
    logger.warning("POSTGRES_URL not set - database will not work")

# Configure session with optimization options
if engine:
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False  # Prevent detached instance errors
    )
else:
    SessionLocal = None

Base = declarative_base()


def get_db():
    """
    Get database session with proper transaction management - FastAPI dependency.
    
    Yields:
        Session: Database session
        
    Raises:
        RuntimeError: If database not configured
    """
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


@contextmanager
def get_db_context():
    """
    Context manager for database session - for use with 'with' statements.
    
    Yields:
        Session: Database session
        
    Raises:
        RuntimeError: If database not configured
    """
    if not SessionLocal:
        raise RuntimeError("Database not configured. Set POSTGRES_URL environment variable.")
    
    db = SessionLocal()
    try:
        logger.debug("Database session created via context manager")
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


def dispose_db_connections():
    """
    Dispose all database connections. Call this during graceful shutdown.
    """
    if engine:
        try:
            engine.dispose()
            logger.info("Database connections disposed")
        except Exception as e:
            logger.error(f"Error disposing database connections: {e}")
