"""
Migration script to add jira_issue_id columns to Epic and Story tables
This enables storing numeric Jira issue IDs for creating stories as child work items.

Fields added:
- Epic.jira_issue_id: Numeric Jira issue ID (e.g., 10028)
- Story.jira_issue_id: Numeric Jira issue ID (e.g., 10030)
- Story.epic_jira_issue_id: Parent epic's numeric Jira issue ID

Run this script to update the database schema
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.config.db import engine

def migrate():
    """Add jira_issue_id columns to epics and stories tables"""
    
    with engine.connect() as connection:
        # Add jira_issue_id to epics table
        print("Checking if jira_issue_id column exists in epics table...")
        try:
            connection.execute(text("SELECT jira_issue_id FROM epics LIMIT 1"))
            print("✓ jira_issue_id column already exists in epics table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_issue_id column to epics table...")
                connection.execute(text("""
                    ALTER TABLE epics
                    ADD COLUMN jira_issue_id VARCHAR(50)
                """))
                connection.commit()
                print("✓ jira_issue_id column added to epics table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_issue_id to epics: {add_error}")
        
        # Add jira_issue_id to stories table
        print("Checking if jira_issue_id column exists in stories table...")
        try:
            connection.execute(text("SELECT jira_issue_id FROM stories LIMIT 1"))
            print("✓ jira_issue_id column already exists in stories table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_issue_id column to stories table...")
                connection.execute(text("""
                    ALTER TABLE stories
                    ADD COLUMN jira_issue_id VARCHAR(50)
                """))
                connection.commit()
                print("✓ jira_issue_id column added to stories table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_issue_id to stories: {add_error}")
        
        # Add epic_jira_issue_id to stories table
        print("Checking if epic_jira_issue_id column exists in stories table...")
        try:
            connection.execute(text("SELECT epic_jira_issue_id FROM stories LIMIT 1"))
            print("✓ epic_jira_issue_id column already exists in stories table")
        except Exception:
            try:
                connection.rollback()
                print("Adding epic_jira_issue_id column to stories table...")
                connection.execute(text("""
                    ALTER TABLE stories
                    ADD COLUMN epic_jira_issue_id VARCHAR(50)
                """))
                connection.commit()
                print("✓ epic_jira_issue_id column added to stories table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add epic_jira_issue_id to stories: {add_error}")

if __name__ == "__main__":
    print("=" * 60)
    print("Running migration: add_jira_issue_ids")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)
