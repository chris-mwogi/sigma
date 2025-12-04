# Workspace Display Content Fix Guide

## Issue Summary

Some workspaces in the Sigma app are not displaying their content properly in the Frappe UI. This happens when the `content` field in the Workspace doctype is empty or doesn't properly represent the shortcuts, links, and number cards defined in the workspace.

## Affected Workspaces

Based on analysis, the following workspaces have issues:

### 1. Vehicle Management
- **Status**: Has 9 links defined but content field only shows a welcome message
- **Issue**: Links are not rendered in the workspace UI
- **Fix**: Need to build proper content JSON from the links

### 2. Guard Monitoring (if exists)
- **Status**: May have empty content field
- **Issue**: No shortcuts or links displayed
- **Fix**: Need to populate content from workspace_config.json

## Root Cause

In Frappe, workspaces use a `content` field that stores a JSON array of UI elements. This field must be properly populated with:
- Headers
- Spacers
- Number cards
- Shortcuts
- Cards (for links)

When workspaces are created with shortcuts/links in child tables but the `content` field is not properly built, the UI doesn't display them.

## Solution

The `fix_workspace_content.py` script has been updated to:

1. **For standard workspaces** (with shortcuts):
   - Build content from shortcuts and links child tables
   - Add proper headers and spacers
   - Format shortcuts with 3 columns per row
   - Format links as cards with 4 columns per row

2. **For Vehicle Management** (with links):
   - Build content from number cards and links
   - Handle "Card Break" type links as section headers
   - Format regular links as cards

## How to Run the Fix

### From Frappe Bench Console

```bash
# Navigate to bench directory
cd /workspace/development/frappe-bench

# Run the fix script
bench --site development.localhost execute sigma.fix_workspace_content.main
```

### From Python Console

```python
import frappe
frappe.init(site='development.localhost')
frappe.connect()

from sigma.fix_workspace_content import main
main()

frappe.db.commit()
```

## Expected Results

After running the fix:

1. **Sigma Home**: Should display 4 shortcuts and number cards
2. **Risk Assessment**: Should display shortcuts and number cards
3. **Assets & Inventory**: Should display shortcuts and number cards
4. **Acquisition (Buying)**: Should display shortcuts and number cards
5. **Disposal (Selling)**: Should display shortcuts and number cards
6. **Vehicle Management**: Should display number cards and all navigation links organized by sections

## Verification

To verify the fix worked:

1. Log into Frappe UI
2. Navigate to each workspace from the sidebar
3. Check that:
   - Number cards are displayed at the top
   - Quick Actions section shows shortcuts
   - Navigation section shows links/cards
   - All sections are properly formatted

## Content Field Structure

The content field should be a JSON array with objects like:

```json
[
  {
    "id": "unique-id",
    "type": "header",
    "data": {
      "text": "<span class=\"h4\"><b>Title</b></span>",
      "col": 12
    }
  },
  {
    "id": "unique-id",
    "type": "number_card",
    "data": {
      "number_card_name": "Card Name",
      "col": 3
    }
  },
  {
    "id": "unique-id",
    "type": "shortcut",
    "data": {
      "shortcut_name": "Shortcut Label",
      "col": 3
    }
  },
  {
    "id": "unique-id",
    "type": "card",
    "data": {
      "card_name": "Link Label",
      "col": 4
    }
  }
]
```

## Future Prevention

When creating new workspaces:

1. Always populate the `content` field when adding shortcuts/links
2. Use the `build_workspace_content()` helper function
3. Test the workspace in the UI before committing
4. Consider using workspace fixtures that include the content field

## Related Files

- `sigma/fix_workspace_content.py` - Main fix script
- `sigma/populate_workspaces.py` - Workspace population script
- `sigma/*/workspace/*.json` - Workspace fixture files

