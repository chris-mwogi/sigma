# Phase 7: Testing & Documentation Guide

## Risk Assessment Module - Complete Testing Guide

This guide provides comprehensive testing instructions for the re-engineered Risk Assessment module.

---

## 🎯 Testing Overview

The Risk Assessment module has been completely re-engineered to comply with ISO 31000 standards and includes:
- **17 DocTypes** (5 Master, 2 Register/Assessment, 3 Controls/Treatment, 4 Monitoring/Incident, 3 Child Tables)
- **6 Script Reports** with filters, charts, and data visualization
- **1 Comprehensive Workspace** with 10 shortcuts and 24 links

---

## 📋 Testing Checklist

### Phase 1: Configuration & Master Data

#### 1.1 Risk Dashboard Settings
**URL:** `http://172.24.13.88:8000/app/risk-dashboard-settings`

**Test Steps:**
1. Open Risk Dashboard Settings
2. Verify default thresholds:
   - Low Threshold: ≤ 6
   - Medium Threshold: ≤ 12
   - High Threshold: ≤ 20
   - Critical: > 20
3. Enable email alerts
4. Save settings

**Expected Result:** Settings saved successfully with proper threshold validation.

---

#### 1.2 Risk Category (NestedSet)
**URL:** `http://172.24.13.88:8000/app/risk-category`

**Test Steps:**
1. Create parent category: "Financial Risk" (Code: FIN)
2. Create child category: "Revenue Risk" (Parent: Financial Risk)
3. Verify tree structure displays correctly
4. Test category code uniqueness validation

**Expected Result:** Hierarchical category structure with proper parent-child relationships.

---

#### 1.3 Risk Impact Matrix
**URL:** `http://172.24.13.88:8000/app/risk-impact-matrix`

**Test Steps:**
1. Verify 5 default impact levels exist:
   - Low (Score: 1)
   - Medium (Score: 2)
   - High (Score: 3)
   - Critical (Score: 4)
   - Catastrophic (Score: 5)
2. Create new impact level with custom score
3. Test score uniqueness validation

**Expected Result:** Impact levels with unique scores and proper descriptions.

---

#### 1.4 Risk Likelihood Matrix
**URL:** `http://172.24.13.88:8000/app/risk-likelihood-matrix`

**Test Steps:**
1. Verify 5 default likelihood levels exist:
   - Rare (Score: 1)
   - Unlikely (Score: 2)
   - Possible (Score: 3)
   - Likely (Score: 4)
   - Almost Certain (Score: 5)
2. Create new likelihood level with custom score
3. Test score uniqueness validation

**Expected Result:** Likelihood levels with unique scores and proper descriptions.

---

#### 1.5 Risk Alert Recipient
**URL:** `http://172.24.13.88:8000/app/risk-alert-recipient`

**Test Steps:**
1. Create alert recipient with email
2. Select alert types (Critical Risk, High Risk, etc.)
3. Set active status
4. Save and verify

**Expected Result:** Alert recipient configured for specified risk events.

---

### Phase 2: Risk Register & Assessment

#### 2.1 Risk Register (Submittable)
**URL:** `http://172.24.13.88:8000/app/risk-register`

**Test Steps:**
1. Create new risk:
   - Title: "Data Breach Risk"
   - Category: "Technology Risk"
   - Owner: Select user
   - Status: "Active"
2. Save as draft
3. Submit the risk
4. Verify auto-naming (RISK-YYYY-#####)
5. Check next review date calculation

**Expected Result:**
- Risk created with auto-generated ID
- Next review date = Date Identified + Review Frequency
- Status changes to Submitted (docstatus=1)

---

#### 2.2 Risk Assessment (Submittable)
**URL:** `http://172.24.13.88:8000/app/risk-assessment`

**Test Steps:**
1. Create new assessment:
   - Linked Risk: Select from Risk Register
   - Assessment Type: "Initial"
   - Assessment Date: Today
   - Assessed By: Select user
2. **Inherent Risk:**
   - Impact: "Critical" (Score: 4)
   - Likelihood: "Likely" (Score: 4)
   - Verify auto-calculation: Score = 16, Rating = "High"
3. **Residual Risk:**
   - Impact: "Medium" (Score: 2)
   - Likelihood: "Possible" (Score: 3)
   - Verify auto-calculation: Score = 6, Rating = "Low"
4. Add existing controls description
5. Select risk response strategy
6. Submit assessment

**Expected Result:**
- Inherent Risk Score: 16 (4 × 4)
- Inherent Risk Rating: "High"
- Residual Risk Score: 6 (2 × 3)
- Residual Risk Rating: "Low"
- Risk reduction percentage calculated
- Assessment submitted successfully


### Phase 4: Monitoring & Incidents

#### 4.1 Compliance Requirement
**URL:** `http://172.24.13.88:8000/app/compliance-requirement`

**Test Steps:**
1. Create new compliance requirement:
   - Title: "ISO 27001 Compliance"
   - Type: "Industry Standard"
   - Framework: "ISO 27001"
   - Owner: Select user
   - Status: "In Progress"
   - Description: "Information security management"
   - Current Compliance Level: 75%
   - Priority: "High"
2. Add gap analysis and remediation plan
3. Set target compliance date
4. Save requirement

**Expected Result:** Compliance requirement tracked with progress percentage and gap analysis.

---

#### 4.2 Business Process Register
**URL:** `http://172.24.13.88:8000/app/business-process-register`

**Test Steps:**
1. Create new business process:
   - Name: "Revenue Collection Process"
   - Code: "REV-001"
   - Owner: Select user
   - Criticality: "High"
   - Description: "End-to-end revenue collection"
2. Link to related risks
3. Add process documentation
4. Save process

**Expected Result:** Business process registered with risk linkage and criticality tracking.

---

#### 4.3 Key Risk Indicator (KRI)
**URL:** `http://172.24.13.88:8000/app/key-risk-indicator`

**Test Steps:**
1. Create new KRI:
   - Name: "System Uptime Percentage"
   - Category: "Technology"
   - Linked Risk: Select from Risk Register
   - Owner: Select user
   - Description: "Measures system availability"
   - Unit: "Percentage"
   - Frequency: "Daily"
   - Target Value: 99.9
   - Current Value: 99.5
2. Set thresholds:
   - Direction: "Higher is Better"
   - Green: ≥ 99.5
   - Yellow: ≥ 98.0
   - Red: < 98.0
3. Status: "Active"
4. Save KRI
5. Verify current status calculation

**Expected Result:**
- KRI created with threshold-based monitoring
- Current Status: "Normal" (99.5 ≥ 99.5)
- Trend tracking enabled

---

#### 4.4 Risk Incident (Submittable)
**URL:** `http://172.24.13.88:8000/app/risk-incident`

**Test Steps:**
1. Create new incident:
   - Title: "Unauthorized Access Attempt"
   - Type: "Security Incident"
   - Category: "Technology Risk"
   - Date: Today
   - Reported By: Select user
   - Status: "Reported"
   - Impact Level: "Medium"
   - Financial Impact: 5,000
   - Linked Risk: Select from Risk Register
2. Add incident description
3. Set investigation details:
   - Investigation Status: "In Progress"
   - Investigation Owner: Select user
4. Save incident
5. Update status to "Resolved"
6. Submit incident

**Expected Result:**
- Incident tracked through lifecycle
- Investigation workflow managed
- Financial impact recorded
- Linked to related risk

---

### Phase 5: Reports & Analytics

#### 5.1 Risk Register Report
**URL:** `http://172.24.13.88:8000/app/query-report/Risk%20Register%20Report`

**Test Steps:**
1. Open report
2. Apply filters:
   - Category: "Technology Risk"
   - Status: "Active"
   - Risk Rating: "High"
3. Verify columns display:
   - Risk ID, Title, Category, Owner
   - Current Risk Rating
   - Assessment/Treatment/Incident counts
4. Export to Excel

**Expected Result:** Comprehensive risk register view with linked information counts.

---

#### 5.2 Risk Heat Map
**URL:** `http://172.24.13.88:8000/app/query-report/Risk%20Heat%20Map`

**Test Steps:**
1. Open report
2. Select Risk Type: "Inherent Risk"
3. Apply filters:
   - Category: All
   - Date Range: Last 6 months
4. Verify heat map data:
   - Impact vs Likelihood distribution
   - Risk counts in each cell
5. View bar chart visualization
6. Switch to "Residual Risk"
7. Compare distributions

**Expected Result:**
- Heat map showing risk distribution
- Bar chart by impact/likelihood
- Ability to toggle between Inherent and Residual

---

#### 5.3 Risk Treatment Status Report
**URL:** `http://172.24.13.88:8000/app/query-report/Risk%20Treatment%20Status%20Report`

**Test Steps:**
1. Open report
2. Apply filters:
   - Status: "In Progress"
   - Owner: Select user
3. Verify columns:
   - Plan ID, Title, Strategy
   - Progress %, Budget Variance
   - Action counts
4. View pie chart by status

**Expected Result:** Treatment plan progress tracking with budget variance analysis.

---

#### 5.4 Compliance Status Report
**URL:** `http://172.24.13.88:8000/app/query-report/Compliance%20Status%20Report`

**Test Steps:**
1. Open report
2. Apply filters:
   - Status: All
   - Priority: "High"
3. Verify columns:
   - Requirement ID, Title, Framework
   - Compliance Level %
   - Days to Review
4. View pie chart by status

**Expected Result:** Compliance tracking with review date monitoring.

---

#### 5.5 KRI Dashboard Report
**URL:** `http://172.24.13.88:8000/app/query-report/KRI%20Dashboard%20Report`

**Test Steps:**
1. Open report
2. Apply filters:
   - Status: "Active"
   - Current Status: All
3. Verify columns:
   - KRI Name, Category
   - Current Value vs Target
   - Threshold Status
   - Trend
4. View bar chart by status

**Expected Result:** KRI monitoring dashboard with threshold-based alerts.

---

#### 5.6 Risk Incident Analysis
**URL:** `http://172.24.13.88:8000/app/query-report/Risk%20Incident%20Analysis`

**Test Steps:**
1. Open report
2. Apply filters:
   - Date Range: Last 3 months
   - Status: All
3. Verify columns:
   - Incident ID, Title, Type
   - Financial Impact
   - Investigation Status
4. View summary statistics
5. View bar chart by incident type

**Expected Result:** Incident analysis with financial impact tracking.

---

### Phase 6: Workspace & Integration

#### 6.1 Risk Assessment Workspace
**URL:** `http://172.24.13.88:8000/app/risk-assessment`

**Test Steps:**
1. Open workspace
2. Verify 10 shortcuts display with counters:
   - Risk Register (Active count)
   - Risk Assessment (Submitted count)
   - Risk Control (Implemented count)
   - Risk Treatment Plan (In Progress count)
   - Key Risk Indicator (Active count)
   - KRI Critical (Critical count)
   - Risk Incident (Open count)
   - Compliance (Active count)
   - Risk Register Report
   - Risk Heat Map
3. Verify 5 card sections:
   - Risk Register & Assessment
   - Controls & Treatment
   - Monitoring & Incidents
   - Reports & Analytics
   - Settings & Configuration
4. Click each shortcut and verify navigation
5. Click each link and verify navigation

**Expected Result:**
- All shortcuts display with correct counters
- All links navigate to correct pages
- Workspace layout is clean and organized

---

## 🔍 Integration Testing

### Test Cross-DocType Relationships

1. **Risk Register → Risk Assessment:**
   - Create risk in Risk Register
   - Create assessment linked to risk
   - Verify assessment count updates in Risk Register

2. **Risk Register → Risk Treatment Plan:**
   - Create treatment plan linked to risk
   - Verify treatment count updates in Risk Register

3. **Risk Register → Risk Incident:**
   - Create incident linked to risk
   - Verify incident count updates in Risk Register

4. **Risk Control → Risk Assessment:**
   - Reference control in assessment's "Existing Controls"
   - Verify linkage

5. **KRI → Risk Register:**
   - Link KRI to risk
   - Verify KRI tracks risk-related metrics

---

## 🎨 UI/UX Testing

### Visual Testing Checklist

- [ ] All forms display correctly on desktop
- [ ] All forms display correctly on mobile
- [ ] Field labels are clear and descriptive
- [ ] Required fields are marked with asterisk
- [ ] Validation messages are clear
- [ ] Auto-calculations work in real-time
- [ ] Charts render correctly in reports
- [ ] Filters work correctly in reports
- [ ] Export to Excel works for all reports
- [ ] Print view works for all DocTypes

---

## 🔐 Permission Testing

### Role-Based Access Control

Test with different user roles:

1. **System Manager:**
   - Full access to all DocTypes
   - Can create, read, update, delete
   - Can submit and cancel

2. **Risk Manager:**
   - Full access to risk management DocTypes
   - Can create, read, update
   - Can submit assessments and treatment plans

3. **Risk Owner:**
   - Read access to all
   - Update access to assigned risks
   - Cannot delete or cancel

4. **User:**
   - Read-only access to reports
   - Can view workspace

---

## 📊 Performance Testing

### Load Testing Checklist

- [ ] Create 100+ risks and verify list view performance
- [ ] Create 50+ assessments and verify report generation time
- [ ] Test heat map with large dataset (500+ assessments)
- [ ] Test workspace shortcuts with high record counts
- [ ] Verify auto-calculations don't slow down form saves

---

## ✅ Final Validation

### Complete Workflow Test

1. **Setup Phase:**
   - Configure Risk Dashboard Settings
   - Create risk categories
   - Create impact/likelihood matrices

2. **Risk Identification:**
   - Create 5 risks in Risk Register
   - Submit all risks

3. **Risk Assessment:**
   - Create assessments for all 5 risks
   - Verify inherent and residual calculations
   - Submit assessments

4. **Risk Treatment:**
   - Create controls for high-rated risks
   - Create treatment plans with actions
   - Submit treatment plans

5. **Monitoring:**
   - Create KRIs for critical risks
   - Create compliance requirements
   - Create business processes

6. **Incident Management:**
   - Create 2 incidents
   - Track investigation
   - Resolve and submit

7. **Reporting:**
   - Run all 6 reports
   - Verify data accuracy
   - Export reports

8. **Workspace:**
   - Verify all counters are accurate
   - Test all navigation links

---

## 🐛 Known Issues & Limitations

### Current Limitations

1. **Risk Category NestedSet:**
   - Requires proper lft/rgt initialization
   - Use Frappe's rebuild tree function if issues occur

2. **Report Filters:**
   - Some filters may need adjustment based on data volume
   - Date range filters default to last 6 months

3. **Email Alerts:**
   - Requires email configuration in Frappe
   - Test in development before production

---

## 📝 Testing Sign-Off

### Testing Completed By

- **Tester Name:** ___________________________
- **Date:** ___________________________
- **Environment:** Development / Staging / Production
- **Browser:** Chrome / Firefox / Safari / Edge
- **Version:** ___________________________

### Test Results

- [ ] All DocTypes tested and working
- [ ] All reports tested and working
- [ ] Workspace tested and working
- [ ] Integration tested and working
- [ ] Performance acceptable
- [ ] No critical bugs found

### Notes:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

## 🚀 Next Steps

After successful testing:

1. **Production Deployment:**
   - Backup database
   - Run migrations
   - Reload workspace
   - Verify all DocTypes

2. **User Training:**
   - Conduct training sessions
   - Provide user documentation
   - Create video tutorials

3. **Go-Live:**
   - Monitor system performance
   - Collect user feedback
   - Address any issues

---

**End of Testing Guide**
#### 3.1 Risk Control
**URL:** `http://172.24.13.88:8000/app/risk-control`

**Test Steps:**
1. Create new control:
   - Name: "Multi-Factor Authentication"
   - Type: "Preventive"
   - Category: "IT-Dependent"
   - Owner: Select user
   - Implementation Status: "Implemented"
2. Add control description and objective
3. Set implementation date
4. Save control

**Expected Result:** Control created with proper categorization and status tracking.

---

#### 3.2 Risk Treatment Plan (Submittable)
**URL:** `http://172.24.13.88:8000/app/risk-treatment-plan`

**Test Steps:**
1. Create new treatment plan:
   - Title: "Cybersecurity Enhancement Plan"
   - Linked Risk: Select from Risk Register
   - Strategy: "Reduce"
   - Owner: Select user
   - Start Date: Today
   - Target Completion: +3 months
   - Estimated Budget: 100,000
2. Add treatment actions (child table):
   - Action 1: "Implement MFA" (Cost: 40,000)
   - Action 2: "Security Training" (Cost: 30,000)
3. Submit plan
4. Verify progress calculation
5. Check budget variance

**Expected Result:**
- Treatment plan submitted
- Progress % calculated from actions
- Budget variance = Estimated - Actual
- Action status tracked

---


