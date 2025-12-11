#!/usr/bin/env python3
"""
Direct SQL migration to add vectorstore_id column to uploads table
"""

import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config.db import engine

def migrate_database_direct():
    """Add vectorstore_id column using direct SQL"""
    
    print("Starting database migration...")
    print("=" * 70)
    
    with engine.connect() as connection:
        try:
            # Check if column exists
            print("\n1. Checking if vectorstore_id column exists...")
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'uploads' 
                AND column_name = 'vectorstore_id'
            """))
            
            if result.fetchone():
                print("   ✅ Column already exists!")
            else:
                print("   ⚠️  Column not found, adding it now...")
                
                # Add the column
                print("\n2. Adding vectorstore_id column...")
                connection.execute(text("""
                    ALTER TABLE uploads 
                    ADD COLUMN vectorstore_id VARCHAR(255) DEFAULT NULL
                """))
                connection.commit()
                print("   ✅ Column added successfully!")
            
            # Verify the column was added
            print("\n3. Verifying schema...")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'uploads'
                ORDER BY ordinal_position
            """))
            
            print("\n   Current uploads table schema:")
            for row in result:
                col_name, col_type, nullable = row
                nullable_text = "✓ Nullable" if nullable == 'YES' else "✗ Not Null"
                status = "✨ NEW" if col_name == 'vectorstore_id' else ""
                print(f"      • {col_name:<25} | {col_type:<20} | {nullable_text} {status}")
            
        except Exception as e:
            if "already exists" in str(e):
                print("   ℹ️  Column already exists (no action needed)")
            else:
                raise

if __name__ == "__main__":
    try:
        migrate_database_direct()
        
        print("\n" + "=" * 70)
        print("✅ Database migration completed successfully!")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Restart your backend: python3 backend/app.py")
        print("  2. Upload files - vector stores will be created automatically")
        print("  3. Search using RAG endpoints")
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
