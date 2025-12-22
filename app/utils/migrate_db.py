"""
Database migration script to add payment_method column to vest_events table.
Run this once to update existing database.
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'stonks.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(vest_events)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'payment_method' not in columns:
        print("Adding payment_method column to vest_events table...")
        cursor.execute("""
            ALTER TABLE vest_events 
            ADD COLUMN payment_method VARCHAR(20) DEFAULT 'sell_to_cover'
        """)
        conn.commit()
        print("✓ Successfully added payment_method column")
    else:
        print("✓ payment_method column already exists")
    
    # Update existing records to have default payment method
    cursor.execute("""
        UPDATE vest_events 
        SET payment_method = 'sell_to_cover' 
        WHERE payment_method IS NULL
    """)
    conn.commit()
    print("✓ Updated existing records with default payment method")
    
    print("\n✓ Migration completed successfully!")
    
except Exception as e:
    print(f"✗ Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
