"""
Migration script to recalculate all vest events with whole share rounding.
"""
from app import create_app, db
from app.models.grant import Grant
from app.models.vest_event import VestEvent
from app.utils.vest_calculator import calculate_vest_schedule

app = create_app()

with app.app_context():
    grants = Grant.query.all()
    print(f"Processing {len(grants)} grants...")
    
    for grant in grants:
        # Delete old vest events
        VestEvent.query.filter_by(grant_id=grant.id).delete()
        
        # Recalculate with rounding
        vest_schedule = calculate_vest_schedule(grant)
        
        for vest in vest_schedule:
            vest_event = VestEvent(
                grant_id=grant.id,
                vest_date=vest['vest_date'],
                shares_vested=vest['shares']
            )
            db.session.add(vest_event)
        
        total = sum(v['shares'] for v in vest_schedule)
        print(f"  Grant {grant.id}: {len(vest_schedule)} vests, total {total} shares (grant: {grant.share_quantity})")
    
    db.session.commit()
    print("Done! All vest events now have whole share amounts.")
