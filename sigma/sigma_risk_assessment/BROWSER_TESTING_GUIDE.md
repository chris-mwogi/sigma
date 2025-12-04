# Browser Testing Guide - Risk Assessment Module

**Testing URL:** http://172.24.13.88:8000/  
**Date:** 2025-11-18  
**Status:** ✅ All Issues Fixed - Ready for Testing

---

## 🎯 Quick Test Checklist

### 1. Risk Assessment Workspace
**URL:** http://172.24.13.88:8000/app/risk-assessment

**What to Test:**
- [ ] Workspace loads without errors
- [ ] All 10 shortcuts are visible
- [ ] All 24 links are organized in 5 sections
- [ ] Counters show correct numbers

**Expected Results:**
- ✅ Workspace displays with orange theme
- ✅ "Risk Register" shortcut shows count of Active risks
- ✅ All sections are properly organized

---

### 2. Risk Assessment DocType
**URL:** http://172.24.13.88:8000/app/risk-assessment

**What to Test:**
- [ ] Click "Risk Assessment" shortcut
- [ ] List view loads without permission errors
- [ ] Status filter works in list view
- [ ] Can open existing assessment (e.g., RASS-2025-01075)

**Expected Results:**
- ✅ List view displays 5 assessments
- ✅ Status field is accessible (no "Field not permitted" error)
- ✅ Can filter by status: Draft, In Progress, Completed, Approved
- ✅ Assessment form shows all fields correctly

**Test Data Available:**
- RASS-2025-01075: Regulatory Non-Compliance (Completed, Low residual risk)
- RASS-2025-01076: Revenue Collection Shortfall (Completed, Medium residual risk)
- RASS-2025-01077: Cybersecurity Breach (Completed, High residual risk)

---

### 3. Risk Register Report
**URL:** http://172.24.13.88:8000/app/query-report/Risk%20Register%20Report

**What to Test:**
- [ ] Report loads without SQL errors
- [ ] Shows 3 risk records
- [ ] "Current Risk Rating" column displays values (Low/Medium/High)
- [ ] "Last Assessment" column shows dates (2025-11-18)
- [ ] Can filter by Risk Category, Status, Risk Owner

**Expected Results:**
- ✅ 3 records displayed:
  - RISK-2025-01052: Cybersecurity Breach (High)
  - RISK-2025-01053: Revenue Collection Shortfall (Medium)
  - RISK-2025-01054: Regulatory Non-Compliance (Low)
- ✅ All columns populated correctly
- ✅ No "Unknown column" errors

---

### 4. Risk Heat Map
**URL:** http://172.24.13.88:8000/app/query-report/Risk%20Heat%20Map

**What to Test:**
- [ ] Report loads without SQL errors
- [ ] Shows 6 records (3 risks with inherent and residual)
- [ ] Can switch between "Inherent" and "Residual" risk types
- [ ] Risk scores calculated correctly
- [ ] Heat map visualization displays

**Expected Results:**
- ✅ Residual Risk Type shows:
  - Cybersecurity Breach: High (Score: 16)
  - Revenue Collection Shortfall: Medium (Score: 9)
  - Regulatory Non-Compliance: Low (Score: 4)
- ✅ No "Unknown column 'ra.residual_impact_level'" error
- ✅ Chart displays risk distribution

---

### 5. Risk Treatment Status Report
**URL:** http://172.24.13.88:8000/app/query-report/Risk%20Treatment%20Status%20Report

**What to Test:**
- [ ] Report loads without SQL errors
- [ ] Shows 1 treatment plan record
- [ ] Status column displays correctly
- [ ] Progress percentage shows
- [ ] Can filter by Status, Strategy, Owner

**Expected Results:**
- ✅ 1 record displayed:
  - RTP-2025-01079: Treatment Plan for Revenue Collection Shortfall
  - Status: Approved
  - Strategy: Transfer
  - Progress: 0%
- ✅ No "Unknown column 'rtp.status'" error

---

### 6. Risk Incident Analysis
**URL:** http://172.24.13.88:8000/app/query-report/Risk%20Incident%20Analysis

**What to Test:**
- [ ] Report loads without errors
- [ ] Shows 2 incident records
- [ ] Incident status displays correctly
- [ ] Financial impact shows
- [ ] Chart displays incident distribution

**Expected Results:**
- ✅ 2 records displayed:
  - INC-2025-01068: Unauthorized Access Attempt (Under Investigation)
  - INC-2025-01069: Payment Processing Delay (Resolved)
- ✅ All columns populated
- ✅ Chart shows incident breakdown

---

### 7. Compliance Status Report
**URL:** http://172.24.13.88:8000/app/query-report/Compliance%20Status%20Report

**What to Test:**
- [ ] Report loads without errors
- [ ] Ready to display compliance data when available

**Expected Results:**
- ✅ Report executes successfully (0 records - no test data)
- ✅ No SQL errors

---

### 8. KRI Dashboard Report
**URL:** http://172.24.13.88:8000/app/query-report/KRI%20Dashboard%20Report

**What to Test:**
- [ ] Report loads without errors
- [ ] Ready to display KRI data when available

**Expected Results:**
- ✅ Report executes successfully (0 records - no test data)
- ✅ No SQL errors

---

## 🐛 Issues That Were Fixed

### ✅ Issue 1: Risk Assessment Permission Error
- **Before:** "Field not permitted in query: status"
- **After:** Status field accessible in list view and filters

### ✅ Issue 2: Risk Heat Map SQL Error
- **Before:** "Unknown column 'ra.residual_impact_level'"
- **After:** Correct field names used (residual_impact, residual_likelihood)

### ✅ Issue 3: Risk Register Report SQL Error
- **Before:** "Unknown column 'rr.current_risk_rating'"
- **After:** Subquery fetches rating from latest assessment

### ✅ Issue 4: Risk Treatment Status Report SQL Error
- **Before:** "Unknown column 'rtp.status'"
- **After:** Correct field name used (plan_status)

---

## 📞 Support

If you encounter any issues during testing:
1. Check the browser console for JavaScript errors (F12)
2. Check the Frappe error log: http://172.24.13.88:8000/app/error-log
3. Verify test data exists by running the data check script
4. Clear browser cache and reload

---

## ✅ Testing Complete

Once all checkboxes are marked, the Risk Assessment module is verified as production-ready!

