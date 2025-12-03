#!/usr/bin/env python3
"""
Migration Runner
Run migrations to update database schema

Usage:
    python run_migration.py up      # Run all pending migrations
    python run_migration.py down    # Rollback last migration
    python run_migration.py status  # Check migration status
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def run_migration(direction="up"):
    """Run migration in specified direction"""
    try:
        from migrations.add_user_id_to_tables import migrate_up, migrate_down
        
        if direction == "up":
            print("=" * 50)
            print("Running Migration: Add user_id to tables")
            print("=" * 50)
            migrate_up()
        elif direction == "down":
            print("=" * 50)
            print("Rolling back Migration: Add user_id to tables")
            print("=" * 50)
            migrate_down()
        else:
            print(f"Unknown direction: {direction}")
            print("Use 'up' or 'down'")
            return False
        
        return True
    
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure migrations module exists")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_status():
    """Check migration status"""
    print("=" * 50)
    print("Migration Status")
    print("=" * 50)
    print("\nPending Migrations:")
    print("1. 001_add_user_id_to_tables - Add user_id column to uploads table")
    print("\nTo run: python run_migration.py up")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py [up|down|status]")
        sys.exit(1)
    
    direction = sys.argv[1].lower()
    
    if direction == "status":
        check_status()
    elif direction in ["up", "down"]:
        success = run_migration(direction)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {direction}")
        print("Use 'up', 'down', or 'status'")
        sys.exit(1)
