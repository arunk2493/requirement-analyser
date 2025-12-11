"""
Migration script to add jira_creation_success column to Epic table
This boolean column tracks whether the Jira creation was successful or failed.

Field added:
- Epic.jira_creation_success: Boolean field
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
    """Add jira_creation_success column to epics table"""
    
    with engine.connect() as connection:
        # Add jira_creation_success to epics table
        print("Checking if jira_creation_success column exists in epics table...")
        try:
            connection.execute(text("SELECT jira_creation_success FROM epics LIMIT 1"))
            print("✓ jira_creation_success column already exists in epics table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_creation_success column to epics table...")
                connection.execute(text("""
                    ALTER TABLE epics
                    ADD COLUMN jira_creation_success BOOLEAN
                """))
                connection.commit()
                print("✓ jira_creation_success column added to epics table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_creation_success to epics: {add_error}")

if __name__ == "__main__":
    print("=" * 60)
    print("Running migration: add_jira_creation_success")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)
