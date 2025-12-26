"""
Fix ISO grants that were created with old vesting logic.
This script updates vest_years and cliff_years, then regenerates vesting schedules.
"""

from app import create_app
from app.models.grant import Grant, GrantType, ShareType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule, get_grant_configuration
from app.utils.init_db import get_stock_price_at_date
from app import db

def fix_iso_grants():
    """Fix all ISO grants with incorrect vest_years/cliff_years."""
    app = create_app()
    
    with app.app_context():
        # Find all ISO grants
        iso_grants = Grant.query.filter(
            Grant.share_type.in_([ShareType.ISO_5Y.value, ShareType.ISO_6Y.value])
        ).all()
        
        print(f"Found {len(iso_grants)} ISO grants to check\n")
        
        for grant in iso_grants:
            print(f"Grant {grant.id}: {grant.grant_type} - {grant.share_type}")
            print(f"  Current: vest_years={grant.vest_years}, cliff_years={grant.cliff_years}")
            
            # Get correct configuration
            vest_years, cliff_years = get_grant_configuration(
                grant.grant_type, 
                grant.share_type, 
                grant.bonus_type
            )
            
            print(f"  Correct: vest_years={vest_years}, cliff_years={cliff_years}")
            
            # Check if needs fixing
            if grant.vest_years != vest_years or grant.cliff_years != cliff_years:
                print(f"  ❌ NEEDS FIX")
                
                # Update grant configuration
                grant.vest_years = vest_years
                grant.cliff_years = cliff_years
                
                # Delete old vest events
                old_count = VestEvent.query.filter_by(grant_id=grant.id).count()
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
                
                new_count = len(vest_schedule)
                print(f"  ✅ FIXED: {old_count} -> {new_count} vest events")
                print(f"     First vest: {vest_schedule[0]['vest_date']} - {vest_schedule[0]['shares']} shares")
                print(f"     Last vest: {vest_schedule[-1]['vest_date']} - {vest_schedule[-1]['shares']} shares")
            else:
                print(f"  ✅ Already correct")
            
            print()

if __name__ == '__main__':
    fix_iso_grants()
    print("All ISO grants have been fixed!")
