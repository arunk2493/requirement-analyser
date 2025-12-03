"""
Migration script to add 'name' column to users table
Run this script once to update the database schema
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from config.db import engine, Base
from models.file_model import User
from sqlalchemy import text

# Load environment variables
load_dotenv()

def migrate():
    """Add name column to users table if it doesn't exist"""
    with engine.connect() as connection:
        # Check if name column already exists
        inspector_query = """
        SELECT column_name FROM information_schema.columns 
        WHERE table_name='users' AND column_name='name'
        """
        
        result = connection.execute(text(inspector_query))
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            print("Adding 'name' column to users table...")
            alter_query = "ALTER TABLE users ADD COLUMN name VARCHAR(255)"
            connection.execute(text(alter_query))
            connection.commit()
            print("✓ Successfully added 'name' column to users table")
        else:
            print("✓ 'name' column already exists in users table")

if __name__ == "__main__":
    try:
        migrate()
        print("\nMigration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
