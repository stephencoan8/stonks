# Vesting Timeline Chart Feature

## Overview
Added an interactive vesting timeline chart to the dashboard that visualizes both vested (past) and unvested (future) shares over time with a toggle to switch between value ($) and share count views.

## Features

### 1. Interactive Timeline Chart
**Location:** Dashboard, between stats grid and content sections

**Visual Elements:**
- **Solid Green Line** - Vested shares/value (dates that have passed)
- **Dashed Gray Line** - Unvested/projected shares/value (future dates)
- **Shaded Fill** - Area under the curve for easy visualization
- **Smooth Curves** - Tension applied for professional look

### 2. Toggle Button
**Two View Modes:**

**Value View (Default)**
- Y-axis: Dollar amount
- Shows cumulative vested value in $
- Shows projected total value in $
- Useful for seeing equity growth in monetary terms

**Shares View**
- Y-axis: Share count
- Shows cumulative vested shares (net after taxes)
- Shows projected total shares
- Useful for tracking share accumulation

### 3. Interactive Features
- **Hover tooltips** - Shows exact date, value/shares at that point
- **Responsive** - Adjusts to screen size
- **Dark theme** - Matches app design
- **Smooth transitions** - Animated view switching
- **Time-based X-axis** - Automatically formats dates by month/year

### 4. Visual Design
**Chart Styling:**
- Green solid line for vested (matches success color)
- Gray dashed line for unvested (indicates projection)
- Semi-transparent fills
- Dark background matching app theme
- Grid lines for easier reading

**Toggle Buttons:**
- Pill-shaped button group
- Active state in accent color (cyan)
- Hover effects
- Clear labels: "Value ($)" and "Shares"

## User Experience

### Scenario 1: Viewing Vested Progress
1. User lands on dashboard
2. Sees vesting timeline chart showing green solid line up to today
3. Gray dashed line continues into the future
4. Can immediately see how much has vested vs. what's coming
5. Hover over any point to see exact values

### Scenario 2: Switching to Shares View
1. User clicks "Shares" toggle button
2. Chart smoothly updates
3. Y-axis changes from $ to share count
4. Tooltips now show "X.XX shares" instead of "$X.XX"
5. Same timeline, different perspective

### Scenario 3: Planning Future Vests
1. User looks at the gray dashed portion
2. Sees projection of total shares by end of vesting period
3. Can estimate future wealth
4. Compare vested vs. unvested amounts visually

## Technical Implementation

### Backend (main.py)
```python
# Prepare vesting timeline data for chart
vesting_timeline = []
cumulative_vested = 0
cumulative_total = 0

for vest in all_vest_events:
    cumulative_total += vest.shares_received  # Use net shares received
    if vest.has_vested:
        cumulative_vested += vest.shares_received
    
    vesting_timeline.append({
        'date': vest.vest_date.strftime('%Y-%m-%d'),
        'vested': cumulative_vested,
        'total': cumulative_total,
        'is_vested': vest.has_vested,
        'shares': vest.shares_received
    })
```

### Frontend (dashboard.html)
**Chart Library:** Chart.js 4.4.0

**Data Processing:**
- Splits data at transition point (vested → unvested)
- Creates two datasets: solid line and dashed line
- Multiplies by current price for value view

**Chart Configuration:**
- Type: Line chart with fills
- X-axis: Time-based (automatic date formatting)
- Y-axis: Dynamic ($ or shares based on toggle)
- Tooltips: Custom formatting for both views
- Responsive: maintainAspectRatio: false
- Height: 400px

**Toggle Logic:**
```javascript
document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Update active state
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Switch view and redraw
        currentView = this.dataset.view;
        createChart(currentView);
    });
});
```

## Data Calculations

### Cumulative Vested
- Starts at 0
- Adds vest.shares_received for each past event
- Only counts events where vest.has_vested == True
- Shows actual net shares (after tax withholding)

### Cumulative Total
- Starts at 0
- Adds vest.shares_received for ALL events (past and future)
- Projects total shares by end of vesting schedule
- Includes tax withholding calculations

### Value Calculation
- Cumulative shares × Current stock price
- Uses latest stock price from database
- Same price for both vested and projected
- Updates when stock price changes

## Styling Details

### Chart Section
- Background: Card background color
- Border radius: 12px
- Padding: 2rem
- Box shadow for depth
- Margin bottom: 2rem

### Toggle Buttons
- Background: Secondary background
- Padding: 0.25rem container
- Border radius: 8px
- Individual buttons: 0.5rem × 1rem padding
- Active state: Accent color background
- Smooth transitions: 0.2s

### Legend
- Centered below chart
- Border top separator
- Flex layout with gap
- Visual line samples (solid/dashed)
- Clear labels

## Benefits
✅ **Visual Progress Tracking** - See vesting progress at a glance
✅ **Future Planning** - Visualize total unvested equity
✅ **Dual Perspectives** - Switch between $ and shares
✅ **Professional UI** - Modern chart with smooth animations
✅ **Interactive** - Hover for exact values
✅ **Date-Aware** - Automatically splits at today's date
✅ **Tax-Aware** - Uses net shares received (after withholding)

## Files Modified
1. `/Users/stephencoan/stonks/app/routes/main.py`
   - Added vesting_timeline data calculation
   - Cumulative vested and total tracking
   - Pass timeline data to template

2. `/Users/stephencoan/stonks/app/templates/main/dashboard.html`
   - Added chart section HTML
   - Chart.js CDN script
   - Toggle button UI
   - Chart configuration JavaScript
   - Complete styling

## Future Enhancements (Possible)
- [ ] Add stock price history line overlay
- [ ] Show individual vest events as markers
- [ ] Add zoom/pan controls
- [ ] Export chart as image
- [ ] Add moving average line
- [ ] Show grants as colored segments
- [ ] Add comparison with colleagues (anonymized)

## Status
🟢 Feature complete and tested
🟢 Responsive design
🟢 Dark theme compatible
🟢 Ready for production
