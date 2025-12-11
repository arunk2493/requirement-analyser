"""Add test_type column to QA table for test case categorization"""

def migrate(db):
    """Add test_type column to QA table"""
    try:
        # Check if column already exists
        from sqlalchemy import inspect, String, Column
        from models.file_model import QA
        
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('qa')]
        
        if 'test_type' not in columns:
            # Add the column
            db.execute("""
                ALTER TABLE qa 
                ADD COLUMN test_type VARCHAR(50) DEFAULT 'functional';
            """)
            db.commit()
            print("✅ Added test_type column to qa table")
        else:
            print("ℹ️ test_type column already exists in qa table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding test_type column: {str(e)}")
        raise

def rollback(db):
    """Rollback: Remove test_type column from QA table"""
    try:
        db.execute("""
            ALTER TABLE qa 
            DROP COLUMN test_type;
        """)
        db.commit()
        print("✅ Removed test_type column from qa table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing test_type column: {str(e)}")
        raise
