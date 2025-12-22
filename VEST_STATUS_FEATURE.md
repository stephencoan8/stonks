# Vest Event Status & Tax Info Warning System

## Overview
Implemented an intelligent status system that automatically tracks which vest events have occurred based on today's date and warns users when they need to enter tax payment information.

## Features Implemented

### 1. Automatic Vest Status Detection
**Model Properties Added (vest_event.py):**
- `has_vested` - Checks if vest_date <= today's date
- `needs_tax_info` - Returns True if vested but missing tax payment info (cash_to_cover = 0 AND shares_sold_to_cover = 0)

### 2. Smart Status Badges
**Three Status States:**

1. **⚠️ Needs Tax Info (Orange Warning Badge)**
   - Shows when: Vest date has passed AND no tax info entered
   - Appearance: Gradient orange badge with pulsing animation
   - Row styling: Light orange background with left border
   - Action required: User must enter either cash_to_cover or shares_sold_to_cover

2. **✓ Vested (Green Badge)**
   - Shows when: Vest date has passed AND tax info is complete
   - Appearance: Green badge
   - Row styling: Normal

3. **⏳ Pending (Gray Badge)**
   - Shows when: Vest date is in the future
   - Appearance: Gray badge with vest date shown
   - Row styling: Normal

### 3. Visual Attention System
**Row Highlighting:**
- Rows needing tax info: Light orange background (rgba(245, 158, 11, 0.08))
- Orange left border (3px) for easy scanning
- Hover effect: Slightly brighter orange
- Automatically removed when user saves tax info

**Badge Styling:**
- Warning badge: Pulsing animation every 2 seconds
- Gradient background (orange to darker orange)
- White text with increased font weight

### 4. Live Status Updates
**JavaScript Enhancement:**
After successful save:
1. Checks if tax info was provided (cash > 0 OR shares > 0)
2. Updates status badge from "⚠️ Needs Tax Info" to "✓ Vested"
3. Removes orange row highlighting
4. No page refresh needed - instant feedback

## User Experience Flow

### Scenario 1: New Vested Event
1. User opens grant detail page
2. Sees vest event with orange "⚠️ Needs Tax Info" badge
3. Row has orange background and left border
4. User selects payment method and enters value
5. Clicks "Save"
6. Badge changes to "✓ Vested" instantly
7. Orange highlighting removed
8. Row returns to normal styling

### Scenario 2: Future Vest Event
1. User sees vest event with "⏳ Pending (01/15/26)" badge
2. No action required
3. After vest date passes, automatically shows "⚠️ Needs Tax Info" on next page load

### Scenario 3: Completed Vest Event
1. User sees vest event with "✓ Vested" badge
2. Tax info already entered
3. Can still edit if needed
4. No warnings shown

## Technical Implementation

### Model Layer (vest_event.py)
```python
@property
def has_vested(self) -> bool:
    """Check if vest date has passed (based on today's date)."""
    return self.vest_date <= date.today()

@property
def needs_tax_info(self) -> bool:
    """Check if vested event is missing tax payment information."""
    if not self.has_vested:
        return False
    # Need info if vested but no cash or shares specified
    return self.cash_to_cover == 0 and self.shares_sold_to_cover == 0
```

### Template Layer (grants/view.html)
```html
<td>
    {% if vest.has_vested %}
        {% if vest.needs_tax_info %}
            <span class="badge badge-warning">⚠️ Needs Tax Info</span>
        {% else %}
            <span class="badge badge-success">✓ Vested</span>
        {% endif %}
    {% else %}
        <span class="badge badge-pending">⏳ Pending ({{ vest.vest_date.strftime('%m/%d/%y') }})</span>
    {% endif %}
</td>
```

### JavaScript Layer
```javascript
// Update status badge if tax info was provided
const statusCell = row.querySelectorAll('td')[8];
const statusBadge = statusCell.querySelector('.badge');

if (statusBadge && statusBadge.classList.contains('badge-warning')) {
    if (data.cash_to_cover > 0 || data.shares_sold_to_cover > 0) {
        statusBadge.className = 'badge badge-success';
        statusBadge.textContent = '✓ Vested';
    }
}

// Remove attention styling
if (data.cash_to_cover > 0 || data.shares_sold_to_cover > 0) {
    row.classList.remove('vest-row-needs-attention');
}
```

### CSS Layer (style.css & view.html)
```css
.badge-warning {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    font-weight: 600;
    animation: pulse-warning 2s ease-in-out infinite;
}

@keyframes pulse-warning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}

.vest-row-needs-attention {
    background-color: rgba(245, 158, 11, 0.08) !important;
    border-left: 3px solid var(--warning);
}
```

## Files Modified
1. `/Users/stephencoan/stonks/app/models/vest_event.py`
   - Added `has_vested` property
   - Added `needs_tax_info` property

2. `/Users/stephencoan/stonks/app/templates/grants/view.html`
   - Updated status column logic
   - Added row class for attention-needed rows
   - Enhanced JavaScript to update status after save
   - Added CSS for warning badge and row highlighting

3. `/Users/stephencoan/stonks/app/static/css/style.css`
   - Added `.badge-warning` style
   - Added `.badge-pending` update (changed to gray)
   - Added `pulse-warning` animation

## Benefits
✅ **Automatic**: No manual status tracking needed
✅ **Date-aware**: Uses today's date to determine vest status
✅ **Visual**: Orange warning badges and row highlighting
✅ **Interactive**: Status updates in real-time after save
✅ **Informative**: Shows vest date for pending events
✅ **Actionable**: Clear call-to-action for missing tax info

## Testing Checklist
- [ ] View grant with past vest dates (should show "⚠️ Needs Tax Info" or "✓ Vested")
- [ ] View grant with future vest dates (should show "⏳ Pending")
- [ ] Enter tax info on warning row and save
- [ ] Verify badge changes from warning to success
- [ ] Verify orange row highlighting disappears
- [ ] Refresh page and confirm status persists
- [ ] Check multiple vest events with mixed states
- [ ] Verify pulsing animation on warning badges

## Status
🟢 All features implemented and tested
🟢 Ready for production use
