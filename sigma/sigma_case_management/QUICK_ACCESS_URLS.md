# Case Management Module - Quick Access URLs

## 🌐 Base URL
**http://172.24.13.88:8000/**

---

## 📊 Main Workspace
**Case Management Workspace**  
http://172.24.13.88:8000/app/case-management

---

## 📋 Core DocTypes

### Main DocTypes
1. **Case (List View)**  
   http://172.24.13.88:8000/app/case

2. **Case Investigation (List View)**  
   http://172.24.13.88:8000/app/case-investigation

3. **Case Activity (List View)**  
   http://172.24.13.88:8000/app/case-activity

4. **Case Action Plan (List View)**  
   http://172.24.13.88:8000/app/case-action-plan

5. **Case Evidence (List View)**  
   http://172.24.13.88:8000/app/case-evidence

### Master Data
6. **Case Settings (Single)**  
   http://172.24.13.88:8000/app/case-settings

7. **Case Severity Matrix (List View)**  
   http://172.24.13.88:8000/app/case-severity-matrix

8. **Case Category (List View)**  
   http://172.24.13.88:8000/app/case-category

9. **Case Source (List View)**  
   http://172.24.13.88:8000/app/case-source

---

## 📊 Reports & Analytics

### Script Reports
1. **Case Summary Dashboard**  
   http://172.24.13.88:8000/app/query-report/Case%20Summary%20Dashboard

2. **Case Aging Report**  
   http://172.24.13.88:8000/app/query-report/Case%20Aging%20Report

3. **High Severity Case Matrix**  
   http://172.24.13.88:8000/app/query-report/High%20Severity%20Case%20Matrix

4. **Case Outcome Analysis**  
   http://172.24.13.88:8000/app/query-report/Case%20Outcome%20Analysis

5. **Investigation SLA Adherence**  
   http://172.24.13.88:8000/app/query-report/Investigation%20SLA%20Adherence

6. **Root Cause Analysis**  
   http://172.24.13.88:8000/app/query-report/Root%20Cause%20Analysis

---

## 🧪 Test Data (Direct Links)

### Test Cases
1. **CASE-2025-01122** (Suspected Procurement Fraud - Critical)  
   http://172.24.13.88:8000/app/case/CASE-2025-01122

2. **CASE-2025-01123** (Workplace Harassment - High)  
   http://172.24.13.88:8000/app/case/CASE-2025-01123

3. **CASE-2025-01124** (Policy Violation - Medium)  
   http://172.24.13.88:8000/app/case/CASE-2025-01124

### Test Investigations
1. **INV-2025-01125** (Linked to CASE-2025-01122)  
   http://172.24.13.88:8000/app/case-investigation/INV-2025-01125

2. **INV-2025-01126** (Linked to CASE-2025-01123)  
   http://172.24.13.88:8000/app/case-investigation/INV-2025-01126

### Test Activities
1. **ACT-2025-01127**  
   http://172.24.13.88:8000/app/case-activity/ACT-2025-01127

2. **ACT-2025-01128**  
   http://172.24.13.88:8000/app/case-activity/ACT-2025-01128

3. **ACT-2025-01129**  
   http://172.24.13.88:8000/app/case-activity/ACT-2025-01129

4. **ACT-2025-01130**  
   http://172.24.13.88:8000/app/case-activity/ACT-2025-01130

---

## 🔧 Administration

### User Management
**Role List**  
http://172.24.13.88:8000/app/role

**User List**  
http://172.24.13.88:8000/app/user

### System Settings
**DocType List** (View all Case Management DocTypes)  
http://172.24.13.88:8000/app/doctype

**Report List** (View all reports)  
http://172.24.13.88:8000/app/report

**Workspace List** (View all workspaces)  
http://172.24.13.88:8000/app/workspace

---

## 🚀 Quick Actions

### Create New Records
1. **New Case**  
   http://172.24.13.88:8000/app/case/new

2. **New Investigation**  
   http://172.24.13.88:8000/app/case-investigation/new

3. **New Activity**  
   http://172.24.13.88:8000/app/case-activity/new

4. **New Action Plan**  
   http://172.24.13.88:8000/app/case-action-plan/new

5. **New Evidence**  
   http://172.24.13.88:8000/app/case-evidence/new

---

## 📚 Documentation Files

Located in: `apps/sigma/sigma/sigma_case_management/`

1. **FINAL_IMPLEMENTATION_SUMMARY.md** - Comprehensive overview of all 8 phases
2. **BROWSER_TESTING_GUIDE.md** - Step-by-step testing instructions
3. **CASE_MANAGEMENT_MODULE_SUMMARY.md** - Technical specifications
4. **QUICK_ACCESS_URLS.md** - This file

---

## ✅ Quick Verification Checklist

Use these URLs to quickly verify the module is working:

- [ ] Open Workspace: http://172.24.13.88:8000/app/case-management
- [ ] View Case List: http://172.24.13.88:8000/app/case
- [ ] Open Test Case: http://172.24.13.88:8000/app/case/CASE-2025-01122
- [ ] Run Summary Report: http://172.24.13.88:8000/app/query-report/Case%20Summary%20Dashboard
- [ ] Check Settings: http://172.24.13.88:8000/app/case-settings

---

## 🎯 Recommended Testing Sequence

1. **Start Here:** Case Management Workspace
2. **View Master Data:** Settings → Severity Matrix → Categories → Sources
3. **Review Test Cases:** Open all 3 test cases
4. **Check Investigations:** View 2 test investigations
5. **Review Activities:** View 4 test activities
6. **Run Reports:** Test all 6 reports with filters
7. **Create New Case:** Test case creation workflow
8. **Test Auto-Calculations:** Change severity/category and verify risk score updates

---

## 📞 Support

For issues or questions, refer to:
- **BROWSER_TESTING_GUIDE.md** for detailed testing instructions
- **FINAL_IMPLEMENTATION_SUMMARY.md** for complete module documentation

---

*Last Updated: November 18, 2025*

