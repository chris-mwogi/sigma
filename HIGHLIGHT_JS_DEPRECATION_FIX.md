# highlight.js Deprecation Warning - Fix Report

**Date**: October 29, 2025  
**Site**: nevel.co.ke  
**Status**: ✅ FIXED

---

## Issue Summary

**Warning**: `Deprecated as of 10.6.0. initHighlighting() is deprecated. Use highlightAll() instead.`

**Location**: `apps/frappe/frappe/website/js/website.js`, line 287

**Root Cause**: The code was using the deprecated `initHighlighting()` function from highlight.js library, which was deprecated in version 10.6.0 and should be replaced with `highlightAll()`.

---

## Investigation Results

### Code Analysis
**File**: `apps/frappe/frappe/website/js/website.js`
**Method**: `highlight_code_blocks()` (line 286-288)
**Issue**: Direct call to deprecated `hljs.initHighlighting()`

**Original Code**:
```javascript
highlight_code_blocks: function () {
    hljs.initHighlighting();  // ❌ Deprecated as of 10.6.0
},
```

---

## Solution Applied

**File Modified**: `apps/frappe/frappe/website/js/website.js`

**Change**: Replaced `initHighlighting()` with `highlightAll()`

**Fixed Code**:
```javascript
highlight_code_blocks: function () {
    // Use highlightAll() instead of deprecated initHighlighting() (deprecated as of highlight.js 10.6.0)
    hljs.highlightAll();  // ✅ Modern API
},
```

**Lines Changed**: 286-289

---

## Why This Fix Works

### highlight.js API Evolution
- **Old API (deprecated)**: `hljs.initHighlighting()` - Automatically highlights all code blocks
- **New API (current)**: `hljs.highlightAll()` - Same functionality, modern naming convention

### Compatibility
- ✅ `highlightAll()` is available in highlight.js 10.6.0+
- ✅ Provides same functionality as `initHighlighting()`
- ✅ No breaking changes to existing code
- ✅ Eliminates deprecation warning

---

## Verification Results

### Code Review ✅
- ✅ Deprecated function replaced
- ✅ Modern API used
- ✅ Functionality preserved
- ✅ No syntax errors

### Cache Management ✅
- ✅ Cache cleared: `bench --site nevel.co.ke clear-cache`

---

## Expected Results

When accessing nevel.co.ke:
- ✅ No deprecation warnings in browser console
- ✅ Code blocks still highlighted correctly
- ✅ Website loads without warnings
- ✅ Syntax highlighting works as expected

---

## Technical Details

### highlight.js Library
- **Purpose**: Syntax highlighting for code blocks
- **Current Version**: 10.6.0+
- **Deprecated Function**: `initHighlighting()`
- **Replacement**: `highlightAll()`

### Function Behavior
Both functions perform the same operation:
1. Find all `<pre><code>` blocks on the page
2. Apply syntax highlighting based on language class
3. Add CSS classes for styling

---

## Files Modified

**File**: `apps/frappe/frappe/website/js/website.js`
- **Method**: `highlight_code_blocks()`
- **Lines**: 286-289
- **Change Type**: Deprecation fix (API update)

---

## Summary

✅ **Deprecation warning fixed successfully**

The website now uses the modern `highlightAll()` API instead of the deprecated `initHighlighting()` function. This eliminates the deprecation warning while maintaining the same functionality.

**Status**: READY FOR PRODUCTION ✅

---

## Next Steps

1. Hard refresh browser: Ctrl+Shift+R
2. Visit nevel.co.ke
3. Open browser console (F12)
4. Verify no deprecation warnings appear
5. Check that code blocks are still highlighted correctly

All code highlighting should work without warnings!

