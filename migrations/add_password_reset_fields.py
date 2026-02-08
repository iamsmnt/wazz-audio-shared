"""
Migration: Add password_reset_token fields to users table.

Run this script once against the database to add the new columns.
Usage: python migrations/add_password_reset_fields.py

Idempotent: safe to run multiple times.

Note: For development environments using Base.metadata.create_all(),
these columns are created automatically when the model is updated.
This script is for existing deployed databases.
"""

from sqlalchemy import text
from wazz_shared.database import engine


def migrate():
    with engine.connect() as conn:
        # Check which columns already exist
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' AND column_name IN (
                'password_reset_token', 'password_reset_token_expires'
            )
        """))
        existing = {row[0] for row in result}

        if 'password_reset_token' not in existing:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN password_reset_token VARCHAR"
            ))
            conn.execute(text(
                "CREATE INDEX ix_users_password_reset_token ON users (password_reset_token)"
            ))
            print("Added: password_reset_token")
        else:
            print("Skipped: password_reset_token (already exists)")

        if 'password_reset_token_expires' not in existing:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN password_reset_token_expires TIMESTAMP WITH TIME ZONE"
            ))
            print("Added: password_reset_token_expires")
        else:
            print("Skipped: password_reset_token_expires (already exists)")

        conn.commit()
        print("Migration complete.")


if __name__ == "__main__":
    migrate()
