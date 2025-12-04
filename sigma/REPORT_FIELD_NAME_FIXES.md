# Asset Management Reports - Field Name Fixes

## Summary

Fixed database field name errors in four Asset Management reports. These errors were caused by SQL queries referencing field names that don't exist in the actual DocType definitions.

**Date:** 2025-11-20  
**Status:** ✅ **ALL FIXES COMPLETE AND TESTED**

---

## Reports Fixed

### 1. Compliance Status Report ✅

**File:** `apps/sigma/sigma/sigma_asset_integrations/report/compliance_status_report/compliance_status_report.py`

**Error:** `Unknown column 'a.iso_55000_compliance' in 'SELECT'`

**Field Name Corrections:**
| Incorrect Field Name | Correct Field Name | Field Type |
|---------------------|-------------------|------------|
| `iso_55000_compliance` | `iso_55000_compliant` | Check |
| `iso_14224_compliance` | `iso_14224_failure_code` | Data |
| `nist_compliance` | `nist_compliant` | Check |
| `regulatory_compliance` | `regulatory_compliance_status` | Select |
| `certification_status` | *(removed - doesn't exist in Asset)* | - |

**Additional Changes:**
- Added `iec_61850_compliant` field (Check) to replace removed `certification_status`
- Updated column labels to match new field types

**Test Result:** ✅ Report loads successfully with 20 data rows

---

### 2. Asset Criticality Matrix ✅

**File:** `apps/sigma/sigma/sigma_asset_integrations/report/asset_criticality_matrix/asset_criticality_matrix.py`

**Error:** `Unknown column 'a.impact_score' in 'SELECT'`

**Field Name Corrections:**
| Incorrect Field Name | Correct Field Name | Field Type |
|---------------------|-------------------|------------|
| `impact_score` | *(removed - doesn't exist in Asset)* | - |

**Changes:**
- Removed `impact_score` field from both columns definition and SQL query
- The Asset DocType doesn't have a separate impact score field
- Risk is calculated from `failure_probability` and other factors

**Test Result:** ✅ Report loads successfully with 20 data rows

---

### 3. Asset Lifecycle Report ✅

**File:** `apps/sigma/sigma/sigma_asset_integrations/report/asset_lifecycle_report/asset_lifecycle_report.py`

**Error:** `Unknown column 'a.commissioning_date' in 'SELECT'`

**Field Name Corrections:**
| Incorrect Field Name | Correct Field Name | Field Type |
|---------------------|-------------------|------------|
| `commissioning_date` | `purchase_date` | Date |
| `expected_end_of_life` | *(removed - doesn't exist in Asset)* | - |
| `health_score` | `health_status` | Select |

**Changes:**
- Replaced `commissioning_date` with `purchase_date` (actual field in Asset DocType)
- Removed `expected_end_of_life` field (doesn't exist in Asset DocType)
- Changed `health_score` to `health_status` (Select field with options: Healthy, Warning, Critical, Failed, Unknown)
- Updated age and remaining life calculations to use `purchase_date` instead of `commissioning_date`
- Removed JOIN with Asset Category Sigma (not needed after removing expected_end_of_life calculation)

**Test Result:** ✅ Report loads successfully with 20 data rows

---

### 4. Maintenance Due Report ✅

**File:** `apps/sigma/sigma/sigma_asset_integrations/report/maintenance_due_report/maintenance_due_report.py`

**Error:** `Unknown column 'ams.schedule_status' in 'SELECT'`

**Field Name Corrections:**
| Incorrect Field Name | Correct Field Name | Field Type |
|---------------------|-------------------|------------|
| `schedule_status` | `status` | Select |
| `estimated_cost` | *(removed - doesn't exist in Asset Maintenance Schedule)* | - |

**Changes:**
- Changed `schedule_status` to `status` (the actual field name in Asset Maintenance Schedule)
- Removed `estimated_cost` field (doesn't exist in Asset Maintenance Schedule DocType)
- Updated status filter from `('Active', 'Overdue')` to `('Scheduled', 'Due', 'Overdue')` to match actual status options
- Added `is_active = 1` filter to only show active schedules

**Test Result:** ✅ Report loads successfully with 0 data rows (no maintenance schedules due yet)

---

## Testing Summary

All four reports were tested via:
1. **Console Testing:** Executed each report's `execute()` function via Frappe console
2. **Browser Testing:** Opened each report in the browser to verify UI rendering

**Test Results:**
- ✅ Compliance Status Report: 20 assets loaded
- ✅ Asset Criticality Matrix: 20 assets loaded
- ✅ Asset Lifecycle Report: 20 assets loaded
- ✅ Maintenance Due Report: 0 schedules (no due maintenance yet)

**Report URLs:**
- http://172.24.13.88:8000/app/query-report/Compliance%20Status%20Report
- http://172.24.13.88:8000/app/query-report/Asset%20Criticality%20Matrix
- http://172.24.13.88:8000/app/query-report/Asset%20Lifecycle%20Report
- http://172.24.13.88:8000/app/query-report/Maintenance%20Due%20Report

---

## Root Cause Analysis

**Problem:** Reports were created with assumed field names that don't match the actual DocType definitions.

**Pattern:** Similar to the dashboard chart errors fixed earlier (e.g., `work_order_status` → `workflow_state`, `risk_classification` → `inherent_risk_level`).

**Solution Approach:**
1. Examined each report's Python file to identify incorrect field names in SQL queries
2. Checked the actual Asset and Asset Maintenance Schedule DocType JSON files
3. Updated SQL queries to use correct field names that exist in the database
4. Removed fields that don't exist in the DocTypes
5. Tested each report to ensure they load without errors

---

## Files Modified

1. `apps/sigma/sigma/sigma_asset_integrations/report/compliance_status_report/compliance_status_report.py`
2. `apps/sigma/sigma/sigma_asset_integrations/report/asset_criticality_matrix/asset_criticality_matrix.py`
3. `apps/sigma/sigma/sigma_asset_integrations/report/asset_lifecycle_report/asset_lifecycle_report.py`
4. `apps/sigma/sigma/sigma_asset_integrations/report/maintenance_due_report/maintenance_due_report.py`

---

**Status:** ✅ **ALL REPORT FIELD NAME ERRORS FIXED AND TESTED**

