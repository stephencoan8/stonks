#!/usr/bin/env python
"""Check database schema."""
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    print("\nVestEvent columns:")
    for col in inspector.get_columns('vest_events'):
        print(f"  {col['name']}: {col['type']}")
    
    # Also check some actual data
    from app.models.vest_event import VestEvent
    vest_events = VestEvent.query.limit(3).all()
    print(f"\nFound {VestEvent.query.count()} vest events")
    if vest_events:
        print("\nSample vest event data:")
        for ve in vest_events:
            print(f"  ID {ve.id}: payment_method={ve.payment_method}, cash={ve.cash_to_cover}, shares_sold={ve.shares_sold_to_cover}")
