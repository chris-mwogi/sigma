# Case Management Module - Browser Testing Guide

## 🌐 Access Information
- **Base URL:** http://172.24.13.88:8000/
- **Login:** Use your ERPNext credentials
- **Module:** Sigma Case Management

---

## 📋 Phase-by-Phase Testing Checklist

### Phase 1: Core Master DocTypes ✅

#### 1.1 Case Settings
**URL:** http://172.24.13.88:8000/app/case-settings

**Test Steps:**
1. Navigate to Case Settings
2. Verify default values:
   - Default SLA Hours: 72
   - SLA Reminder Hours: 24
   - Evidence Hash Algorithm: SHA256
   - Max File Size: 50 MB
3. Try modifying settings and saving
4. Verify validation (e.g., negative values should be rejected)

**Expected Result:** Settings save successfully with proper validation

---

#### 1.2 Case Severity Matrix
**URL:** http://172.24.13.88:8000/app/case-severity-matrix

**Test Steps:**
1. View list of severity levels (Critical, High, Medium, Low)
2. Open "Critical" severity
3. Verify fields:
   - Severity Score: 4
   - Response Time Hours: 24
   - Escalation Required: Yes
4. Create a new custom severity level
5. Test sorting by severity score

**Expected Result:** All severity levels display correctly with proper scoring

---

#### 1.3 Case Category
**URL:** http://172.24.13.88:8000/app/case-category

**Test Steps:**
1. View list of categories (Fraud, Corruption, Harassment, etc.)
2. Open "Fraud" category
3. Verify Risk Weight field
4. Create a new category
5. Test category hierarchy (if parent categories exist)

**Expected Result:** Categories display with risk weights, new categories can be created

---

#### 1.4 Case Source
**URL:** http://172.24.13.88:8000/app/case-source

**Test Steps:**
1. View list of sources (Hotline, Email, Walk-in, etc.)
2. Create a new source
3. Verify source can be linked to cases

**Expected Result:** Sources list correctly, can be created and linked

---

#### 1.5 Case (Main DocType)
**URL:** http://172.24.13.88:8000/app/case

**Test Steps:**
1. View case list (should show 3 test cases: CASE-2025-01122, CASE-2025-01123, CASE-2025-01124)
2. Open CASE-2025-01122
3. Verify all sections:
   - Case Information (Title, Description, Status)
   - Classification (Category, Severity, Source)
   - Assignment (Assigned To, Reported By)
   - Dates (Reported Date, SLA Due Date, Closure Date)
   - Risk Assessment (Risk Score - auto-calculated)
   - Compliance & Standards (Child table for compliance links)
   - Communication Log (Child table for communications)
4. Test auto-calculations:
   - Change severity → Risk Score should recalculate
   - Change status to "Closed" → Actual Closure Date should auto-fill
5. Test submission workflow (Save → Submit)
6. Test confidentiality levels (Public, Restricted, Highly Restricted, Confidential)

**Expected Result:** 
- All fields display correctly
- Auto-calculations work
- Submission workflow functions
- Child tables are accessible

---

### Phase 2: Investigation & Evidence ✅

#### 2.1 Case Investigation
**URL:** http://172.24.13.88:8000/app/case-investigation

**Test Steps:**
1. View investigation list (should show INV-2025-01125, INV-2025-01126)
2. Create new investigation:
   - Link to existing case
   - Set investigation type (e.g., "Full Investigation")
   - Set lead investigator
   - Set start date and target completion date
3. Add findings and recommendations
4. Test submission (status must be "Completed" before submit)
5. Verify date validation (target date cannot be before start date)

**Expected Result:** Investigations can be created, linked to cases, and submitted with proper validation

---

#### 2.2 Case Evidence
**URL:** http://172.24.13.88:8000/app/case-evidence

**Test Steps:**
1. View evidence list
2. Create new evidence:
   - Link to case
   - Set evidence type (Document, Physical, Digital, Testimony, etc.)
   - Upload file attachment
   - Set collection date and collected by
3. Test chain of custody:
   - Add custody log entries (Evidence Custody Log child table)
   - Track transfers between custodians
4. Verify evidence numbering (EVD-2025-XXXXX format)

**Expected Result:** Evidence can be created with proper tracking and chain of custody

---

#### 2.3 Case Activity
**URL:** http://172.24.13.88:8000/app/case-activity

**Test Steps:**
1. View activity list (should show ACT-2025-01127 through ACT-2025-01130)
2. Create new activity:
   - Link to case
   - Set activity type (Interview, Site Visit, Document Review, etc.)
   - Set activity date and performed by
   - Add activity notes
3. Test activity timeline view
4. Verify activity numbering (ACT-2025-XXXXX format)

**Expected Result:** Activities can be logged and tracked against cases

---

### Phase 3: Compliance & Action Plans ✅

#### 3.1 Case Compliance Link (Child Table)
**Test Steps:**
1. Open any case (e.g., CASE-2025-01122)
2. Scroll to "Compliance & Standards" section
3. Add compliance link:
   - Select standard (ISO 31000, ISO 37001, ISO 27001, ACFE, DOJ, etc.)
   - Enter requirement reference
   - Set compliance status (Compliant, Non-Compliant, Partially Compliant, Under Review)
   - Add notes
4. Save case
5. Verify compliance links are saved

**Expected Result:** Compliance links can be added and tracked within cases

---

#### 3.2 Case Communication Log (Child Table)
**Test Steps:**
1. Open any case
2. Scroll to "Communication Log" section
3. Add communication entry:
   - Set communication date
   - Select type (Email, Phone Call, Meeting, etc.)
   - Enter communicated by and to
   - Add subject and notes
4. Save case
5. Verify communication log is saved

**Expected Result:** All communications can be logged and tracked

---

#### 3.3 Case Action Plan
**URL:** http://172.24.13.88:8000/app/case-action-plan

**Test Steps:**
1. View action plan list
2. Create new action plan:
   - Link to case
   - Set action type (Corrective Action, Preventive Action, Disciplinary Action, etc.)
   - Set priority (Critical, High, Medium, Low)
   - Assign responsible person
   - Set due date
   - Add action description
3. Update status (Planned → In Progress → Completed)
4. Test auto-completion date (when status = Completed)
5. Verify action plan numbering (CAP-2025-XXXXX format)

**Expected Result:** Action plans can be created, tracked, and completed

---

### Phase 4: Reporting & Analytics ✅

#### 4.1 Case Summary Dashboard
**URL:** http://172.24.13.88:8000/app/query-report/Case%20Summary%20Dashboard

**Test Steps:**
1. Open report
2. Test filters:
   - From Date / To Date
   - Status
   - Severity
   - Case Category
   - Assigned To
3. Verify columns display:
   - Case ID, Title, Status, Severity, Category
   - Risk Score, Reported Date, SLA Due Date
   - Assigned To, Confidentiality Level
4. Check chart (Cases by Status)

**Expected Result:** Report displays with filters and chart

---

#### 4.2 Case Aging Report
**URL:** http://172.24.13.88:8000/app/query-report/Case%20Aging%20Report

**Test Steps:**
1. Open report
2. Verify aging calculations:
   - Days Open
   - SLA Breach (Yes/No/N/A)
   - Days Overdue
3. Check aging buckets chart (0-7, 8-14, 15-30, 31-60, 60+ days)
4. Test filters

**Expected Result:** Aging metrics calculate correctly with visual chart

---

#### 4.3 High Severity Case Matrix
**URL:** http://172.24.13.88:8000/app/query-report/High%20Severity%20Case%20Matrix

**Test Steps:**
1. Open report
2. Verify only Critical and High severity cases display
3. Check risk score calculations
4. View chart (Average Risk Score by Category)

**Expected Result:** Only high-severity cases shown with risk analysis

---

#### 4.4 Case Outcome Analysis
**URL:** http://172.24.13.88:8000/app/query-report/Case%20Outcome%20Analysis

**Test Steps:**
1. Open report
2. Verify only closed cases display
3. Check resolution days calculation
4. View chart (Average Resolution Days by Category)

**Expected Result:** Closed cases analyzed with resolution metrics

---

#### 4.5 Investigation SLA Adherence
**URL:** http://172.24.13.88:8000/app/query-report/Investigation%20SLA%20Adherence

**Test Steps:**
1. Open report
2. Verify investigation completion tracking
3. Check SLA status (On Time/Delayed/In Progress)
4. View summary section (Adherence Rate %)

**Expected Result:** Investigation SLA compliance tracked with adherence rate

---

#### 4.6 Root Cause Analysis
**URL:** http://172.24.13.88:8000/app/query-report/Root%20Cause%20Analysis

**Test Steps:**
1. Open report
2. Verify findings aggregated by category
3. Check recent investigation findings
4. View chart (Total Cases by Category)

**Expected Result:** Root causes aggregated and visualized

---

### Phase 5: Workspace & Integration ✅

#### 5.1 Case Management Workspace
**URL:** http://172.24.13.88:8000/app/case-management

**Test Steps:**
1. Navigate to Case Management workspace
2. Verify all shortcuts are present:
   - **Main DocTypes:** Case, Case Investigation, Case Activity, Case Action Plan
   - **Master Data:** Case Settings, Case Severity Matrix, Case Category, Case Source
   - **Reports:** All 6 reports listed
3. Click each shortcut to verify navigation
4. Check color coding of shortcuts

**Expected Result:** Workspace displays all shortcuts with proper navigation

---

## 🔐 Phase 6 & 7: Workflows & Security (Manual Setup Required)

### 6.1 Role Setup
**Test Steps:**
1. Go to User Management → Role
2. Verify roles exist:
   - Case Manager
   - Case Intake Officer
   - Investigator
   - Ethics Officer
   - Legal Officer
   - Case Viewer
3. Assign roles to test users

---

### 6.2 Permission Testing
**Test Steps:**
1. Login as different roles
2. Verify access levels:
   - **Case Manager:** Full access
   - **Case Intake Officer:** Create and submit cases
   - **Investigator:** Read and update cases/investigations
   - **Ethics Officer:** Read and review compliance
   - **Legal Officer:** Read and review
   - **Case Viewer:** Read only

---

## ✅ Final Verification Checklist

- [ ] All 12 DocTypes accessible
- [ ] All 6 reports functional
- [ ] Workspace navigation works
- [ ] Auto-calculations function (Risk Score, SLA, Closure Date)
- [ ] Child tables display and save correctly
- [ ] Submission workflows work
- [ ] Date validations function
- [ ] Filters work on all reports
- [ ] Charts display on reports
- [ ] Test data displays correctly

---

## 🐛 Common Issues & Solutions

### Issue: Child tables not showing
**Solution:** Ensure migration completed successfully. Check Case.json has compliance_links and communication_log fields.

### Issue: Reports show no data
**Solution:** Ensure test data was created. Run test data creation script.

### Issue: Auto-calculations not working
**Solution:** Check Case.py has calculate_risk_score() and calculate_sla_due_date() methods.

### Issue: Permission denied
**Solution:** Ensure user has appropriate role assigned.

---

## 📞 Support
For issues or questions, contact the development team or check the module documentation.

