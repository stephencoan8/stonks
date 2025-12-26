"""
Fix ALL RSU/RSA grants to use the closest vest date to cliff anniversary.
This applies to new hire, promotion, and all other grant types.
"""

from app import create_app
from app.models.grant import Grant, ShareType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule
from app.utils.init_db import get_stock_price_at_date
from app import db

def fix_all_rsu_cliffs():
    """Fix all RSU grants to use closest vest date logic."""
    app = create_app()
    
    with app.app_context():
        # Find all RSU grants (not ISOs, not ESPP)
        grants = Grant.query.filter(
            Grant.share_type == ShareType.RSU.value
        ).all()
        
        print(f"Found {len(grants)} RSU grants to check\n")
        
        fixed_count = 0
        
        for grant in grants:
            print(f"Grant {grant.id}: {grant.grant_type}")
            print(f"  Grant Date: {grant.grant_date}")
            print(f"  Cliff: {grant.cliff_years} years")
            
            # Get current vest events
            old_events = VestEvent.query.filter_by(grant_id=grant.id).order_by(VestEvent.vest_date).all()
            if old_events:
                old_first_vest = old_events[0].vest_date
                print(f"  Old first vest: {old_first_vest}")
            else:
                print(f"  No vest events found")
                continue
            
            # Calculate new schedule
            new_schedule = calculate_vest_schedule(grant)
            new_first_vest = new_schedule[0]['vest_date']
            
            # Check if it needs fixing
            if old_first_vest != new_first_vest:
                print(f"  ❌ NEEDS FIX")
                
                # Delete old vest events
                VestEvent.query.filter_by(grant_id=grant.id).delete()
                
                # Create new vest events
                for vest in new_schedule:
                    vest_event = VestEvent(
                        grant_id=grant.id,
                        vest_date=vest['vest_date'],
                        shares_vested=vest['shares'],
                        share_price_at_vest=get_stock_price_at_date(vest['vest_date'])
                    )
                    db.session.add(vest_event)
                
                db.session.commit()
                
                print(f"  ✅ FIXED: {old_first_vest} → {new_first_vest}")
                print(f"     Total vests: {len(old_events)} → {len(new_schedule)}")
                fixed_count += 1
            else:
                print(f"  ✅ Already correct")
            
            print()
        
        print(f"\n{'='*70}")
        print(f"Fixed {fixed_count} out of {len(grants)} grants")
        print(f"{'='*70}")

if __name__ == '__main__':
    fix_all_rsu_cliffs()
    print("\nAll RSU grants now use the closest vest date to cliff anniversary!")
