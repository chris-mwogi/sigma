# 🚀 Asset Management Module - Quick Start Guide

## What Was Built

A comprehensive ISO 55000/55001-compliant Asset Management system with:
- **9 DocTypes** (7 main + 2 child tables)
- **IoT Integration** with existing Unified Monitoring system
- **Predictive Maintenance** with automated work order generation
- **Risk Management** (ISO 31000)
- **Audit & Compliance** tracking

---

## 🎯 Quick Access

### Main DocTypes
```
Asset Category Sigma:     http://172.24.13.88:8000/app/asset-category-sigma
Asset Location:           http://172.24.13.88:8000/app/asset-location
Asset:                    http://172.24.13.88:8000/app/asset
Maintenance Schedule:     http://172.24.13.88:8000/app/asset-maintenance-schedule
Work Order:               http://172.24.13.88:8000/app/asset-work-order
Risk Register:            http://172.24.13.88:8000/app/asset-risk-register
Asset Audit:              http://172.24.13.88:8000/app/asset-audit
```

### Reports
```
Asset Health Dashboard:   http://172.24.13.88:8000/app/query-report/Asset%20Health%20Dashboard
```

---

## 📋 Test Data Available

### ✅ Ready to Use
- **4 Asset Categories**: Power Distribution, IT Infrastructure, Vehicles, Security
- **5 Locations**: Headquarters, Substation A, Data Center, Warehouse, Field Office
- **2 Assets**: Transformer T-001, Server SRV-001 (with full ISO 55000 data)
- **3 Maintenance Schedules**: Recurring, Condition-Based, Predictive
- **3 Work Orders**: Preventive, Corrective, Emergency

### ⏳ Pending
- Risk Register entries (DocType ready, test data needs field validation fixes)
- Audit entries (DocType ready, test data needs field validation fixes)

---

## 🔧 How to Use

### 1. Create an Asset Category
```
Navigate to: Asset Category Sigma → New
Fill in:
- Category Name: e.g., "Transformers"
- Category Code: e.g., "TRANS"
- Asset Type: e.g., "Equipment"
- Criticality Level: e.g., "Critical"
- Maintenance Strategy: e.g., "Predictive Maintenance"
- Expected Useful Life: e.g., 25 years
```

### 2. Create a Location
```
Navigate to: Asset Location → New
Fill in:
- Location Name: e.g., "Substation B"
- Location Code: e.g., "SUB-B"
- Location Type: e.g., "Site"
- GPS Coordinates: Latitude, Longitude
- Geofence: Shape (Circle/Polygon), Radius
```

### 3. Create an Asset
```
Navigate to: Asset → New
Fill in:
- Asset Name: e.g., "Transformer T-002"
- Asset Category Sigma: Select from dropdown
- Asset Location: Select from dropdown
- Criticality Rating: Low/Medium/High/Critical
- Lifecycle Status: Planned/Operational/Maintenance/etc.
- Risk Score: 0-100
- Condition Index: 0-100%
- Health Score: 0-100%
Submit the asset
```

### 4. Create a Maintenance Schedule
```
Navigate to: Asset Maintenance Schedule → New
Fill in:
- Asset: Select from dropdown
- Schedule Type: Recurring/One-Time/Condition-Based/Predictive
- Maintenance Type: Preventive/Corrective/Inspection/etc.
- Frequency: e.g., 3 Months
- Start Date: Today or future date
- For Condition-Based: Set telemetry metric and threshold
- For Predictive: Set failure probability threshold
Submit the schedule
```

### 5. Create a Work Order
```
Navigate to: Asset Work Order → New
Fill in:
- Asset: Select from dropdown
- Work Order Type: Preventive/Corrective/Emergency/etc.
- Priority: Low/Medium/High/Critical
- Scheduled Date: When work should be done
- Assigned To: Select user
- Estimated Hours: e.g., 4
- Description: What needs to be done
Submit the work order
```

### 6. Create a Risk Register Entry
```
Navigate to: Asset Risk Register → New
Fill in:
- Asset: Select from dropdown
- Risk Type: Operational/Financial/Safety/etc.
- Risk Category: Equipment Failure/Human Error/etc.
- Risk Description: Describe the risk
- Likelihood Score: 1-5 (1=Rare, 5=Almost Certain)
- Consequence Score: 1-5 (1=Insignificant, 5=Catastrophic)
- Control Effectiveness: 0-100%
- Treatment Strategy: Avoid/Mitigate/Transfer/Accept
- Treatment Owner: Select user
Submit the risk entry
```

### 7. Create an Audit
```
Navigate to: Asset Audit → New
Fill in:
- Asset: Select from dropdown
- Audit Type: Internal/External/Compliance/etc.
- Auditor: Select user
- Audit Standard: ISO 55000/ISO 14224/etc.
- Audit Scope: Describe what's being audited
- Add Audit Findings (child table):
  - Check Item: What was checked
  - Check Category: Documentation/Safety/etc.
  - Check Result: Pass/Fail/N/A/Observation
  - Severity (if Fail): Critical/Major/Minor
  - Finding Description: Details
  - Recommendation: What to do
Submit the audit
```

---

## 🤖 Automation Features

### Auto-Generated Work Orders
- **From Maintenance Schedules**: Work orders auto-created when schedule is due
- **From Monitoring Alerts**: Critical alerts auto-create emergency work orders
- **From Audits**: Critical audit findings auto-create corrective action work orders

### Auto-Calculated Fields
- **Risk Register**: Inherent Risk = Likelihood × Consequence
- **Risk Register**: Residual Risk = Inherent Risk × (1 - Control Effectiveness)
- **Audit**: Compliance % = (Passed Checks / Total Checks) × 100
- **Maintenance Schedule**: Next Due Date auto-calculated based on frequency
- **Work Order**: SLA Status auto-updated based on actual vs scheduled dates

### Auto-Updated Fields
- **Asset**: Risk Score updated from Risk Register
- **Asset**: Last Audit Date updated from Audit
- **Maintenance Schedule**: Compliance updated from Work Order completion

---

## 🔍 Integration Points

### With Unified Monitoring System
- **Asset** ↔ **Monitored Device**: Link assets to IoT devices
- **Telemetry Event** → **Condition-Based Maintenance**: Trigger schedules based on sensor data
- **Monitoring Alert** → **Work Order**: Auto-create work orders from critical alerts

### With ERPNext Core
- **Asset** ↔ **Item**: Link assets to inventory items
- **Asset** ↔ **Purchase Receipt**: Track asset procurement
- **Maintenance Schedule** ↔ **Maintenance Visit**: Track maintenance execution

---

## 📊 Key Metrics Tracked

### Asset Health
- Condition Index (0-100%)
- Health Score (0-100%)
- Performance Rating (0-100%)
- Risk Score (0-100)

### Maintenance
- MTBF (Mean Time Between Failures) - hours
- MTTR (Mean Time To Repair) - hours
- Schedule Compliance (%)
- Overdue Maintenance Count

### Risk
- Inherent Risk Score (1-25)
- Residual Risk Score (calculated)
- Risk Level (Low/Medium/High/Very High)

### Compliance
- Audit Compliance (%)
- ISO 55000 Compliance Status
- ISO 14224 Compliance Status
- NIST Compliance Status
- Regulatory Compliance Status

---

## 🎓 Best Practices

1. **Always set Asset Category and Location** before creating assets
2. **Use Criticality Rating** to prioritize maintenance and risk management
3. **Link assets to Monitored Devices** for IoT integration
4. **Set up Recurring Maintenance Schedules** for critical assets
5. **Use Condition-Based Schedules** for assets with IoT sensors
6. **Document all risks** in Risk Register with proper treatment plans
7. **Conduct regular audits** and track corrective actions
8. **Review Work Order SLA compliance** to optimize maintenance planning

---

## 🆘 Troubleshooting

### Issue: Can't create Asset
- **Solution**: Ensure Asset Category Sigma and Asset Location are created first

### Issue: Maintenance Schedule not generating Work Orders
- **Solution**: Check that schedule is submitted and next_due_date is in the past

### Issue: Condition-Based Schedule not triggering
- **Solution**: Verify asset is linked to Monitored Device and telemetry metric name is correct

### Issue: Risk calculations not working
- **Solution**: Ensure Likelihood Score and Consequence Score are filled in (1-5)

### Issue: Audit compliance not calculating
- **Solution**: Ensure audit findings have Check Result filled in (Pass/Fail/N/A/Observation)

---

## 📞 Support

For issues or questions:
1. Check the comprehensive documentation: `ASSET_MANAGEMENT_COMPLETE_SUMMARY.md`
2. Review the implementation details: `ASSET_MANAGEMENT_IMPLEMENTATION_SUMMARY.md`
3. Check the Phase 2-4 completion summary: `ASSET_MANAGEMENT_PHASE_2_4_COMPLETE.md`

---

**Last Updated**: 2025-11-19  
**Version**: 1.0 (Phases 2-5 Complete)

