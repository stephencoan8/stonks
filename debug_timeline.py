"""
Debug script to check the vesting timeline data generation.
"""
from app import create_app
from app.models.grant import Grant
from app.models.vest_event import VestEvent
from app.models.stock_price import StockPrice
from datetime import date

app = create_app()

with app.app_context():
    # Simulate the timeline generation from main.py
    
    # Get all vest events for user 2 (actual user with data)
    all_vest_events = VestEvent.query.join(Grant).filter(
        Grant.user_id == 2
    ).order_by(VestEvent.vest_date).all()
    
    # Get all stock price updates
    all_stock_prices = StockPrice.query.order_by(StockPrice.valuation_date).all()
    
    print(f"Total vest events: {len(all_vest_events)}")
    print(f"Total stock prices: {len(all_stock_prices)}")
    
    # Create a timeline of all significant dates
    timeline_events = []
    
    # Add all vest events
    for vest in all_vest_events:
        timeline_events.append({
            'date': vest.vest_date,
            'type': 'vest',
            'vest': vest
        })
    
    # Add all stock price updates
    for price in all_stock_prices:
        timeline_events.append({
            'date': price.valuation_date,
            'type': 'price_update',
            'price': price.price_per_share
        })
    
    # Sort all events by date
    timeline_events.sort(key=lambda x: x['date'])
    
    print(f"\nTotal timeline events: {len(timeline_events)}")
    print("\nFirst 10 events:")
    for i, event in enumerate(timeline_events[:10]):
        print(f"{i+1}. {event['date']} - {event['type']}")
        if event['type'] == 'vest':
            print(f"   Vest: {event['vest'].shares_vested} shares")
        else:
            print(f"   Price: ${event['price']}")
    
    # Calculate cumulative values at each point in time
    vesting_timeline = []
    cumulative_vested_shares = 0
    cumulative_total_shares = 0
    processed_vests = set()
    
    for event in timeline_events:
        event_date = event['date']
        
        # Process vest if this is a vest event
        if event['type'] == 'vest':
            vest = event['vest']
            if vest.id not in processed_vests:
                processed_vests.add(vest.id)
                cumulative_total_shares += vest.shares_received
                
                if vest.has_vested:
                    cumulative_vested_shares += vest.shares_received
        
        # Get the stock price at this point in time
        price_at_date = 0
        for price in all_stock_prices:
            if price.valuation_date <= event_date:
                price_at_date = price.price_per_share
            else:
                break
        
        if price_at_date == 0:
            continue  # Skip if no price data available yet
        
        # Calculate values
        vested_value = cumulative_vested_shares * price_at_date
        total_value = cumulative_total_shares * price_at_date
        
        # Only add point if there's actual data to show
        if cumulative_total_shares > 0:
            vesting_timeline.append({
                'date': event_date.strftime('%Y-%m-%d'),
                'vested_shares': cumulative_vested_shares,
                'total_shares': cumulative_total_shares,
                'vested_value': vested_value,
                'total_value': total_value,
                'is_vested': event_date <= date.today(),
                'price_at_date': price_at_date,
                'event_type': event['type']
            })
    
    print(f"\nTotal vesting timeline points: {len(vesting_timeline)}")
    print("\nFirst 15 timeline points:")
    for i, point in enumerate(vesting_timeline[:15]):
        print(f"{i+1}. {point['date']} ({point['event_type']})")
        print(f"   Price at date: ${point['price_at_date']}")
        print(f"   Vested shares: {point['vested_shares']}")
        print(f"   Total shares: {point['total_shares']}")
        print(f"   Vested value: ${point['vested_value']:,.2f}")
        print(f"   Total value: ${point['total_value']:,.2f}")
        print()
    
    print("\nLast 5 timeline points:")
    for i, point in enumerate(vesting_timeline[-5:]):
        print(f"{len(vesting_timeline)-4+i}. {point['date']} ({point['event_type']})")
        print(f"   Price at date: ${point['price_at_date']}")
        print(f"   Total shares: {point['total_shares']}")
        print(f"   Total value: ${point['total_value']:,.2f}")
        print()
