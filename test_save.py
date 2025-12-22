#!/usr/bin/env python
"""Test saving vest event data."""
from app import create_app, db
from app.models.vest_event import VestEvent

app = create_app()
with app.app_context():
    # Get a vest event
    vest = VestEvent.query.first()
    if vest:
        print(f"\nBefore update:")
        print(f"  ID: {vest.id}")
        print(f"  Payment method: {vest.payment_method}")
        print(f"  Cash to cover: {vest.cash_to_cover}")
        print(f"  Shares sold: {vest.shares_sold_to_cover}")
        
        # Update it
        vest.payment_method = 'sell_to_cover'
        vest.shares_sold_to_cover = 25.5
        vest.cash_to_cover = 0
        db.session.commit()
        
        print(f"\nAfter update and commit:")
        print(f"  Payment method: {vest.payment_method}")
        print(f"  Cash to cover: {vest.cash_to_cover}")
        print(f"  Shares sold: {vest.shares_sold_to_cover}")
        
        # Query it again to verify
        vest2 = VestEvent.query.get(vest.id)
        print(f"\nRe-queried from database:")
        print(f"  Payment method: {vest2.payment_method}")
        print(f"  Cash to cover: {vest2.cash_to_cover}")
        print(f"  Shares sold: {vest2.shares_sold_to_cover}")
    else:
        print("No vest events found")
