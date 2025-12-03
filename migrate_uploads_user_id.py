"""
Migration script to add user_id to uploads table
This handles the user_id foreign key constraint
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from config.db import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def migrate():
    """Add user_id column to uploads table and set default values"""
    if not engine:
        logger.error("Database engine not configured")
        return False
    
    with engine.connect() as connection:
        try:
            # Check if user_id column already exists
            inspector_query = """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='uploads' AND column_name='user_id'
            """
            
            result = connection.execute(text(inspector_query))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                logger.info("Adding 'user_id' column to uploads table...")
                
                # Step 1: Add the column as nullable
                alter_query = """
                ALTER TABLE uploads 
                ADD COLUMN user_id INTEGER
                """
                connection.execute(text(alter_query))
                connection.commit()
                logger.info("✓ Column added as nullable")
                
                # Step 2: Set default value to 1 for existing records (first user)
                update_query = """
                UPDATE uploads SET user_id = 1 WHERE user_id IS NULL
                """
                connection.execute(text(update_query))
                connection.commit()
                logger.info("✓ Existing records assigned to default user (ID: 1)")
                
                # Step 3: Add foreign key constraint
                fk_query = """
                ALTER TABLE uploads 
                ADD CONSTRAINT fk_uploads_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                """
                connection.execute(text(fk_query))
                connection.commit()
                logger.info("✓ Foreign key constraint added")
                
                # Step 4: Make column NOT NULL
                notnull_query = """
                ALTER TABLE uploads 
                ALTER COLUMN user_id SET NOT NULL
                """
                connection.execute(text(notnull_query))
                connection.commit()
                logger.info("✓ Column set to NOT NULL")
                
                logger.info("✓ Successfully added 'user_id' column to uploads table")
                return True
            else:
                logger.info("✓ 'user_id' column already exists in uploads table")
                return True
                
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            connection.rollback()
            return False

if __name__ == "__main__":
    try:
        success = migrate()
        if success:
            print("\n✓ Migration completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Migration failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Migration error: {str(e)}")
        sys.exit(1)

