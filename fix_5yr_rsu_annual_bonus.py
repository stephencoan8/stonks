"""
Fix 5-year RSU annual bonuses to vest properly over 5 years.
Similar to ISO 5Y but with biannual vesting instead of monthly.
"""

from app import create_app
from app.models.grant import Grant, GrantType, ShareType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule
from app.utils.init_db import get_stock_price_at_date
from app import db

def fix_5yr_rsu_annual_bonus():
    """Fix 5-year RSU annual bonuses."""
    app = create_app()
    
    with app.app_context():
        # Find 5-year RSU annual bonuses that need fixing
        grants = Grant.query.filter_by(
            grant_type=GrantType.ANNUAL_PERFORMANCE.value,
            share_type=ShareType.RSU.value,
            bonus_type='long_term'
        ).all()
        
        print(f"Found {len(grants)} long-term RSU annual bonuses\n")
        
        for grant in grants:
            print(f"Grant {grant.id}:")
            print(f"  Grant Date: {grant.grant_date}")
            print(f"  Current: vest_years={grant.vest_years}, cliff={grant.cliff_years}")
            
            # Get current vest events
            old_events = VestEvent.query.filter_by(grant_id=grant.id).all()
            if old_events:
                print(f"  Old schedule: {len(old_events)} vests from {old_events[0].vest_date} to {old_events[-1].vest_date}")
            
            # Check if needs fixing
            if grant.vest_years != 5 or grant.cliff_years != 1.5:
                print(f"  ❌ NEEDS FIX")
                
                # Update grant configuration
                grant.vest_years = 5
                grant.cliff_years = 1.5
                
                # Delete old vest events
                VestEvent.query.filter_by(grant_id=grant.id).delete()
                
                # Recalculate vest schedule
                vest_schedule = calculate_vest_schedule(grant)
                
                # Create new vest events
                for vest in vest_schedule:
                    vest_event = VestEvent(
                        grant_id=grant.id,
                        vest_date=vest['vest_date'],
                        shares_vested=vest['shares'],
                        share_price_at_vest=get_stock_price_at_date(vest['vest_date'])
                    )
                    db.session.add(vest_event)
                
                db.session.commit()
                
                print(f"  ✅ FIXED: vest_years 5, cliff 1.5 years")
                print(f"     New schedule: {len(vest_schedule)} vests from {vest_schedule[0]['vest_date']} to {vest_schedule[-1]['vest_date']}")
                print(f"     First vest: {vest_schedule[0]['shares']:.2f} shares (1/10 of total)")
                print(f"     Each subsequent: {vest_schedule[1]['shares']:.2f} shares (1/9 of remaining)" if len(vest_schedule) > 1 else "")
            else:
                print(f"  ✅ Already correct")
            
            print()

if __name__ == '__main__':
    fix_5yr_rsu_annual_bonus()
    print("All 5-year RSU annual bonuses have been fixed!")
    print("\n5-year RSU annual bonuses now vest like ISO 5Y but biannually:")
    print("  - Vesting starts 1 year after grant")
    print("  - Cliff at 1.5 years (first vest)")
    print("  - First vest = 1/10 of total (6 months worth)")
    print("  - Then 9 biannual vests for remaining 54 months")
    print("  - Total: 10 vests over 60 months")
