# Test Plan - Vest Event Save Functionality

## Bug Fixed
The vest event save button was reverting input values after a few seconds due to spurious `change` events on the payment method dropdown clearing the opposite field.

## Root Cause
The payment method change handler was clearing values unconditionally:
```javascript
// OLD CODE - BUGGY
if (this.value === 'cash_to_cover') {
    sharesInput.value = '';  // Always cleared, even if already 'cash_to_cover'
} else {
    cashInput.value = '';    // Always cleared, even if already 'sell_to_cover'
}
```

## Fix Applied
1. Track previous payment method value
2. Only clear opposite field when method **actually changes**
3. Enhance save handler to restore proper field states
4. Return all saved values from server for verification

## Test Scenarios

### Test 1: Basic Save - Sell to Cover
1. Navigate to grant detail page (http://127.0.0.1:5001/grants/1)
2. Ensure payment method is "Sell to Cover"
3. Enter a value in "Shares Withheld" (e.g., 25.5)
4. Click "Save"
5. **VERIFY:** Button shows "Saving..." then "✓ Saved"
6. **VERIFY:** After 2 seconds, button shows "Save" again
7. **VERIFY:** Input value remains "25.50" (does NOT revert to empty)
8. **VERIFY:** "Shares Received" and "Net Value" update correctly
9. Refresh page
10. **VERIFY:** Value persists after page reload

### Test 2: Basic Save - Cash to Cover
1. Change payment method to "Cash to Cover"
2. **VERIFY:** "Shares Withheld" field is disabled and cleared
3. **VERIFY:** "Cash to Cover" field is enabled
4. Enter a value in "Cash to Cover" (e.g., 2500.00)
5. Click "Save"
6. **VERIFY:** Button shows "Saving..." then "✓ Saved"
7. **VERIFY:** After 2 seconds, input value remains "2500.00"
8. **VERIFY:** No reversion occurs
9. Refresh page
10. **VERIFY:** Value persists

### Test 3: Switch Payment Methods
1. Start with "Sell to Cover" selected
2. Enter "30.0" in "Shares Withheld"
3. Click "Save"
4. **VERIFY:** Saves successfully
5. Change payment method to "Cash to Cover"
6. **VERIFY:** "Shares Withheld" is cleared (correct behavior)
7. **VERIFY:** "Cash to Cover" is enabled
8. Enter "3000.00" in "Cash to Cover"
9. Click "Save"
10. **VERIFY:** Saves successfully without reverting
11. Switch back to "Sell to Cover"
12. **VERIFY:** "Cash to Cover" is cleared
13. Enter new value in "Shares Withheld"
14. Click "Save"
15. **VERIFY:** No reversion

### Test 4: Multiple Vest Events
1. On grant detail page, find multiple vest event rows
2. Edit values in 2-3 different rows
3. Save each one
4. **VERIFY:** Each row maintains its saved values
5. **VERIFY:** No cross-contamination between rows
6. **VERIFY:** After all saves, all values persist

### Test 5: Edge Cases
**Empty Values:**
1. Select "Sell to Cover"
2. Leave "Shares Withheld" empty (or clear it)
3. Click "Save"
4. **VERIFY:** Saves successfully with 0
5. **VERIFY:** Field shows empty (not "0.00")

**Zero Values:**
1. Enter "0" in "Shares Withheld"
2. Click "Save"
3. **VERIFY:** Field shows empty after save

**Large Values:**
1. Enter "999999.99" in "Cash to Cover"
2. Click "Save"
3. **VERIFY:** Saves and displays correctly

**Decimal Precision:**
1. Enter "123.456789" in "Shares Withheld"
2. Click "Save"
3. **VERIFY:** Rounds to "123.46" (2 decimal places)

### Test 6: Error Handling
**Network Error:**
1. Open browser console
2. Simulate network error (disconnect network or block request)
3. Try to save
4. **VERIFY:** Error alert appears
5. **VERIFY:** Button reverts to "Save"
6. **VERIFY:** Values remain in inputs

**Invalid Data:**
1. Try entering negative numbers
2. **VERIFY:** HTML5 validation prevents (min="0")

### Test 7: Browser Console Verification
1. Open browser developer tools
2. Go to Console tab
3. Perform a save
4. **VERIFY:** Console shows:
   - "Saving vest event: [id]"
   - "Payment method: [method]"
   - "Cash to cover: [value]" or "Shares sold: [value]"
   - "Server response: {success: true, ...}"
   - "Save successful, updating UI with server data"
   - "Successfully saved and updated UI"
5. **VERIFY:** No JavaScript errors
6. **VERIFY:** No failed network requests

### Test 8: Database Persistence
From terminal:
```bash
cd /Users/stephencoan/stonks
.venv/bin/python -c "
from app import create_app, db
from app.models.vest_event import VestEvent

app = create_app()
with app.app_context():
    vest = VestEvent.query.get(1)
    print(f'Payment Method: {vest.payment_method}')
    print(f'Cash: {vest.cash_to_cover}')
    print(f'Shares Sold: {vest.shares_sold_to_cover}')
"
```

**VERIFY:** Database shows correct saved values

## Success Criteria
✅ Values persist in UI after save (no reversion after 2 seconds)
✅ Values persist in database
✅ Values persist after page refresh
✅ Payment method switching clears opposite field only when method changes
✅ No spurious clearing of saved values
✅ Console shows no errors
✅ All calculated fields update correctly

## Known Good State
- Database saves correctly ✅
- Server returns correct values ✅
- Template renders correctly ✅
- JavaScript properly updates UI ✅
- Payment method change handler doesn't interfere with saved values ✅

## Files Modified
- `/Users/stephencoan/stonks/app/templates/grants/view.html` - Fixed payment method change handler and save handler
- `/Users/stephencoan/stonks/app/routes/grants.py` - Added debug logging and comprehensive error handling
- `/Users/stephencoan/stonks/FIXES.md` - Documented root cause and solution

## Technical Notes

### Payment Method Change Handler
Now tracks previous value and only clears when method actually changes:
```javascript
let previousValue = select.value;
select.addEventListener('change', function() {
    if (this.value === previousValue) return; // No-op if same
    // ... rest of logic
    previousValue = this.value; // Update tracker
});
```

### Save Success Handler
Properly restores field states:
```javascript
if (data.payment_method === 'cash_to_cover') {
    if (savedCash > 0) cashInput.value = savedCash.toFixed(2);
    sharesInput.value = '';
    sharesInput.disabled = true;
    cashInput.disabled = false;
} else {
    if (savedShares > 0) sharesInput.value = savedShares.toFixed(2);
    cashInput.value = '';
    cashInput.disabled = true;
    sharesInput.disabled = false;
}
paymentMethodSelect.value = data.payment_method; // Sync dropdown
```

## Status
🟢 All fixes applied and tested
🟢 Ready for user testing
