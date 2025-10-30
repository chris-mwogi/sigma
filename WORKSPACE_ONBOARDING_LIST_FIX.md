# Workspace onboarding_list AttributeError - Fix Report

**Date**: October 29, 2025  
**Site**: prismod.co.ke  
**App**: Sigma (v0.0.1)  
**Status**: ✅ FIXED

---

## Issue Summary

**Error**: `AttributeError: 'Workspace' object has no attribute 'onboarding_list'`

**Location**: `apps/frappe/frappe/desk/desktop.py`, line 320, in `get_onboardings()`

**Affected Workspaces**:
- Stock
- Buying
- Selling

**Root Cause**: The Workspace doctype does not have an `onboarding_list` field, but the `get_onboardings()` method was trying to access it without checking if it exists first.

---

## Investigation Results

### Workspace DocType Analysis
- ✅ Workspace doctype has 30 fields
- ❌ `onboarding_list` field does NOT exist
- ✅ Other fields present: content, charts, shortcuts, links, quick_lists, custom_blocks, roles

### Code Analysis
**File**: `apps/frappe/frappe/desk/desktop.py`
**Method**: `get_onboardings()` (line 318-333)
**Problem**: Direct access to `self.onboarding_list` without checking if attribute exists

**Original Code**:
```python
@handle_not_exist
def get_onboardings(self):
    if self.onboarding_list:  # ❌ AttributeError here
        for onboarding in self.onboarding_list:
            # ... process onboardings
    return self.onboardings
```

---

## Solution Applied

**File Modified**: `apps/frappe/frappe/desk/desktop.py`

**Change**: Added `hasattr()` check before accessing `onboarding_list`

**Fixed Code**:
```python
@handle_not_exist
def get_onboardings(self):
    # Check if onboarding_list attribute exists before accessing it
    if hasattr(self, 'onboarding_list') and self.onboarding_list:
        for onboarding in self.onboarding_list:
            # ... process onboardings
    return self.onboardings
```

**Lines Changed**: 318-334

---

## Verification Results

### API Testing ✅
- ✅ Stock workspace page loads successfully
- ✅ Buying workspace page loads successfully
- ✅ Selling workspace page loads successfully
- ✅ No AttributeError thrown
- ✅ Onboardings data included in response

### Test Results
```
✅ Testing Stock workspace via get_desktop_page API...
   ✅ Stock workspace page loaded successfully!
   - Has onboardings: True

✅ Testing Buying workspace via get_desktop_page API...
   ✅ Buying workspace page loaded successfully!
   - Has onboardings: True

✅ Testing Selling workspace via get_desktop_page API...
   ✅ Selling workspace page loaded successfully!
   - Has onboardings: True
```

---

## Expected Results

When accessing workspace pages:
- ✅ No AttributeError
- ✅ Workspace pages load successfully
- ✅ Sidebar renders correctly
- ✅ Navigation works smoothly
- ✅ All workspace items accessible

---

## Technical Details

### Root Cause Analysis
The Workspace doctype in Frappe v16.0.0-dev does not include an `onboarding_list` field. The `get_onboardings()` method in the desktop.Workspace class was attempting to access this non-existent attribute without proper validation.

### Why This Happened
When workspaces are created or updated, they may not have all optional fields initialized. The code should gracefully handle missing attributes rather than throwing an error.

### Fix Approach
Added defensive programming by checking if the attribute exists before accessing it using `hasattr()`. This is a common pattern in Python for handling optional attributes.

---

## Files Modified

**File**: `apps/frappe/frappe/desk/desktop.py`
- **Method**: `get_onboardings()`
- **Lines**: 318-334
- **Change Type**: Bug fix (added attribute existence check)

---

## Cache Management

- ✅ Cache cleared: `bench --site prismod.co.ke clear-cache`

---

## Affected Workspaces

All three child workspaces under "Assets & Inventory" are now working:
1. ✅ Stock (icon: package)
2. ✅ Buying/Acquisition (icon: shopping-cart)
3. ✅ Selling/Disposal (icon: trending-up)

---

## Summary

✅ **AttributeError fixed successfully**

The workspace pages now load without errors. The fix is minimal, defensive, and follows Python best practices for handling optional attributes.

**Status**: READY FOR PRODUCTION ✅

---

## Next Steps

1. Hard refresh browser: Ctrl+Shift+R
2. Navigate to Stock workspace
3. Verify page loads without errors
4. Check browser console for any errors
5. Test navigation to Buying and Selling workspaces

All workspaces should now be fully functional!

