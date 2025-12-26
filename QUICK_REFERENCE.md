# Quick Reference Guide - Tax Profile Integration

## 🚀 How to Use the Tax Configuration System

### For End Users

#### Setting Up Your Tax Profile

1. **Navigate to Settings**
   - From Finance Deep Dive: Click "Configure Tax Settings" button
   - Direct link: http://127.0.0.1:5000/settings/tax

2. **Choose Your Mode**
   
   **Manual Mode (Simple)**
   - Use sliders to set custom rates
   - Federal Tax Rate: 0-37%
   - State Tax Rate: 0-13.3%
   - Long-Term Capital Gains: 0-20%
   - Click "Save Manual Rates"

   **Automatic Mode (Smart)**
   - Select your state (e.g., California)
   - Choose filing status (Single, Married Filing Jointly, etc.)
   - Enter annual income
   - Click "Calculate Rates" to preview
   - Click "Save Automatic Settings"

3. **View Your Rates in Action**
   - Go to Finance Deep Dive
   - Sliders will pre-populate with your rates
   - Tax calculations use your personalized rates
   - Adjust sliders anytime for "what-if" scenarios

---

## 💻 For Developers

### Key Files and Their Roles

#### Backend
```
app/models/tax_rate.py
├── TaxBracket - Stores federal/state tax brackets
└── UserTaxProfile - Stores user tax configuration
    └── get_tax_rates() - Calculates rates based on profile

app/routes/settings.py
├── tax_settings() - Render tax settings page
├── save_tax_settings() - Save user tax profile
└── calculate_tax_preview() - AJAX endpoint for preview

app/routes/grants.py
└── finance_deep_dive() - Loads user tax profile, calculates rates
```

#### Frontend
```
app/templates/settings/tax.html
└── Tax configuration UI with mode toggle

app/templates/grants/finance_deep_dive.html
└── Finance Deep Dive with dynamic tax rate integration
```

### Database Schema

#### tax_brackets
```sql
CREATE TABLE tax_brackets (
    id INTEGER PRIMARY KEY,
    jurisdiction VARCHAR(50) NOT NULL,  -- 'federal', 'CA', 'TX', etc.
    tax_year INTEGER NOT NULL,
    filing_status VARCHAR(20) NOT NULL,
    tax_type VARCHAR(20) NOT NULL,      -- 'ordinary', 'capital_gains_long'
    income_min FLOAT NOT NULL,
    income_max FLOAT,                   -- NULL for top bracket
    rate FLOAT NOT NULL,                -- e.g., 0.22 for 22%
    created_at DATETIME,
    updated_at DATETIME
);
```

#### user_tax_profiles
```sql
CREATE TABLE user_tax_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    state VARCHAR(2),
    filing_status VARCHAR(20) DEFAULT 'single',
    annual_income FLOAT,
    use_manual_rates BOOLEAN DEFAULT 0,
    manual_federal_rate FLOAT,
    manual_state_rate FLOAT,
    manual_ltcg_rate FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### API Endpoints

#### GET /settings/tax
Returns tax settings page

#### POST /settings/tax/save
Saves user tax profile
```json
{
  "mode": "automatic",
  "state": "CA",
  "filing_status": "single",
  "annual_income": 150000
}
```

#### POST /settings/tax/calculate
Preview tax rates (AJAX)
```json
{
  "state": "CA",
  "filing_status": "single",
  "annual_income": 150000
}
```

Returns:
```json
{
  "federal": 24.0,
  "state": 9.3,
  "ltcg": 15.0
}
```

### Code Examples

#### Get User's Tax Rates (Backend)
```python
from app.models.tax_rate import UserTaxProfile

# In a route
tax_profile = UserTaxProfile.query.filter_by(user_id=current_user.id).first()
if tax_profile:
    rates = tax_profile.get_tax_rates()
    # rates = {'federal': 0.24, 'state': 0.093, 'ltcg': 0.15}
else:
    rates = {'federal': 0.24, 'state': 0.093, 'ltcg': 0.15}
```

#### Create/Update Tax Profile
```python
from app.models.tax_rate import UserTaxProfile
from app import db

# Create new profile
profile = UserTaxProfile(
    user_id=current_user.id,
    state='CA',
    filing_status='single',
    annual_income=150000,
    use_manual_rates=False
)
db.session.add(profile)
db.session.commit()

# Update existing profile
profile = UserTaxProfile.query.filter_by(user_id=current_user.id).first()
profile.annual_income = 175000
db.session.commit()
```

#### Add Tax Brackets (for new tax year)
```python
from app.models.tax_rate import TaxBracket
from app import db

# Add a new federal bracket
bracket = TaxBracket(
    jurisdiction='federal',
    tax_year=2026,
    filing_status='single',
    tax_type='ordinary',
    income_min=100000,
    income_max=200000,
    rate=0.24
)
db.session.add(bracket)
db.session.commit()
```

---

## 🔧 Troubleshooting

### User sees default rates instead of profile rates
- Check if user has created a tax profile
- Verify `UserTaxProfile` exists in database for user
- Check `use_manual_rates` flag in profile

### Tax rates not updating in Finance Deep Dive
- User needs to refresh page after saving settings
- Check browser console for JavaScript errors
- Verify tax_rates are being passed to template

### Calculate button doesn't work in settings
- Check browser console for AJAX errors
- Verify `/settings/tax/calculate` endpoint is registered
- Check that tax brackets exist in database for selected state

### Database migration needed
```bash
# If tables don't exist
cd /Users/stephencoan/stonks
source .venv/bin/activate
python -c "from app import db; db.create_all()"
python app/utils/populate_tax_brackets.py
```

---

## 📊 Data Flow Diagram

```
User Profile Setup
    ↓
UserTaxProfile (database)
    ↓
get_tax_rates() method
    ↓
Query TaxBracket table
    ↓
Calculate rates based on income
    ↓
Return {'federal': X, 'state': Y, 'ltcg': Z}
    ↓
Finance Deep Dive route
    ↓
Pass rates to template
    ↓
Pre-populate sliders
    ↓
Display tax projections
```

---

## 🎯 Quick Commands

### Start the app
```bash
cd /Users/stephencoan/stonks
source .venv/bin/activate
python main.py
```

### Populate tax brackets
```bash
python app/utils/populate_tax_brackets.py
```

### Check if tax tables exist
```bash
sqlite3 instance/stonks.db "SELECT COUNT(*) FROM tax_brackets;"
sqlite3 instance/stonks.db "SELECT COUNT(*) FROM user_tax_profiles;"
```

### View tax brackets for a state
```bash
sqlite3 instance/stonks.db "SELECT * FROM tax_brackets WHERE jurisdiction='CA' AND tax_year=2025;"
```

---

## 🎨 UI Components

### Button Styles
```html
<a href="{{ url_for('settings.tax_settings') }}" class="btn btn-secondary">
    Configure Tax Settings
</a>
```

### Tax Slider
```html
<div class="tax-slider-item">
    <label for="federalTaxRate">
        Federal Tax Rate: <strong><span id="federalTaxValue">24.0</span>%</strong>
    </label>
    <input type="range" id="federalTaxRate" min="0" max="37" step="1" 
           value="{{ tax_rates.federal * 100 }}" class="tax-slider">
</div>
```

### Mode Toggle
```html
<div class="toggle-container">
    <label class="toggle-switch">
        <input type="checkbox" id="taxModeToggle">
        <span class="toggle-slider"></span>
    </label>
    <label for="taxModeToggle">Use Automatic Calculation</label>
</div>
```

---

## 📝 Testing Checklist

### Functional Tests
- [ ] Create new user
- [ ] Set manual tax rates
- [ ] Save and verify rates appear in Finance Deep Dive
- [ ] Switch to automatic mode
- [ ] Enter state and income
- [ ] Calculate and save rates
- [ ] Verify calculated rates appear in Finance Deep Dive
- [ ] Adjust sliders in Finance Deep Dive
- [ ] Verify tax projections update

### Edge Cases
- [ ] User with no profile (should see defaults)
- [ ] User with incomplete profile
- [ ] Invalid income values
- [ ] State with no tax (e.g., TX, FL)
- [ ] Top tax bracket (income > max)
- [ ] Multiple users with different profiles

---

## 🔐 Security Notes

- Tax profiles are user-specific (filtered by user_id)
- Login required for all settings routes
- CSRF protection on POST requests
- Input validation on income values
- No sensitive data in tax brackets table

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready
