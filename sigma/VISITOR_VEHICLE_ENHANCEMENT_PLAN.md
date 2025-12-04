# Visitor & Vehicle Management Modules - Enhancement Plan

## 📋 Executive Summary

Both **Visitor Management** and **Vehicle Management** modules already exist in the Sigma ERPNext system. This document outlines the enhancements needed to align them with international standards (ISO 27001, ISO 45001, ISO 31000, OSHA, DHS/CBP, IEC) and integrate them with Risk Assessment and Case Management modules.

**Implementation Date:** November 18, 2025  
**Modules:** Sigma Visitor Management, Sigma Vehicle Management  
**Integration Targets:** Risk Assessment, Case Management, Security Operations, Asset Tracking

---

## ✅ EXISTING IMPLEMENTATION STATUS

### Visitor Management Module (EXISTING)
**Location:** `apps/sigma/sigma/sigma_visitor_management/`

**Existing DocTypes (8):**
1. ✅ Visitor (Master)
2. ✅ Visitor Type (Master)
3. ✅ Visitor Registration
4. ✅ Visitor Required Document (Child Table)
5. ✅ Visitor Badge
6. ✅ Visitor Checkin Checkout
7. ✅ Visitor Access Log
8. ✅ Inter Station Staff Visit
9. ✅ VMS Event

**Existing Features:**
- Basic visitor registration
- Host employee linking
- Location-based access
- Badge management
- Check-in/check-out tracking
- Access logging

**Existing Workspace:**
- Visitor Management workspace with number cards

---

### Vehicle Management Module (EXISTING)
**Location:** `apps/sigma/sigma/sigma_vehicle_management/`

**Existing DocTypes (6):**
1. ✅ Vehicle (Master)
2. ✅ Vehicle Registration
3. ✅ Vehicle Pass
4. ✅ Vehicle Checkin Checkout
5. ✅ Vehicle Access Log
6. ✅ Parking Space

**Existing Features:**
- Vehicle registration (license plate, make, model)
- Owner tracking (company/personal)
- Parking space management
- Check-in/check-out tracking
- Access logging
- Vehicle pass management

**Existing Workspace:**
- Vehicle Management workspace with number cards

---

## 🎯 REQUIRED ENHANCEMENTS

### Phase 1: Standards Compliance Enhancements

#### A. Visitor Management Enhancements

**1. ISO 27001 A.6 & A.11 Compliance (Physical Access Control)**
- ✅ Already has: Visitor Type, Access Levels
- ❌ Missing: Risk-based access control
- ❌ Missing: Watchlist checking
- ❌ Missing: NDA management
- ❌ Missing: Document verification workflow

**Required Additions:**
- Add `Visitor Watchlist` DocType
- Add risk scoring algorithm to Visitor Registration
- Add NDA document management
- Add document verification workflow
- Add security approval workflow for high-risk visitors

**2. ISO 31000 Risk Management**
- ❌ Missing: Automated risk scoring
- ❌ Missing: Risk band classification (Low/Medium/High)
- ❌ Missing: Integration with Risk Assessment module

**Required Additions:**
- Add risk_score and risk_band fields to Visitor Registration
- Implement calculate_risk_score() method
- Link to Risk Assessment module
- Auto-escalation for high-risk visitors

**3. ISO 45001 Safety Management**
- ❌ Missing: Safety induction tracking
- ❌ Missing: PPE requirements management
- ❌ Missing: Contractor compliance tracking

**Required Additions:**
- Add safety_induction_completed field
- Add PPE issuance tracking
- Add contractor certificate management
- Link to incident management

**4. DHS/CBP Visitor Management Guidelines**
- ❌ Missing: Pre-registration workflow
- ❌ Missing: Identity verification
- ❌ Missing: Escort management
- ❌ Missing: Exit verification

**Required Additions:**
- Add pre-registration web form
- Add ID document upload and verification
- Add escort assignment and tracking
- Add mandatory exit process

**5. GDPR/Privacy Compliance**
- ❌ Missing: Data retention policy
- ❌ Missing: Consent management
- ❌ Missing: Data anonymization

**Required Additions:**
- Add data_retention_days field
- Add consent_given checkbox
- Add anonymization script for old records

---

#### B. Vehicle Management Enhancements

**1. ISO 39001 Road Traffic Safety**
- ❌ Missing: Vehicle inspection checklists
- ❌ Missing: Safety compliance tracking
- ❌ Missing: Driver verification

**Required Additions:**
- Add `Vehicle Inspection Checklist` DocType
- Add `Vehicle Inspection Template` DocType
- Add driver_id and driver_license fields
- Add inspection_status field

**2. ISO 27001 A.11 Physical Security**
- ❌ Missing: Risk-based vehicle access
- ❌ Missing: Cargo declaration
- ❌ Missing: Security inspection workflow

**Required Additions:**
- Add risk_score and risk_band to Vehicle
- Add cargo_declaration field to Vehicle Entry Log
- Add security_inspection_required checkbox
- Add inspection checklist to entry/exit

**3. FTA Vehicle Access Management**
- ❌ Missing: Zone-based access control
- ❌ Missing: Temporary pass management
- ❌ Missing: Parking bay allocation

**Required Additions:**
- Add `Parking Zone` DocType with capacity tracking
- Add allowed_access_zones to Vehicle
- Add temporary_pass_expiry to Vehicle Pass
- Add auto-allocation algorithm for parking bays

**4. OSHA Transport Safety**
- ❌ Missing: Vehicle safety equipment tracking
- ❌ Missing: Dangerous goods declaration
- ❌ Missing: Emergency equipment verification

**Required Additions:**
- Add safety_equipment_checklist to Vehicle
- Add dangerous_goods_declaration to Vehicle Entry Log
- Add fire_extinguisher_valid, first_aid_kit_valid fields
- Add emergency_contact field

**5. IoT/Telemetry Integration**
- ❌ Missing: GPS tracking integration
- ❌ Missing: Sensor-based parking management
- ❌ Missing: Automated gate control

**Required Additions:**
- Add gps_device_id to Vehicle
- Add sensor_id to Parking Space
- Add gate_controller_id to Vehicle Entry Log
- Add API endpoints for IoT integration

---

### Phase 2: Integration Enhancements

#### A. Risk Assessment Module Integration

**Visitor Risk Scoring:**
```python
risk_score = (visitor_type_weight * 10) + 
             (watchlist_flag * 30) + 
             (first_time_visitor * 10) + 
             (sensitive_area_access * 20) + 
             (unknown_company * 15)

if risk_score >= 60: risk_band = "High"
elif risk_score >= 40: risk_band = "Medium"
else: risk_band = "Low"
```

**Vehicle Risk Scoring:**
```python
risk_score = (vehicle_type_weight * 10) + 
             (unknown_driver * 20) + 
             (cargo_declared * 15) + 
             (restricted_zone_access * 25) + 
             (inspection_failed * 30)

if risk_score >= 60: risk_band = "High"
elif risk_score >= 40: risk_band = "Medium"
else: risk_band = "Low"
```

**Integration Points:**
- Auto-create Risk Assessment record for high-risk visitors/vehicles
- Link visitor/vehicle incidents to Case Management
- Trigger security alerts for risk threshold breaches

---

#### B. Case Management Module Integration

**Automatic Case Creation:**
- Visitor security violation → Create Case
- Vehicle inspection failure → Create Case
- Watchlist match → Create Case
- Unauthorized access attempt → Create Case

**Integration Fields:**
- Add case_id link field to Visitor Registration
- Add case_id link field to Vehicle Entry Log
- Add incident_type field
- Add auto_create_case checkbox in settings

---

#### C. Security Operations Integration

**Access Control Integration:**
- RFID badge issuance and deactivation
- Biometric enrollment (optional)
- Gate automation (open/close based on approval)
- Real-time access logging

**CCTV Integration:**
- Link visitor/vehicle entry to CCTV footage
- Add camera_id field to entry logs
- Add snapshot_url field for facial recognition

**Guard Tour Integration:**
- Link guard patrols to visitor/vehicle checks
- Add guard_id to check-in/check-out records
- Add patrol_checkpoint_id field

---

### Phase 3: Automation & Workflows

#### A. Visitor Management Automation

**1. Pre-Registration Workflow:**
```
Visitor submits web form → Host receives email → Host approves → 
Security reviews (if high-risk) → Security approves → 
QR code generated → Visitor receives email with QR code
```

**2. Check-In Workflow:**
```
Visitor scans QR at kiosk → System verifies registration → 
Checks watchlist → Verifies documents → Issues badge → 
Notifies host → Logs entry → Activates RFID (if applicable)
```

**3. Check-Out Workflow:**
```
Visitor scans badge → System verifies → Deactivates RFID → 
Collects badge → Logs exit → Notifies host → 
Closes visit record → Archives data (GDPR compliance)
```

**4. SLA Monitoring:**
- Alert if visitor overstays expected duration
- Auto-escalate to security after 2 hours overdue
- Send reminder to host 30 minutes before expected exit

---

#### B. Vehicle Management Automation

**1. Pre-Registration Workflow:**
```
Driver submits vehicle details → System checks vehicle database → 
Assigns parking bay → Generates temporary pass → 
Sends pass to driver email/SMS
```

**2. Entry Workflow:**
```
Vehicle arrives at gate → Guard scans QR/plate → 
System verifies registration → Runs inspection checklist → 
Checks cargo declaration → Issues vehicle pass → 
Opens gate (if automated) → Logs entry → 
Sends parking bay directions
```

**3. Exit Workflow:**
```
Vehicle arrives at exit gate → Guard scans pass → 
System verifies → Runs exit inspection → 
Closes movement record → Deactivates pass → 
Opens gate → Logs exit → Updates parking availability
```

**4. Parking Management:**
- Real-time parking bay availability
- Auto-allocation based on vehicle type and visitor priority
- Sensor-based occupancy detection (IoT integration)
- Overstay alerts

---

### Phase 4: Reporting & Analytics

**Required Reports (12 total):**

**Visitor Management Reports (6):**
1. Daily Visitor Summary (by location, type, risk band)
2. Visitor Aging Report (overstays, SLA breaches)
3. High-Risk Visitor Matrix (watchlist, risk scores)
4. Host Performance Report (approval times, visitor counts)
5. Visitor Compliance Report (NDA, safety induction, documents)
6. Visitor Trend Analysis (monthly trends, peak times)

**Vehicle Management Reports (6):**
1. Daily Vehicle Movement Report (entries, exits, on-site)
2. Vehicle Inspection Compliance Report (pass/fail rates)
3. Parking Utilization Report (occupancy, turnover)
4. High-Risk Vehicle Matrix (risk scores, violations)
5. Vehicle Incident Report (accidents, violations, damages)
6. Contractor Vehicle Compliance (insurance, certifications)

---

### Phase 5: Web Forms & Portals

**Required Web Forms (4):**
1. **Visitor Pre-Registration Form**
   - Public-facing form for visitor self-registration
   - Fields: Name, Company, ID, Purpose, Host, Visit Date
   - Auto-email to host for approval

2. **Vehicle Pre-Registration Form**
   - Driver submits vehicle details in advance
   - Fields: Plate, Make, Model, Driver, Purpose, Visit Date
   - Auto-generate temporary pass

3. **Contractor Compliance Form**
   - Upload insurance, safety certificates, licenses
   - Auto-verification workflow
   - Expiry tracking and alerts

4. **Visitor Feedback Form**
   - Post-visit feedback collection
   - Security experience rating
   - Suggestions for improvement

---

## 📊 IMPLEMENTATION PRIORITY

### Priority 1 (Critical - Week 1)
- ✅ Add Visitor Watchlist DocType
- ✅ Implement risk scoring algorithms
- ✅ Add NDA management
- ✅ Add Vehicle Inspection Checklist DocType
- ✅ Add Parking Zone DocType
- ✅ Integrate with Risk Assessment module
- ✅ Integrate with Case Management module

### Priority 2 (High - Week 2)
- ✅ Create all 12 reports
- ✅ Implement automation workflows
- ✅ Add safety induction tracking
- ✅ Add PPE management
- ✅ Add cargo declaration
- ✅ Add security inspection workflows

### Priority 3 (Medium - Week 3)
- ✅ Create web forms
- ✅ Implement IoT integration APIs
- ✅ Add CCTV integration
- ✅ Add RFID/biometric integration
- ✅ Implement GDPR compliance features

### Priority 4 (Low - Week 4)
- ✅ Advanced analytics dashboards
- ✅ Mobile app integration
- ✅ Facial recognition integration
- ✅ License plate recognition (ANPR)
- ✅ Predictive analytics for parking

---

## 🎯 SUCCESS CRITERIA

✅ **Functional Requirements:**
- Complete visitor lifecycle management (pre-reg → entry → exit)
- Complete vehicle lifecycle management (pre-reg → entry → exit → parking)
- Risk-based access control
- Automated compliance checking
- Integration with Risk Assessment and Case Management

✅ **Standards Compliance:**
- ISO 27001 (Physical Access Control)
- ISO 45001 (Safety Management)
- ISO 31000 (Risk Management)
- ISO 39001 (Road Traffic Safety)
- OSHA (Workplace Safety)
- DHS/CBP (Visitor Management)
- GDPR (Data Privacy)

✅ **Technical Requirements:**
- Auto-calculations and validations
- Workflow automation
- Real-time monitoring
- IoT integration readiness
- Mobile-friendly interfaces

✅ **User Experience:**
- Intuitive web forms
- QR code-based check-in
- Real-time notifications
- Comprehensive reporting
- Dashboard analytics

---

## 📞 Next Steps

1. **Review existing implementation** - Audit current DocTypes and features
2. **Prioritize enhancements** - Focus on Priority 1 items first
3. **Create missing DocTypes** - Watchlist, Inspection Checklist, Parking Zone
4. **Implement risk scoring** - Add algorithms to existing DocTypes
5. **Build integrations** - Connect to Risk Assessment and Case Management
6. **Create reports** - All 12 reports with filters and charts
7. **Build web forms** - Public-facing registration forms
8. **Test thoroughly** - Browser testing with real scenarios
9. **Document everything** - User guides and admin documentation
10. **Train users** - Security guards, hosts, administrators

---

*End of Enhancement Plan*

