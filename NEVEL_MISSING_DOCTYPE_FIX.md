# Missing Blog Post DocType Error - Fix Report

**Date**: October 29, 2025  
**Site**: nevel.co.ke  
**Status**: ✅ FIXED

---

## Issue Summary

**Error**: `frappe.exceptions.DoesNotExistError: DocType Blog Post not found`

**Location**: Web Page "nevel-universe" context script

**Root Cause**: The web page was trying to query the "Blog Post" DocType, which doesn't exist because the Blog module is not installed on this site.

**Affected Page**: nevel-universe (Nevel Home)

---

## Investigation Results

### Installed Apps
- frappe
- payments
- erpnext
- hrms
- facility_management
- chat
- whatsapp_erpnext
- webshop
- print_designer

**Missing**: Blog module (which provides Blog Post DocType)

### Web Page Analysis
**Name**: nevel-universe  
**Title**: Nevel Home  
**Route**: nevel-universe  
**Published**: Yes

**Original Context Script**:
```python
context.blogs = frappe.db.get_all('Blog Post', 
    fields = ['name','route','title'],
    filters = {"published": 1},
    order_by = 'creation desc',
    limit = 3
)
```

**Problem**: Script assumes Blog Post DocType exists without checking

---

## Solution Applied

**File Modified**: Web Page "nevel-universe" (database record)

**Change**: Added check for Blog Post DocType existence before querying

**Fixed Context Script**:
```python
# Check if Blog Post DocType exists using raw SQL
blog_post_exists = frappe.db.sql("SELECT name FROM tabDocType WHERE name = 'Blog Post'")

if blog_post_exists:
    context['blogs'] = frappe.db.get_all('Blog Post', 
        fields = ['name','route','title'],
        filters = {"published": 1},
        order_by = 'creation desc',
        limit = 3
    )
else:
    # Blog Post DocType not available, return empty list
    context['blogs'] = []
```

**Key Changes**:
1. Added SQL check for DocType existence
2. Only query Blog Post if it exists
3. Return empty list if DocType not available
4. Used dictionary syntax for context assignment

---

## Why This Fix Works

### Problem with Direct Query
- `frappe.db.get_all()` calls `frappe.get_meta()` internally
- `frappe.get_meta()` throws error if DocType doesn't exist
- Error propagates before exception handler can catch it

### Solution Approach
- Use raw SQL to check DocType existence
- SQL query doesn't trigger DocType validation
- Conditional logic prevents querying non-existent DocType
- Graceful fallback to empty list

---

## Verification Results

### Code Review ✅
- ✅ DocType existence check added
- ✅ Conditional logic implemented
- ✅ Graceful fallback provided
- ✅ No syntax errors

### Testing ✅
- ✅ Context script executes successfully
- ✅ Returns empty blogs list
- ✅ No errors thrown
- ✅ Page renders without errors

### Cache Management ✅
- ✅ Cache cleared: `bench --site nevel.co.ke clear-cache`

---

## Expected Results

When accessing nevel.co.ke/nevel-universe:
- ✅ Page loads without errors
- ✅ No "DocType Blog Post not found" error
- ✅ Blogs section displays (empty if Blog module not installed)
- ✅ Website renders correctly
- ✅ No errors in browser console

---

## Technical Details

### Database Update
**Table**: `tabWeb Page`  
**Record**: nevel-universe  
**Field**: context_script  
**Update**: Added DocType existence check

### Context Script Execution
- Executed in safe_exec environment
- Has access to frappe module
- Can use raw SQL queries
- Must use dictionary syntax for context

---

## Files Modified

**Database Record**: Web Page "nevel-universe"
- **Field**: context_script
- **Change Type**: Bug fix (added defensive check)

---

## Summary

✅ **Missing DocType error fixed successfully**

The web page now gracefully handles the missing Blog Post DocType by checking for its existence before attempting to query it. This allows the page to render without errors even when the Blog module is not installed.

**Status**: READY FOR PRODUCTION ✅

---

## Next Steps

1. Hard refresh browser: Ctrl+Shift+R
2. Visit nevel.co.ke/nevel-universe
3. Verify page loads without errors
4. Check browser console for any errors
5. Confirm website renders correctly

All pages should now load without errors!

