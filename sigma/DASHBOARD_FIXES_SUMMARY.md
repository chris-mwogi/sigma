# Asset Management Dashboard - Database Field Name Fixes

**Date**: 2025-11-20  
**Status**: ✅ COMPLETED  
**Issue**: Database column errors preventing Asset Management workspace from loading

---

## Problem Summary

The Asset Management workspace was failing to load with the following error:
```
MySQLdb.OperationalError: (1054, "Unknown column 'work_order_status' in 'GROUP BY'")
MySQLdb.OperationalError: (1054, "Unknown column 'risk_classification' in 'GROUP BY'")
```

### Root Cause

Dashboard charts and number cards were referencing field names that don't exist in the DocTypes:
- **Asset Work Order** DocType uses `workflow_state`, NOT `work_order_status`
- **Asset Risk Register** DocType uses `inherent_risk_level`, NOT `risk_classification`

---

## Fixes Applied

### 1. Dashboard Chart: "Work Order Status" ✅

**File**: `apps/sigma/sigma/sigma_asset_integrations/dashboard_chart/work_order_status/work_order_status.json`

**Change**:
```json
{
  "group_by_based_on": "workflow_state"  // Changed from "work_order_status"
}
```

**Database Update**:
```python
chart = frappe.get_doc("Dashboard Chart", "Work Order Status")
chart.group_by_based_on = "workflow_state"
chart.save()
```

---

### 2. Dashboard Chart: "Risk Classification" ✅

**File**: `apps/sigma/sigma/sigma_asset_integrations/dashboard_chart/risk_classification/risk_classification.json`

**Change**:
```json
{
  "group_by_based_on": "inherent_risk_level"  // Changed from "risk_classification"
}
```

**Database Update**:
```python
chart = frappe.get_doc("Dashboard Chart", "Risk Classification")
chart.group_by_based_on = "inherent_risk_level"
chart.save()
```

---

### 3. Number Card: "Open Work Orders" ✅

**File**: `apps/sigma/sigma/sigma_asset_integrations/number_card/open_work_orders/open_work_orders.json`

**Change**:
```json
{
  "filters_json": "[[\"Asset Work Order\",\"workflow_state\",\"in\",[\"In Progress\",\"On Hold\",\"Assigned\"]],[\"Asset Work Order\",\"docstatus\",\"!=\",2]]"
  // Changed from: "work_order_status" with ["Open", "In Progress", "On Hold"]
}
```

**Database Update**:
```python
card = frappe.get_doc("Number Card", "Open Work Orders")
card.filters_json = json.dumps([
    ["Asset Work Order", "workflow_state", "in", ["In Progress", "On Hold", "Assigned"]],
    ["Asset Work Order", "docstatus", "!=", 2]
])
card.save()
```

---

### 4. Workspace Shortcuts ✅

**File**: `apps/sigma/sigma/sigma_asset_integrations/workspace/asset_management/asset_management.json`

**Changes**:

#### Asset Work Order Shortcut:
```json
{
  "stats_filter": "{\"workflow_state\": [\"in\", [\"In Progress\", \"Assigned\", \"On Hold\"]]}"
  // Changed from: "work_order_status"
}
```

#### Asset Risk Register Shortcut:
```json
{
  "stats_filter": "{\"inherent_risk_level\": [\"in\", [\"High (13-20)\", \"Very High (21-25)\"]]}"
  // Changed from: "risk_classification": "High"
}
```

**Database Update**:
```sql
UPDATE `tabWorkspace Shortcut`
SET stats_filter = '{"workflow_state": ["in", ["In Progress", "Assigned", "On Hold"]]}'
WHERE parent = 'Asset Management' AND link_to = 'Asset Work Order';

UPDATE `tabWorkspace Shortcut`
SET stats_filter = '{"inherent_risk_level": ["in", ["High (13-20)", "Very High (21-25)"]]}'
WHERE parent = 'Asset Management' AND link_to = 'Asset Risk Register';
```

---

## Field Name Reference

| DocType | ❌ Incorrect Field | ✅ Correct Field | Valid Values |
|---------|-------------------|------------------|--------------|
| **Asset Work Order** | `work_order_status` | `workflow_state` | Draft, Scheduled, Assigned, In Progress, On Hold, Completed, Cancelled, Closed |
| **Asset Risk Register** | `risk_classification` | `inherent_risk_level` | Low (1-5), Medium (6-12), High (13-20), Very High (21-25) |

---

## Verification Steps

All fixes have been verified in the database:

```python
✓ Dashboard Chart "Work Order Status": group_by_based_on = "workflow_state"
✓ Dashboard Chart "Risk Classification": group_by_based_on = "inherent_risk_level"
✓ Number Card "Open Work Orders": filters use "workflow_state"
✓ Workspace Shortcut "Asset Work Order": stats_filter uses "workflow_state"
✓ Workspace Shortcut "Asset Risk Register": stats_filter uses "inherent_risk_level"
```

---

## Commands Executed

1. **Fixed dashboard components in database**:
   ```bash
   bench --site prismod.localhost console
   ```

2. **Cleared cache**:
   ```bash
   bench --site prismod.localhost clear-cache
   ```

3. **Reloaded workspace**:
   ```bash
   bench --site prismod.localhost reload-doc sigma_asset_integrations Workspace asset_management
   ```

---

## Testing

**URL**: http://172.24.13.88:8000/app/asset-management

**Expected Results**:
- ✅ Workspace loads without database errors
- ✅ All 4 dashboard charts render correctly
- ✅ All 5 number cards display correct counts
- ✅ All workspace shortcuts show correct counts

---

## Notes

### Duplicate Workspaces

Two Asset Management workspaces were found:
1. **`sigma_asset_integrations/workspace/asset_management`** (NEW - with dashboard charts) ✅ ACTIVE
2. **`sigma_assets_inventory/workspace/asset_management`** (OLD - basic workspace) ⚠️ LEGACY

The system is now using the correct workspace from `sigma_asset_integrations` module.

---

**Status**: All fixes applied and verified. Workspace is ready for testing.

