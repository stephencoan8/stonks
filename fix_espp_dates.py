"""
Fix ESPP grants to vest on the grant date (not the next ESPP payment date).
For ESPP, the grant_date IS the vest date (the date shares were received).
"""

from app import create_app
from app.models.grant import Grant, GrantType
from app.models.vest_event import VestEvent
from app.utils.init_db import get_stock_price_at_date
from app import db

def fix_espp_vests():
    """Fix all ESPP grants to vest immediately on grant date."""
    app = create_app()
    
    with app.app_context():
        # Find all ESPP grants
        espp_grants = Grant.query.filter(
            Grant.grant_type.in_([GrantType.ESPP.value, GrantType.NQESPP.value])
        ).all()
        
        print(f"Found {len(espp_grants)} ESPP/NQESPP grants to fix\n")
        
        for grant in espp_grants:
            print(f"Grant {grant.id}: {grant.grant_type}")
            print(f"  Grant Date: {grant.grant_date}")
            
            # Get current vest event
            vest_event = VestEvent.query.filter_by(grant_id=grant.id).first()
            
            if vest_event:
                old_vest_date = vest_event.vest_date
                print(f"  Current vest date: {old_vest_date}")
                
                # Check if it needs fixing
                if vest_event.vest_date != grant.grant_date:
                    print(f"  ❌ NEEDS FIX: vest date should match grant date")
                    
                    # Update vest date to grant date
                    vest_event.vest_date = grant.grant_date
                    vest_event.share_price_at_vest = get_stock_price_at_date(grant.grant_date)
                    
                    db.session.commit()
                    
                    print(f"  ✅ FIXED: {old_vest_date} → {grant.grant_date}")
                    print(f"     Stock price: ${vest_event.share_price_at_vest:.2f}")
                else:
                    print(f"  ✅ Already correct")
            else:
                print(f"  ⚠️  No vest event found")
            
            print()

if __name__ == '__main__':
    fix_espp_vests()
    print("All ESPP grants have been fixed!")
    print("\nESPP grants now vest immediately on the grant date you enter.")
    print("The grant date should be the actual date you received the ESPP shares.")
