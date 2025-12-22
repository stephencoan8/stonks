"""
Fix annual bonus grants with 1-year cliff to use the closest vest date.
"""

from app import create_app
from app.models.grant import Grant, GrantType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule
from app.utils.init_db import get_stock_price_at_date
from app import db

def fix_annual_bonus_cliffs():
    """Fix all annual bonus grants with 1-year cliff."""
    app = create_app()
    
    with app.app_context():
        # Find all annual performance grants with 1 year cliff
        grants = Grant.query.filter_by(
            grant_type=GrantType.ANNUAL_PERFORMANCE.value,
            cliff_years=1.0
        ).all()
        
        print(f"Found {len(grants)} annual bonus grants with 1-year cliff\n")
        
        for grant in grants:
            print(f"Grant {grant.id}: {grant.share_type}")
            print(f"  Grant Date: {grant.grant_date}")
            
            # Get current vest event
            old_events = VestEvent.query.filter_by(grant_id=grant.id).all()
            if old_events:
                print(f"  Old vest date: {old_events[0].vest_date}")
            
            # Delete old vest events
            VestEvent.query.filter_by(grant_id=grant.id).delete()
            
            # Recalculate with new logic
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
            
            print(f"  ✅ New vest date: {vest_schedule[0]['vest_date']}")
            print(f"     Stock price: ${get_stock_price_at_date(vest_schedule[0]['vest_date']):.2f}")
            print()

if __name__ == '__main__':
    fix_annual_bonus_cliffs()
    print("All annual bonus grants have been fixed!")
    print("\nAnnual bonuses now vest at the closest SpaceX vest date (6/15 or 11/15)")
    print("to the 1-year anniversary of the grant date.")
