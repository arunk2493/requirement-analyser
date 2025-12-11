#!/usr/bin/env python3
"""
Migration script to add Jira credential columns to users table
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.config.db import engine, SessionLocal

def migrate():
    """Add Jira columns to users table"""
    db = SessionLocal()
    
    try:
        with engine.connect() as conn:
            # List of columns to add with their definitions
            columns_to_add = [
                ("jira_url", "VARCHAR(512)"),
                ("jira_username", "VARCHAR(255)"),
                ("jira_api_token", "VARCHAR(512)"),
                ("jira_project_key", "VARCHAR(50)"),
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    # Check if column already exists
                    result = conn.execute(
                        text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='users' 
                        AND column_name='{col_name}'
                        """)
                    )
                    
                    if not result.fetchone():
                        # Column doesn't exist, add it
                        conn.execute(
                            text(f"""
                            ALTER TABLE users 
                            ADD COLUMN {col_name} {col_type}
                            """)
                        )
                        conn.commit()
                        print(f"✅ Added column '{col_name}' to users table")
                    else:
                        print(f"⏭️  Column '{col_name}' already exists, skipping")
                        
                except Exception as e:
                    print(f"❌ Error adding column '{col_name}': {str(e)}")
                    conn.rollback()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Running migration: Add Jira credentials to users table...")
    migrate()
