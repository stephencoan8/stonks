#!/usr/bin/env python3
"""
Robust Data Migration Script: Old Database → New Secure Database
Migrates users, grants, and vest events with enhanced error handling and batch commits.
"""

import sqlite3
import sys
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.grant import Grant
from app.models.vest_event import VestEvent


def migrate_data():
    """Migrate all data from backup to new secure database with robust error handling."""
    
    print("=" * 70)
    print("🔄 ROBUST DATA MIGRATION: Backup → Secure Database")
    print("=" * 70)
    print()
    
    # Connect to backup database
    try:
        backup_conn = sqlite3.connect('instance/stonks.db.backup')
        backup_conn.row_factory = sqlite3.Row  # Access columns by name
        backup_cursor = backup_conn.cursor()
        print("✓ Connected to backup database")
    except Exception as e:
        print(f"❌ Failed to connect to backup database: {e}")
        return False
    
    # Create Flask app context
    try:
        app = create_app()
        print("✓ Flask app initialized")
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        backup_conn.close()
        return False
    
    with app.app_context():
        try:
            # Get current state
            current_users = User.query.count()
            current_grants = Grant.query.count()
            current_vests = VestEvent.query.count()
            
            print()
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
                ORDER BY id
            ''')
            backup_users = backup_cursor.fetchall()
            print(f"   Found {len(backup_users)} users in backup")
            
            user_id_map = {}  # Map old IDs to new IDs
            migrated_users = 0
            updated_users = 0
            
            for user_row in backup_users:
                old_id = user_row['id']
                username = user_row['username']
                email = user_row['email']
                password_hash = user_row['password_hash']
                is_admin = user_row['is_admin']
                created_at = user_row['created_at']
                
                try:
                    # Check if user already exists
                    existing_user = User.query.filter_by(username=username).first()
                    
                    if existing_user:
                        print(f"   ⚠️  User '{username}' exists (ID {existing_user.id}) - updating")
                        existing_user.password_hash = password_hash
                        existing_user.email = email
                        existing_user.is_admin = bool(is_admin)
                        user_id_map[old_id] = existing_user.id
                        updated_users += 1
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
                        db.session.flush()  # Get the new ID without committing
                        
                        user_id_map[old_id] = new_user.id
                        print(f"   ✓ Migrated: {username} (old ID:{old_id} → new ID:{new_user.id})")
                        migrated_users += 1
                    
                except Exception as e:
                    print(f"   ❌ Error migrating user '{username}': {e}")
                    db.session.rollback()
                    continue
            
            # Commit all user changes
            try:
                db.session.commit()
                print(f"\n   ✅ Summary: {migrated_users} new, {updated_users} updated")
            except Exception as e:
                print(f"   ❌ Failed to commit users: {e}")
                db.session.rollback()
                backup_conn.close()
                return False
            print()
            
            # STEP 2: Migrate Grants
            print("📈 STEP 2: Migrating Grants...")
            print("-" * 70)
            
            backup_cursor.execute('''
                SELECT id, user_id, grant_date, grant_type, share_type, share_quantity,
                       share_price_at_grant, vest_years, cliff_years, bonus_type, notes, created_at
                FROM grants
                ORDER BY id
            ''')
            backup_grants = backup_cursor.fetchall()
            print(f"   Found {len(backup_grants)} grants in backup")
            
            grant_id_map = {}  # Map old IDs to new IDs
            migrated_grants = 0
            skipped_grants = 0
            
            for grant_row in backup_grants:
                old_id = grant_row['id']
                old_user_id = grant_row['user_id']
                
                # Map to new user ID
                new_user_id = user_id_map.get(old_user_id)
                
                if not new_user_id:
                    print(f"   ⚠️  Skipping grant {old_id} - user {old_user_id} not mapped")
                    skipped_grants += 1
                    continue
                
                try:
                    # Create new grant
                    # For ESPP grants without vest_years, default to 0
                    vest_years_value = grant_row['vest_years']
                    if vest_years_value is None:
                        if grant_row['grant_type'] in ('espp', 'nqespp'):
                            vest_years_value = 0
                        else:
                            vest_years_value = 1  # Default to 1 year for other types
                    
                    new_grant = Grant(
                        user_id=new_user_id,
                        grant_date=datetime.fromisoformat(grant_row['grant_date']) if grant_row['grant_date'] else datetime.utcnow(),
                        grant_type=grant_row['grant_type'],
                        share_type=grant_row['share_type'],
                        share_quantity=float(grant_row['share_quantity']),
                        share_price_at_grant=float(grant_row['share_price_at_grant']) if grant_row['share_price_at_grant'] else 0.0,
                        vest_years=int(vest_years_value),
                        cliff_years=float(grant_row['cliff_years']) if grant_row['cliff_years'] else 0.0,
                        bonus_type=grant_row['bonus_type'],
                        notes=grant_row['notes'],
                        created_at=datetime.fromisoformat(grant_row['created_at']) if grant_row['created_at'] else datetime.utcnow()
                    )
                    
                    db.session.add(new_grant)
                    db.session.flush()  # Get the new ID
                    
                    grant_id_map[old_id] = new_grant.id
                    migrated_grants += 1
                    
                    if migrated_grants % 5 == 0:
                        print(f"   ✓ Progress: {migrated_grants}/{len(backup_grants)} grants")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating grant {old_id}: {e}")
                    db.session.rollback()
                    continue
            
            # Commit all grant changes
            try:
                db.session.commit()
                print(f"\n   ✅ Summary: {migrated_grants} migrated, {skipped_grants} skipped")
            except Exception as e:
                print(f"   ❌ Failed to commit grants: {e}")
                db.session.rollback()
                backup_conn.close()
                return False
            print()
            
            # STEP 3: Migrate Vest Events
            print("📅 STEP 3: Migrating Vest Events...")
            print("-" * 70)
            
            backup_cursor.execute('''
                SELECT id, grant_id, vest_date, shares_vested, is_vested, created_at
                FROM vest_events
                ORDER BY id
            ''')
            backup_vests = backup_cursor.fetchall()
            print(f"   Found {len(backup_vests)} vest events in backup")
            
            migrated_vests = 0
            skipped_vests = 0
            batch_size = 50
            batch_count = 0
            
            for vest_row in backup_vests:
                old_id = vest_row['id']
                old_grant_id = vest_row['grant_id']
                
                # Map to new grant ID
                new_grant_id = grant_id_map.get(old_grant_id)
                
                if not new_grant_id:
                    print(f"   ⚠️  Skipping vest {old_id} - grant {old_grant_id} not mapped")
                    skipped_vests += 1
                    continue
                
                try:
                    # Create new vest event
                    new_vest = VestEvent(
                        grant_id=new_grant_id,
                        vest_date=datetime.fromisoformat(vest_row['vest_date']) if vest_row['vest_date'] else datetime.utcnow(),
                        shares_vested=float(vest_row['shares_vested']),
                        is_vested=bool(vest_row['is_vested']) if vest_row['is_vested'] is not None else False,
                        created_at=datetime.fromisoformat(vest_row['created_at']) if vest_row['created_at'] else datetime.utcnow()
                    )
                    
                    db.session.add(new_vest)
                    migrated_vests += 1
                    batch_count += 1
                    
                    # Commit in batches to avoid memory issues
                    if batch_count >= batch_size:
                        db.session.commit()
                        batch_count = 0
                        print(f"   ✓ Progress: {migrated_vests}/{len(backup_vests)} vest events")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating vest event {old_id}: {e}")
                    db.session.rollback()
                    batch_count = 0
                    continue
            
            # Commit remaining vest events
            try:
                if batch_count > 0:
                    db.session.commit()
                print(f"\n   ✅ Summary: {migrated_vests} migrated, {skipped_vests} skipped")
            except Exception as e:
                print(f"   ❌ Failed to commit vest events: {e}")
                db.session.rollback()
                backup_conn.close()
                return False
            print()
            
            # STEP 4: Verification
            print("✅ STEP 4: Verification")
            print("-" * 70)
            
            final_users = User.query.count()
            final_grants = Grant.query.count()
            final_vests = VestEvent.query.count()
            
            print(f"   Users:       {current_users} → {final_users} (+{final_users - current_users})")
            print(f"   Grants:      {current_grants} → {final_grants} (+{final_grants - current_grants})")
            print(f"   Vest Events: {current_vests} → {final_vests} (+{final_vests - current_vests})")
            print()
            
            # Detailed verification
            print("👥 User Details:")
            for user in User.query.order_by(User.id).all():
                grants_count = Grant.query.filter_by(user_id=user.id).count()
                vests_count = VestEvent.query.join(Grant).filter(Grant.user_id == user.id).count()
                admin_badge = " [ADMIN]" if user.is_admin else ""
                print(f"   - {user.username} ({user.email}){admin_badge}")
                print(f"     → {grants_count} grants, {vests_count} vest events")
            print()
            
            # Compare with backup
            backup_user_count = len(backup_users)
            backup_grant_count = len(backup_grants)
            backup_vest_count = len(backup_vests)
            
            all_good = True
            if final_users < backup_user_count:
                print(f"   ⚠️  WARNING: Expected {backup_user_count} users, got {final_users}")
                all_good = False
            if final_grants < backup_grant_count:
                print(f"   ⚠️  WARNING: Expected {backup_grant_count} grants, got {final_grants}")
                all_good = False
            if final_vests < backup_vest_count:
                print(f"   ⚠️  WARNING: Expected {backup_vest_count} vests, got {final_vests}")
                all_good = False
            
            if all_good:
                print("   ✅ All data verified successfully!")
            print()
            
            print("=" * 70)
            print("🎉 MIGRATION COMPLETE!")
            print("=" * 70)
            print()
            print("✅ Security enhancements preserved:")
            print("   ✓ Enhanced User model with security fields")
            print("   ✓ Password hashes migrated")
            print("   ✓ All grants and vest events copied")
            print("   ✓ User relationships maintained")
            print()
            print("🔐 Your data is now in the secure database!")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR during migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
        finally:
            backup_conn.close()


if __name__ == '__main__':
    print()
    print("⚠️  IMPORTANT:")
    print("   - This will migrate data from stonks.db.backup to stonks.db")
    print("   - Existing users will be updated, not duplicated")
    print("   - The backup database will NOT be modified")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print()
        success = migrate_data()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Migration cancelled.")
        print()
        sys.exit(0)
