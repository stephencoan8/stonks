# Grant Edit Form Fix

## Problem
When editing grants (especially non-Kickass grants), users encountered a browser error:
```
An invalid form control with name='vest_years' is not focusable
```

This error occurs when a required form field is hidden. The browser tries to validate the form but can't focus on the hidden required field to show the validation message.

## Root Cause
The `vest_years` input field in `app/templates/grants/edit.html` was:
1. Hidden via CSS (`display: none`) for non-Kickass grants
2. Still marked as required in the HTML
3. When the form was submitted, the browser tried to validate this hidden required field and failed

## Solution
Updated the JavaScript in `edit.html` to dynamically manage the `required` and `disabled` attributes:

### Changes Made

1. **vest_years field**: When grant type is NOT kickass:
   - Remove `required` attribute
   - Add `disabled` attribute
   - Field remains hidden

2. **bonus_type field**: When grant type is NOT annual_performance:
   - Add `disabled` attribute
   - Field remains hidden

3. **share_type field**: When grant type is ESPP/nqESPP:
   - Add `disabled` attribute
   - Field remains hidden

4. **Backend handling** (`app/routes/grants.py`):
   - Updated to handle disabled fields gracefully
   - If `share_type` is not submitted (because disabled), keep the existing value
   - Properly handle `None` values for `bonus_type` and `vest_years`

## Files Changed
- `app/templates/grants/edit.html` - Updated JavaScript to manage field attributes
- `app/routes/grants.py` - Handle disabled fields in form submission

## Testing
To verify the fix works:
1. Edit a non-Kickass grant (e.g., New Hire RSU or ISO 6Y)
2. Change share quantity
3. Submit the form
4. Verify no browser validation errors
5. Confirm grant updates successfully and vest schedule recalculates

## Technical Details

### Why disabled instead of just removing required?
Disabled fields have several benefits:
- They are NOT submitted with the form (browser skips them)
- They are NOT validated (browser ignores them)
- Users can't interact with them (visual indication they don't apply)

### Why keep existing value for share_type?
When a field is disabled, the browser doesn't submit it with the form. For fields like `share_type` that should never change for certain grant types (e.g., ESPP), we keep the existing value in the database if the field isn't submitted.

## Related Issues
This fix ensures all grant types can be edited smoothly:
- ✅ ISO 5Y and 6Y grants
- ✅ RSU grants (New Hire, Promotion, Annual Bonus)
- ✅ Cash grants (Annual Bonus)
- ✅ Kickass grants (1-5 year vesting)
- ✅ ESPP and nqESPP grants

## Commit
Commit: `5d1b8a7`
Message: "Fix grant edit form: remove required attribute from hidden vest_years field"
