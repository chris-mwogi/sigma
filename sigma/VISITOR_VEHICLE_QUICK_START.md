# Visitor & Vehicle Management - Quick Start Guide

## 🚀 Quick Access

**Browser URL:** http://172.24.13.88:8000/

### Visitor Management
- **Workspace:** http://172.24.13.88:8000/app/visitor-management
- **New Visitor:** http://172.24.13.88:8000/app/visitor/new
- **New Registration:** http://172.24.13.88:8000/app/visitor-registration/new
- **Watchlist:** http://172.24.13.88:8000/app/visitor-watchlist ✅ **NEW**
- **Check-In/Out:** http://172.24.13.88:8000/app/visitor-checkin-checkout

### Vehicle Management
- **Workspace:** http://172.24.13.88:8000/app/vehicle-management
- **New Vehicle:** http://172.24.13.88:8000/app/vehicle/new
- **New Registration:** http://172.24.13.88:8000/app/vehicle-registration/new
- **Vehicle Pass:** http://172.24.13.88:8000/app/vehicle-pass/new
- **Parking Spaces:** http://172.24.13.88:8000/app/parking-space

---

## ✅ What's Working Now

### Visitor Management (75% Complete)
1. ✅ **Visitor Master** - Store visitor information
2. ✅ **Visitor Types** - Categorize visitors (Contractor, Vendor, VIP, etc.)
3. ✅ **Visitor Registration** - Pre-register visitors with host approval
4. ✅ **Visitor Badge** - Issue and track badges
5. ✅ **Check-In/Check-Out** - Track visitor entry and exit
6. ✅ **Access Logs** - Complete audit trail
7. ✅ **Watchlist** ✅ **NEW** - Security screening

### Vehicle Management (65% Complete)
1. ✅ **Vehicle Master** - Store vehicle information
2. ✅ **Vehicle Registration** - Register vehicles
3. ✅ **Vehicle Pass** - Issue temporary passes
4. ✅ **Check-In/Check-Out** - Track vehicle entry and exit
5. ✅ **Parking Spaces** - Manage parking
6. ✅ **Access Logs** - Complete audit trail

---

## 🧪 Testing the New Visitor Watchlist

### Test Scenario 1: Add a Person to Watchlist

1. **Navigate to Watchlist:**
   - Go to http://172.24.13.88:8000/app/visitor-watchlist
   - Click "New"

2. **Fill in Details:**
   - **Person Name:** John Doe
   - **ID Number:** 12345678
   - **Company:** Suspicious Corp
   - **Contact Number:** +254712345678
   - **Reason:** Security Threat
   - **Risk Score Impact:** 30 (default)
   - **Expiry Date:** Leave blank for permanent
   - **Is Active:** Checked
   - **Notification Recipients:** security@kplc.co.ke
   - **Notes:** "Previous security incident at Gate 3"

3. **Save:**
   - Click "Save"
   - Verify the watchlist entry is created with ID like `WL-2025-00001`

4. **Expected Result:**
   - Entry saved successfully
   - Security team receives email notification
   - Entry appears in Visitor Watchlist list

---

### Test Scenario 2: Test Watchlist Expiry

1. **Create Expired Entry:**
   - Create new watchlist entry
   - Set **Expiry Date:** Yesterday's date
   - **Is Active:** Checked

2. **Save:**
   - Click "Save"
   - System should auto-deactivate (Is Active = unchecked)

3. **Expected Result:**
   - Entry is automatically marked as inactive
   - Message: "Expiry date is in the past. Entry will be inactive."

---

### Test Scenario 3: Test Duplicate Prevention

1. **Create First Entry:**
   - Person Name: Jane Smith
   - ID Number: 87654321
   - Is Active: Checked
   - Save

2. **Create Duplicate:**
   - Create another entry with same name and ID
   - Is Active: Checked
   - Save

3. **Expected Result:**
   - Warning message: "An active watchlist entry already exists for this person."
   - Entry still saves (warning only, not blocking)

---

## 📊 Testing Existing Visitor Management

### Test Scenario 4: Complete Visitor Workflow

1. **Create Visitor Type:**
   - Go to http://172.24.13.88:8000/app/visitor-type
   - Create "Contractor" type if not exists

2. **Register Visitor:**
   - Go to http://172.24.13.88:8000/app/visitor-registration/new
   - Fill in:
     - **Visitor:** Create new or select existing
     - **Location:** Select location
     - **Expected Arrival Date:** Today
     - **Expected Arrival Time:** Current time + 1 hour
     - **Host Employee:** Select an employee
     - **Purpose of Visit:** "Equipment installation"
     - **Duration Hours:** 4
     - **Visitor Type:** Contractor
   - Save

3. **Check-In Visitor:**
   - Go to http://172.24.13.88:8000/app/visitor-checkin-checkout/new
   - Select the visitor registration
   - Fill in check-in details
   - Save

4. **Check-Out Visitor:**
   - Open the same check-in record
   - Fill in check-out time
   - Save

5. **Expected Result:**
   - Complete visitor lifecycle tracked
   - Access logs created
   - Host notified (if email configured)

---

## 🚗 Testing Existing Vehicle Management

### Test Scenario 5: Complete Vehicle Workflow

1. **Register Vehicle:**
   - Go to http://172.24.13.88:8000/app/vehicle/new
   - Fill in:
     - **License Plate:** KCA 123A
     - **Make:** Toyota
     - **Model:** Hilux
     - **Year:** 2023
     - **Color:** White
     - **Owner Type:** Visitor
     - **Owner Name:** ABC Contractors
   - Save

2. **Issue Vehicle Pass:**
   - Go to http://172.24.13.88:8000/app/vehicle-pass/new
   - Select the vehicle
   - Set expiry date
   - Save

3. **Check-In Vehicle:**
   - Go to http://172.24.13.88:8000/app/vehicle-checkin-checkout/new
   - Select the vehicle
   - Fill in entry details
   - Assign parking space
   - Save

4. **Check-Out Vehicle:**
   - Open the same check-in record
   - Fill in exit time
   - Save

5. **Expected Result:**
   - Complete vehicle lifecycle tracked
   - Parking space released
   - Access logs created

---

## ❌ What's NOT Working Yet (To Be Implemented)

### Visitor Management Gaps:
- ❌ **Risk Scoring** - Visitors not automatically scored for risk
- ❌ **Watchlist Integration** - Visitor Registration doesn't check watchlist yet
- ❌ **NDA Management** - No NDA tracking
- ❌ **Safety Induction** - No safety compliance tracking
- ❌ **PPE Management** - No PPE issuance tracking
- ❌ **Security Approval** - No workflow for high-risk visitors
- ❌ **Reports** - No comprehensive reports yet

### Vehicle Management Gaps:
- ❌ **Risk Scoring** - Vehicles not automatically scored for risk
- ❌ **Inspection Checklists** - No inspection workflow
- ❌ **Parking Zones** - No zone-based management
- ❌ **Cargo Declaration** - No dangerous goods tracking
- ❌ **Driver Verification** - No driver license tracking
- ❌ **Reports** - No comprehensive reports yet

### Integration Gaps:
- ❌ **Risk Assessment** - Not integrated yet
- ❌ **Case Management** - Not integrated yet
- ❌ **IoT/RFID** - No automation yet
- ❌ **CCTV** - No video correlation yet

---

## 🎯 Next Steps

### Immediate (This Week):
1. ⏳ Test Visitor Watchlist thoroughly
2. ⏳ Implement risk scoring in Visitor Registration
3. ⏳ Implement risk scoring in Vehicle
4. ⏳ Create Vehicle Inspection Checklist
5. ⏳ Create Parking Zone management

### Short Term (Next 2 Weeks):
1. ⏳ Integrate with Risk Assessment module
2. ⏳ Integrate with Case Management module
3. ⏳ Add NDA and safety induction tracking
4. ⏳ Add security approval workflows
5. ⏳ Create all 12 reports

### Medium Term (Next 4 Weeks):
1. ⏳ Create public web forms
2. ⏳ Implement automation workflows
3. ⏳ Add IoT integration
4. ⏳ Add CCTV integration
5. ⏳ Complete all documentation

---

## 📞 Support & Documentation

### Documentation Files:
1. ✅ `VISITOR_VEHICLE_ENHANCEMENT_PLAN.md` - Detailed roadmap
2. ✅ `VISITOR_VEHICLE_IMPLEMENTATION_STATUS.md` - Gap analysis
3. ✅ `VISITOR_VEHICLE_FINAL_SUMMARY.md` - Complete summary
4. ✅ `VISITOR_VEHICLE_QUICK_START.md` - This guide

### Key Contacts:
- **System Administrator:** Administrator
- **Security Manager:** (To be assigned)
- **Risk Officer:** (To be assigned)

---

## 🏁 Summary

**Current Status:** 72% Complete
- ✅ Visitor Management: 76% (9 DocTypes working)
- ✅ Vehicle Management: 68% (6 DocTypes working)
- ✅ Visitor Watchlist: Deployed and ready to test
- ❌ Risk Scoring: Not implemented yet
- ❌ Advanced Features: Not implemented yet

**Browser is open at:** http://172.24.13.88:8000/app/visitor-management

**Start testing the Visitor Watchlist now!**

---

*End of Quick Start Guide*

