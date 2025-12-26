"""
Database migration to add security fields to User model.
Run this script to update existing databases.
"""

from app import create_app, db
from sqlalchemy import text

def migrate_user_security_fields():
    """Add security fields to existing User table."""
    app = create_app()
    
    with app.app_context():
        # Check if we're using SQLite or PostgreSQL
        engine = db.engine
        
        migrations = [
            # Security tracking fields
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until DATETIME",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login DATETIME",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_password_change DATETIME",
            
            # Password reset fields
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expiry DATETIME",
            
            # Email verification
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255)",
            
            # Two-factor authentication
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(32)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS backup_codes TEXT",
            
            # Session security
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS session_token VARCHAR(255)",
        ]
        
        # For SQLite, we need different syntax
        if 'sqlite' in str(engine.url):
            print("Detected SQLite database - using SQLite-compatible migrations")
            # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
            # We'll need to check each column first
            
            connection = engine.connect()
            
            # Get existing columns
            result = connection.execute(text("PRAGMA table_info(users)"))
            existing_columns = {row[1] for row in result}
            
            sqlite_migrations = {
                'failed_login_attempts': "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0",
                'is_locked': "ALTER TABLE users ADD COLUMN is_locked BOOLEAN DEFAULT FALSE",
                'locked_until': "ALTER TABLE users ADD COLUMN locked_until DATETIME",
                'last_login': "ALTER TABLE users ADD COLUMN last_login DATETIME",
                'last_password_change': "ALTER TABLE users ADD COLUMN last_password_change DATETIME",
                'password_reset_token': "ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255)",
                'password_reset_expiry': "ALTER TABLE users ADD COLUMN password_reset_expiry DATETIME",
                'email_verified': "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE",
                'email_verification_token': "ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255)",
                'totp_secret': "ALTER TABLE users ADD COLUMN totp_secret VARCHAR(32)",
                'totp_enabled': "ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE",
                'backup_codes': "ALTER TABLE users ADD COLUMN backup_codes TEXT",
                'session_token': "ALTER TABLE users ADD COLUMN session_token VARCHAR(255)",
            }
            
            for column_name, migration_sql in sqlite_migrations.items():
                if column_name not in existing_columns:
                    try:
                        connection.execute(text(migration_sql))
                        connection.commit()
                        print(f"✓ Added column: {column_name}")
                    except Exception as e:
                        print(f"✗ Error adding {column_name}: {e}")
                else:
                    print(f"- Column already exists: {column_name}")
            
            connection.close()
        else:
            # PostgreSQL or other databases
            print("Using PostgreSQL-compatible migrations")
            connection = engine.connect()
            
            for migration_sql in migrations:
                try:
                    connection.execute(text(migration_sql))
                    connection.commit()
                    print(f"✓ Executed: {migration_sql[:50]}...")
                except Exception as e:
                    print(f"✗ Error: {e}")
            
            connection.close()
        
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update existing users' last_password_change to current time")
        print("2. Consider forcing password resets for existing users")
        print("3. Review and test all security features")


if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION: Adding Security Fields to Users")
    print("=" * 60)
    print("\nThis will add the following security fields:")
    print("  - Failed login tracking")
    print("  - Account locking")
    print("  - Password reset tokens")
    print("  - Email verification")
    print("  - Two-factor authentication")
    print("  - Session tokens")
    print("\n" + "=" * 60)
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_user_security_fields()
    else:
        print("Migration cancelled.")
