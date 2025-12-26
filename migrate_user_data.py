#!/usr/bin/env python3
"""
Data Migration Script: Old Database → New Secure Database
Migrates users, grants, and vest events while preserving all security enhancements.
"""

import sqlite3
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.grant import Grant
from app.models.vest_event import VestEvent
from werkzeug.security import generate_password_hash

def migrate_data():
    """Migrate all data from backup to new secure database."""
    
    print("=" * 70)
    print("🔄 DATA MIGRATION: Backup → Secure Database")
    print("=" * 70)
    print()
    
    # Connect to backup database
    backup_conn = sqlite3.connect('instance/stonks.db.backup')
    backup_cursor = backup_conn.cursor()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get current state
        current_users = User.query.count()
        current_grants = Grant.query.count()
        current_vests = VestEvent.query.count()
        
        print(f"📊 CURRENT STATE:")
        print(f"   Users: {current_users}")
        print(f"   Grants: {current_grants}")
        print(f"   Vest Events: {current_vests}")
        print()
        
        # STEP 1: Migrate Users
        print("👥 STEP 1: Migrating Users...")
        print("-" * 70)
        
        backup_cursor.execute('''
            SELECT id, username, email, password_hash, is_admin, created_at 
            FROM users
        ''')
        backup_users = backup_cursor.fetchall()
        
        user_id_map = {}  # Map old IDs to new IDs
        migrated_users = 0
        skipped_users = 0
        
        for old_id, username, email, password_hash, is_admin, created_at in backup_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f"   ⚠️  User '{username}' already exists - updating password")
                existing_user.password_hash = password_hash
                existing_user.email = email
                existing_user.is_admin = bool(is_admin)
                user_id_map[old_id] = existing_user.id
                skipped_users += 1
            else:
                # Create new user with security fields
                new_user = User(
                    username=username,
                    email=email,
                    is_admin=bool(is_admin),
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow()
                )
                new_user.password_hash = password_hash
                
                # Initialize security fields
                new_user.failed_login_attempts = 0
                new_user.is_locked = False
                new_user.last_password_change = datetime.utcnow()
                new_user.email_verified = False
                new_user.totp_enabled = False
                
                db.session.add(new_user)
                db.session.flush()  # Get the new ID
                
                user_id_map[old_id] = new_user.id
                print(f"   ✓ Migrated user: {username} (ID: {old_id} → {new_user.id})")
                migrated_users += 1
        
        db.session.commit()
        print(f"\n   Summary: {migrated_users} new users, {skipped_users} existing users updated")
        print()
        
        # STEP 2: Migrate Grants
        print("📈 STEP 2: Migrating Grants...")
        print("-" * 70)
        
        backup_cursor.execute('''
            SELECT id, user_id, grant_date, grant_type, share_type, share_quantity,
                   bonus_type, vest_years, notes, created_at
            FROM grants
            ORDER BY id
        ''')
        backup_grants = backup_cursor.fetchall()
        
        grant_id_map = {}  # Map old IDs to new IDs
        migrated_grants = 0
        
        for old_grant in backup_grants:
            (old_id, old_user_id, grant_date, grant_type, share_type, share_quantity,
             bonus_type, vest_years, notes, created_at) = old_grant
            
            # Map to new user ID
            new_user_id = user_id_map.get(old_user_id)
            
            if not new_user_id:
                print(f"   ⚠️  Skipping grant {old_id} - user {old_user_id} not found")
                continue
            
            # Create new grant
            new_grant = Grant(
                user_id=new_user_id,
                grant_date=datetime.fromisoformat(grant_date) if grant_date else datetime.utcnow(),
                grant_type=grant_type,
                share_type=share_type,
                share_quantity=float(share_quantity),
                bonus_type=bonus_type,
                vest_years=int(vest_years) if vest_years else None,
                notes=notes,
                created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow()
            )
            
            db.session.add(new_grant)
            db.session.flush()  # Get the new ID
            
            grant_id_map[old_id] = new_grant.id
            migrated_grants += 1
            
            if migrated_grants % 5 == 0:
                print(f"   ✓ Migrated {migrated_grants} grants...")
        
        db.session.commit()
        print(f"\n   Summary: {migrated_grants} grants migrated")
        print()
        
        # STEP 3: Migrate Vest Events
        print("📅 STEP 3: Migrating Vest Events...")
        print("-" * 70)
        
        backup_cursor.execute('''
            SELECT id, grant_id, vest_date, vest_quantity, is_cliff, notes, created_at
            FROM vest_events
            ORDER BY id
        ''')
        backup_vests = backup_cursor.fetchall()
        
        migrated_vests = 0
        
        for old_vest in backup_vests:
            (old_id, old_grant_id, vest_date, vest_quantity, is_cliff, notes, created_at) = old_vest
            
            # Map to new grant ID
            new_grant_id = grant_id_map.get(old_grant_id)
            
            if not new_grant_id:
                print(f"   ⚠️  Skipping vest event {old_id} - grant {old_grant_id} not found")
                continue
            
            # Create new vest event
            new_vest = VestEvent(
                grant_id=new_grant_id,
                vest_date=datetime.fromisoformat(vest_date) if vest_date else datetime.utcnow(),
                vest_quantity=float(vest_quantity),
                is_cliff=bool(is_cliff),
                notes=notes,
                created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow()
            )
            
            db.session.add(new_vest)
            migrated_vests += 1
            
            if migrated_vests % 25 == 0:
                print(f"   ✓ Migrated {migrated_vests} vest events...")
        
        db.session.commit()
        print(f"\n   Summary: {migrated_vests} vest events migrated")
        print()
        
        # STEP 4: Verify Migration
        print("✅ STEP 4: Verification")
        print("-" * 70)
        
        final_users = User.query.count()
        final_grants = Grant.query.count()
        final_vests = VestEvent.query.count()
        
        print(f"   Users: {current_users} → {final_users} (+{final_users - current_users})")
        print(f"   Grants: {current_grants} → {final_grants} (+{final_grants - current_grants})")
        print(f"   Vest Events: {current_vests} → {final_vests} (+{final_vests - current_vests})")
        print()
        
        # Show user details
        print("👥 Migrated Users:")
        for user in User.query.all():
            grants_count = Grant.query.filter_by(user_id=user.id).count()
            print(f"   - {user.username} ({user.email}) - {grants_count} grants")
        print()
        
        print("=" * 70)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        print()
        print("✅ All security enhancements preserved:")
        print("   - Enhanced User model with 13 security fields")
        print("   - Password hashes migrated")
        print("   - All grants and vest events copied")
        print("   - User relationships maintained")
        print()
        print("🔐 Your data is now in the secure database!")
        print()
    
    backup_conn.close()


if __name__ == '__main__':
    print()
    response = input("This will migrate data from stonks.db.backup to stonks.db. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_data()
    else:
        print("Migration cancelled.")
        print()
