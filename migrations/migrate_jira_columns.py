"""
Migration script to add jira_key and jira_url columns to Epic and Story tables
Run this script to update the database schema
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.config.db import engine

def migrate():
    """Add jira columns to epics and stories tables"""
    
    with engine.connect() as connection:
        # Check if columns exist before adding
        print("Checking if jira_key column exists in epics table...")
        try:
            connection.execute(text("SELECT jira_key FROM epics LIMIT 1"))
            print("✓ jira_key column already exists in epics table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_key column to epics table...")
                connection.execute(text("""
                    ALTER TABLE epics
                    ADD COLUMN jira_key VARCHAR(50)
                """))
                connection.commit()
                print("✓ jira_key column added to epics table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_key to epics: {add_error}")
        
        print("Checking if jira_url column exists in epics table...")
        try:
            connection.execute(text("SELECT jira_url FROM epics LIMIT 1"))
            print("✓ jira_url column already exists in epics table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_url column to epics table...")
                connection.execute(text("""
                    ALTER TABLE epics
                    ADD COLUMN jira_url VARCHAR(512)
                """))
                connection.commit()
                print("✓ jira_url column added to epics table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_url to epics: {add_error}")
        
        print("\nChecking if jira_key column exists in stories table...")
        try:
            connection.execute(text("SELECT jira_key FROM stories LIMIT 1"))
            print("✓ jira_key column already exists in stories table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_key column to stories table...")
                connection.execute(text("""
                    ALTER TABLE stories
                    ADD COLUMN jira_key VARCHAR(50)
                """))
                connection.commit()
                print("✓ jira_key column added to stories table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_key to stories: {add_error}")
        
        print("Checking if jira_url column exists in stories table...")
        try:
            connection.execute(text("SELECT jira_url FROM stories LIMIT 1"))
            print("✓ jira_url column already exists in stories table")
        except Exception:
            try:
                connection.rollback()
                print("Adding jira_url column to stories table...")
                connection.execute(text("""
                    ALTER TABLE stories
                    ADD COLUMN jira_url VARCHAR(512)
                """))
                connection.commit()
                print("✓ jira_url column added to stories table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add jira_url to stories: {add_error}")
        
        print("Checking if epic_jira_key column exists in stories table...")
        try:
            connection.execute(text("SELECT epic_jira_key FROM stories LIMIT 1"))
            print("✓ epic_jira_key column already exists in stories table")
        except Exception:
            try:
                connection.rollback()
                print("Adding epic_jira_key column to stories table...")
                connection.execute(text("""
                    ALTER TABLE stories
                    ADD COLUMN epic_jira_key VARCHAR(50)
                """))
                connection.commit()
                print("✓ epic_jira_key column added to stories table")
            except Exception as add_error:
                connection.rollback()
                print(f"⚠️ Could not add epic_jira_key to stories: {add_error}")
        
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
