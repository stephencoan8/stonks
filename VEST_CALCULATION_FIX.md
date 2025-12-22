# Dashboard Vested Calculation Fix

## Issue
The dashboard was not accurately counting vested shares and their value. It was showing 0 or incorrect values for "Shares Received (Net)" and "Vested Inventory Value".

## Root Cause
The dashboard route was filtering vest events using the database column `is_vested`:
```python
vested_events = VestEvent.query.join(Grant).filter(
    Grant.user_id == current_user.id,
    VestEvent.is_vested == True  # ❌ This column is not automatically updated
).all()
```

The `is_vested` column is a manual flag that was never being updated, so it remained `False` for all events, even those with past vest dates.

## Solution
Changed the dashboard to:
1. Fetch ALL vest events for the user
2. Use the `has_vested` property to filter events where `vest_date <= today`

**Before:**
```python
vested_events = VestEvent.query.join(Grant).filter(
    Grant.user_id == current_user.id,
    VestEvent.is_vested == True
).all()
```

**After:**
```python
# Get ALL vest events and filter by has_vested property (vest_date in the past)
all_vest_events = VestEvent.query.join(Grant).filter(
    Grant.user_id == current_user.id
).all()

# Filter vested events using the has_vested property
vested_events = [v for v in all_vest_events if v.has_vested]
```

## The `has_vested` Property
Defined in `app/models/vest_event.py`:
```python
@property
def has_vested(self) -> bool:
    """Check if vest date has passed (based on today's date)."""
    return self.vest_date <= date.today()
```

This property automatically returns `True` if the vest date is today or in the past, without requiring any database updates.

## Verified Results
For user "stephen" (id=2) as of 2025-12-21:
- **Total vest events:** 27
- **Vested events (date ≤ today):** 5
- **Upcoming events (date > today):** 22
- **Shares vested (gross):** 1,065.00
- **Shares received (net after taxes):** 737.83
- **Vested inventory value:** $71,606.97 (at $97/share)

### Vested Events Detail:
| Date | Shares Vested | Shares Received (Net) |
|------|---------------|----------------------|
| 2024-06-15 | 390.00 | 340.00 |
| 2024-11-15 | 195.00 | 155.00 |
| 2025-06-15 (Grant 1) | 195.00 | 7.83 |
| 2025-06-15 (Grant 3) | 90.00 | 40.00 |
| 2025-11-15 | 195.00 | 195.00 |
| **Total** | **1,065.00** | **737.83** |

## Impact
- Dashboard now correctly shows vested shares based on actual vest dates
- Values automatically update as time passes and more events vest
- No manual database updates required
- Consistent with the vest event detail pages

## Files Modified
- `/Users/stephencoan/stonks/app/routes/main.py` - Updated dashboard calculation logic

## Testing
1. Navigate to dashboard
2. Verify "Shares Received (Net)" shows 737.83 (or current accurate value)
3. Verify "Vested Inventory Value" shows correct calculation (shares × current price)
4. Wait until a new vest date passes, refresh dashboard
5. Verify values automatically update to include new vested events

## Future Consideration
The `is_vested` column could potentially be removed from the database since the `has_vested` property provides the same information dynamically. However, keeping it allows for potential manual overrides if needed.
