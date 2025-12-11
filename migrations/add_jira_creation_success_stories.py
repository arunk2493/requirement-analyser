"""
Migration script to add jira_creation_success column to Story table
This boolean column tracks whether the Jira creation was successful or failed.

Field added:
- Story.jira_creation_success: Boolean field
  - True: Jira creation succeeded
  - False: Jira creation failed
  - None: No creation attempt yet

Run this script to update the database schema
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.config.db import engine

def migrate():
    """Add jira_creation_success column to stories table"""
    
    with engine.connect() as connection:
        # Check if column already exists
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'stories' AND column_name = 'jira_creation_success'
            """)
        )
        
        if result.fetchone() is None:
            # Add the column if it doesn't exist
            connection.execute(
                text("ALTER TABLE stories ADD COLUMN jira_creation_success BOOLEAN DEFAULT NULL")
            )
            connection.commit()
            print("✅ Added jira_creation_success column to stories table")
        else:
            print("ℹ️  jira_creation_success column already exists in stories table")

def rollback():
    """Remove jira_creation_success column from stories table"""
    
    with engine.connect() as connection:
        # Check if column exists
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'stories' AND column_name = 'jira_creation_success'
            """)
        )
        
        if result.fetchone() is not None:
            # Remove the column if it exists
            connection.execute(
                text("ALTER TABLE stories DROP COLUMN jira_creation_success")
            )
            connection.commit()
            print("✅ Removed jira_creation_success column from stories table")
        else:
            print("ℹ️  jira_creation_success column does not exist in stories table")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
