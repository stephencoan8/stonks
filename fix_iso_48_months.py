#!/usr/bin/env python3
"""
Fix ISO vesting schedules to use 48 months (4 years) instead of 60 months.

Both ISO 5Y and ISO 6Y should vest over 4 years from vesting start:
- ISO 5Y: Vests from year 1 to year 5 (48 months)
- ISO 6Y: Vests from year 2 to year 6 (48 months)

Vesting pattern:
- First vest at 6-month cliff: 6/48 of total shares
- Monthly thereafter: 1/48 of total shares for 42 more months
- Total: 48 monthly vests
"""

from app import create_app, db
from app.models.grant import Grant, ShareType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule

def fix_iso_vesting():
    """Fix all ISO grants to use 48-month vesting period."""
    app = create_app()
    
    with app.app_context():
        # Find all ISO grants (both 5Y and 6Y)
        iso_grants = Grant.query.filter(
            Grant.share_type.in_([ShareType.ISO_5Y.value, ShareType.ISO_6Y.value])
        ).all()
        
        if not iso_grants:
            print("No ISO grants found.")
            return
        
        print(f"Found {len(iso_grants)} ISO grant(s) to fix\n")
        
        for grant in iso_grants:
            print(f"Processing Grant #{grant.id}:")
            print(f"  Type: {grant.share_type.upper()}")
            print(f"  Shares: {grant.share_quantity}")
            print(f"  Grant Date: {grant.grant_date}")
            
            # Show old vesting
            old_vests = VestEvent.query.filter_by(grant_id=grant.id).order_by(VestEvent.vest_date).all()
            print(f"  Old vest count: {len(old_vests)} vests")
            if old_vests:
                print(f"    First vest: {old_vests[0].vest_date} - {old_vests[0].shares_vested:.2f} shares")
                if len(old_vests) > 1:
                    print(f"    Second vest: {old_vests[1].vest_date} - {old_vests[1].shares_vested:.2f} shares")
                print(f"    Last vest: {old_vests[-1].vest_date} - {old_vests[-1].shares_vested:.2f} shares")
            
            # Delete old vest events
            VestEvent.query.filter_by(grant_id=grant.id).delete()
            
            # Recalculate with 48-month logic
            new_vest_schedule = calculate_vest_schedule(grant)
            
            # Create new vest events
            for vest_data in new_vest_schedule:
                vest_event = VestEvent(
                    grant_id=grant.id,
                    vest_date=vest_data['vest_date'],
                    shares_vested=vest_data['shares']
                )
                db.session.add(vest_event)
            
            print(f"  New vest count: {len(new_vest_schedule)} vests")
            print(f"    First vest: {new_vest_schedule[0]['vest_date']} - {new_vest_schedule[0]['shares']:.2f} shares (6/48 = {grant.share_quantity * 6 / 48:.2f})")
            if len(new_vest_schedule) > 1:
                print(f"    Second vest: {new_vest_schedule[1]['vest_date']} - {new_vest_schedule[1]['shares']:.2f} shares (1/48 = {grant.share_quantity / 48:.2f})")
            print(f"    Last vest: {new_vest_schedule[-1]['vest_date']} - {new_vest_schedule[-1]['shares']:.2f} shares")
            print()
        
        # Commit changes
        db.session.commit()
        print("✅ All ISO grants updated successfully!")
        print(f"   Both ISO 5Y and ISO 6Y now vest over 48 months (4 years)")
        print(f"   First vest: 6/48 of shares, then 1/48 monthly for 42 more months")

if __name__ == '__main__':
    fix_iso_vesting()
