"""
Fix ISO 6Y vesting to vest over 4 years (48 months) instead of 5 years (60 months).

ISO 6Y should:
- Start vesting 2 years after grant
- Vest over 4 years (48 months total)
- Cliff at 6 months (2.5 years from grant)
- First vest: 6/48 of total shares
- Monthly vests: 1/48 of total shares for remaining 42 months
"""

from app import create_app, db
from app.models.grant import Grant, ShareType
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule

app = create_app()

with app.app_context():
    # Find all ISO 6Y grants
    iso_6y_grants = Grant.query.filter_by(share_type=ShareType.ISO_6Y.value).all()
    
    print(f"Found {len(iso_6y_grants)} ISO 6Y grant(s)")
    
    for grant in iso_6y_grants:
        print(f"\nProcessing Grant #{grant.id}:")
        print(f"  Shares: {grant.share_quantity}")
        print(f"  Grant Date: {grant.grant_date}")
        
        # Delete existing vest events
        old_events = VestEvent.query.filter_by(grant_id=grant.id).all()
        print(f"  Deleting {len(old_events)} old vest events...")
        for event in old_events:
            db.session.delete(event)
        
        # Recalculate vest schedule
        print(f"  Recalculating vest schedule (4-year vesting)...")
        vest_schedule = calculate_vest_schedule(grant)
        
        # Create new vest events
        for vest in vest_schedule:
            new_event = VestEvent(
                grant_id=grant.id,
                vest_date=vest['vest_date'],
                shares_vested=vest['shares']
            )
            db.session.add(new_event)
        
        print(f"  Created {len(vest_schedule)} new vest events")
        
        # Show first few vests
        print(f"  First 3 vests:")
        for i, vest in enumerate(vest_schedule[:3]):
            print(f"    {i+1}. {vest['vest_date']}: {vest['shares']:.2f} shares")
    
    # Commit changes
    db.session.commit()
    print("\n✅ ISO 6Y vesting fixed!")
    print(f"✅ Now vests over 4 years (48 months) instead of 5 years")
