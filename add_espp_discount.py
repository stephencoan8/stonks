#!/usr/bin/env python3
"""
Add ESPP discount field to grants table.
This tracks the purchase discount (typically 15% for qualified ESPP).
"""

import sqlite3
import sys

def add_espp_discount_field():
    """Add espp_discount column to grants table."""
    
    print("=" * 70)
    print("🔄 DATABASE MIGRATION: Add ESPP Discount Field")
    print("=" * 70)
    print()
    
    db_path = 'instance/stonks.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(grants)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'espp_discount' in columns:
            print("✅ Column 'espp_discount' already exists in grants table")
            print("   No migration needed.")
            conn.close()
            return True
        
        print("📊 Adding 'espp_discount' column to grants table...")
        
        # Add the new column with default value 0.0
        cursor.execute('''
            ALTER TABLE grants 
            ADD COLUMN espp_discount FLOAT DEFAULT 0.0
        ''')
        
        conn.commit()
        print("   ✅ Column added successfully")
        print()
        
        # Update existing ESPP grants to have 15% discount
        print("📈 Updating existing ESPP grants with 15% discount...")
        cursor.execute('''
            UPDATE grants 
            SET espp_discount = 0.15 
            WHERE grant_type = 'espp'
        ''')
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"   ✅ Updated {updated_count} ESPP grants with 0.15 (15%) discount")
        print()
        
        # Verify the changes
        print("✅ Verification:")
        cursor.execute('''
            SELECT grant_type, COUNT(*) as count, AVG(espp_discount) as avg_discount
            FROM grants
            GROUP BY grant_type
        ''')
        
        results = cursor.fetchall()
        for grant_type, count, avg_discount in results:
            discount_str = f"{avg_discount*100:.0f}%" if avg_discount else "0%"
            print(f"   - {grant_type}: {count} grants, avg discount: {discount_str}")
        
        print()
        print("=" * 70)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        print()
        print("✅ ESPP discount tracking enabled:")
        print("   - New column 'espp_discount' added to grants table")
        print("   - Existing ESPP grants updated with 15% discount")
        print("   - Cost basis calculations now accurate")
        print("   - Capital gains will be calculated correctly")
        print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == '__main__':
    print()
    response = input("Add ESPP discount field to grants table? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        success = add_espp_discount_field()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Migration cancelled.")
        sys.exit(0)
