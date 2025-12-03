"""
Migration: Add user_id column to uploads table and update schema
This script adds the user_id foreign key to the uploads table and ensures
all records have a valid user_id (defaults to user_id=1 for existing records)
"""

from sqlalchemy import text
from config.db import SessionLocal

def migrate_up():
    """Add user_id column and foreign key constraint"""
    db = SessionLocal()
    try:
        # Check if user_id column already exists
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='uploads' AND column_name='user_id'"
        ))
        
        if result.fetchone():
            print("✓ user_id column already exists in uploads table")
            return
        
        # Add user_id column with default value NULL (will update below)
        print("Adding user_id column to uploads table...")
        db.execute(text(
            "ALTER TABLE uploads ADD COLUMN user_id INTEGER"
        ))
        db.commit()
        print("✓ user_id column added")
        
        # Set default user_id to 1 for existing records (assuming user 1 exists)
        print("Updating existing records with user_id=1...")
        db.execute(text(
            "UPDATE uploads SET user_id = 1 WHERE user_id IS NULL"
        ))
        db.commit()
        print("✓ Existing records updated")
        
        # Add NOT NULL constraint
        print("Adding NOT NULL constraint...")
        db.execute(text(
            "ALTER TABLE uploads ALTER COLUMN user_id SET NOT NULL"
        ))
        db.commit()
        print("✓ NOT NULL constraint added")
        
        # Add foreign key constraint
        print("Adding foreign key constraint...")
        db.execute(text(
            "ALTER TABLE uploads ADD CONSTRAINT fk_uploads_user_id "
            "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
        ))
        db.commit()
        print("✓ Foreign key constraint added")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def migrate_down():
    """Rollback: Remove user_id column"""
    db = SessionLocal()
    try:
        print("Rolling back migration...")
        
        # Drop foreign key constraint
        db.execute(text(
            "ALTER TABLE uploads DROP CONSTRAINT IF EXISTS fk_uploads_user_id"
        ))
        
        # Drop user_id column
        db.execute(text(
            "ALTER TABLE uploads DROP COLUMN IF EXISTS user_id"
        ))
        
        db.commit()
        print("✅ Rollback completed successfully!")
        
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        migrate_down()
    else:
        migrate_up()
