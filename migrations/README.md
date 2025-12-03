# Database Migrations

This directory contains database migration scripts to update the schema.

## Available Migrations

### 001. Add user_id to uploads table
**File:** `add_user_id_to_tables.py`
**Description:** Adds user_id foreign key column to the uploads table for user-scoped data access

**Changes:**
- Adds `user_id` INTEGER column to `uploads` table
- Sets existing records to user_id=1 (default admin user)
- Adds NOT NULL constraint
- Adds foreign key constraint referencing `users(id)` with CASCADE DELETE

## Running Migrations

### Run all pending migrations (up):
```bash
python run_migration.py up
```

### Rollback last migration (down):
```bash
python run_migration.py down
```

### Check migration status:
```bash
python run_migration.py status
```

## Migration Details

Each migration script contains:
- `migrate_up()` - Apply the migration
- `migrate_down()` - Rollback the migration

The migrations use SQLAlchemy's `text()` for raw SQL queries to ensure compatibility with PostgreSQL.

## Prerequisites

Before running migrations:
1. Ensure PostgreSQL is running
2. Verify `.env` has correct `POSTGRES_URL`
3. Ensure backend is not running (to avoid connection conflicts)

## Troubleshooting

If a migration fails:
1. Check PostgreSQL logs
2. Verify the database connection
3. Check if the column/constraint already exists
4. Run `python run_migration.py status` to see pending migrations

## Creating New Migrations

To create a new migration:
1. Create a new file: `migrations/descriptive_name.py`
2. Implement `migrate_up()` and `migrate_down()` functions
3. Add to the migration runner in `run_migration.py`
