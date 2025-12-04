# Asset Management System - Training Presentation
## ISO 55000/55001 Compliant Asset Management for KPLC

---

## Slide 1: Welcome & Introduction

### Asset Management System Training
**ISO 55000/55001 Compliant Solution**

**Objectives:**
- Understand the Asset Management System architecture
- Learn how to manage assets throughout their lifecycle
- Master work order and maintenance scheduling
- Utilize IoT monitoring and predictive maintenance
- Generate reports and analytics

**Duration:** 2 hours

---

## Slide 2: System Overview

### What is Asset Management?

Asset Management is the **coordinated activity of an organization to realize value from assets** throughout their lifecycle.

**Key Benefits:**
- ✅ Improved asset reliability and performance
- ✅ Reduced maintenance costs
- ✅ Extended asset lifespan
- ✅ Better compliance with regulations
- ✅ Data-driven decision making

**Standards Compliance:**
- ISO 55000/55001 (Asset Management)
- ISO 31000 (Risk Management)
- ISO 14224 (Reliability Data)
- ITIL4 (Service Management)

---

## Slide 3: System Architecture

### Module Structure

```
Asset Management System
├── Asset Registry (Master Data)
├── Asset Categories & Locations
├── Maintenance Management
│   ├── Maintenance Schedules
│   ├── Work Orders
│   └── Spare Parts
├── IoT & Monitoring Integration
│   ├── Monitored Devices
│   ├── Telemetry Events
│   └── Monitoring Alerts
├── Risk & Compliance
│   ├── Risk Register
│   ├── Audits & Inspections
│   └── Compliance Tracking
├── Vendor Management
│   ├── Vendor Profiles
│   ├── SLA Contracts
│   └── Performance Tracking
└── Reports & Analytics
```

---

## Slide 4: Asset Lifecycle

### ISO 55000 Asset Lifecycle Stages

1. **Planned** - Asset identified and budgeted
2. **Procurement** - Purchase order created
3. **Installation** - Physical installation in progress
4. **Commissioning** - Testing and validation
5. **Operational** - In active service
6. **Maintenance** - Scheduled or corrective maintenance
7. **Upgrade** - Enhancement or modernization
8. **Decommissioning** - Removal from service
9. **Disposal** - Final disposal or sale

**Each stage has specific workflows and requirements**

---

## Slide 5: Asset Categories

### Hierarchical Asset Classification

**Asset Types:**
- IT Equipment (Servers, Network Devices, Workstations)
- Facilities (Buildings, HVAC, Electrical Systems)
- Vehicles (Fleet Management)
- Security Systems (CCTV, Access Control)
- Industrial Equipment (Generators, Transformers)

**Category Configuration:**
- Maintenance strategies (Preventive, Predictive, Corrective)
- MTBF (Mean Time Between Failures)
- Depreciation templates
- Risk classification
- IoT/Network monitoring flags

---

## Slide 6: Asset Locations

### Hierarchical Location Structure

**Location Hierarchy:**
```
Site (e.g., KPLC Head Office)
└── Building (e.g., Main Building)
    └── Floor (e.g., 3rd Floor)
        └── Room (e.g., Server Room 301)
```

**Location Features:**
- GPS coordinates for mapping
- Geofencing capabilities
- Capacity tracking
- Environmental conditions
- Access control integration

---

## Slide 7: Creating an Asset

### Step-by-Step Asset Creation

**Required Information:**
1. **Basic Details**
   - Asset Name
   - Serial Number
   - Asset Category
   - Location

2. **Lifecycle Information**
   - Lifecycle Status
   - Purchase Date
   - Warranty Expiry
   - Criticality Rating

3. **Technical Details**
   - Manufacturer & Model
   - Specifications
   - Operating Hours
   - Health Score

4. **Financial Information**
   - Purchase Cost
   - Depreciation Method
   - Current Value

**Demo:** Creating a network switch asset

---

## Slide 8: Asset Health Monitoring

### Real-Time Health Tracking

**Health Score Calculation:**
- Based on telemetry data from IoT devices
- Ranges from 0-100
- Auto-updated hourly

**Health Status Categories:**
- 🟢 **Excellent** (90-100): Optimal performance
- 🟡 **Good** (70-89): Normal operation
- 🟠 **Fair** (50-69): Requires attention
- 🔴 **Poor** (30-49): Immediate action needed
- ⚫ **Critical** (0-29): Emergency intervention

**Integration with Monitoring Alerts:**
- Critical alerts auto-create work orders
- Health trends trigger predictive maintenance

---

## Slide 9: Maintenance Schedules

### Proactive Maintenance Planning

**Schedule Types:**
1. **Time-Based** - Fixed intervals (daily, weekly, monthly)
2. **Usage-Based** - Operating hours threshold
3. **Condition-Based** - Sensor thresholds
4. **Predictive** - MTBF and failure probability

**Schedule Configuration:**
- Maintenance type (Preventive, Corrective, Predictive)
- Frequency and next due date
- Required skills and tools
- Estimated duration and cost
- Spare parts requirements

**Auto-Generation:**
- System automatically creates schedules for operational assets
- Runs daily via scheduled job

---

## Slide 10: Work Orders

### Maintenance Execution

**Work Order Workflow:**
```
Draft → Scheduled → Assigned → In Progress → Completed → Closed
```

**Work Order Types:**
- Preventive Maintenance
- Corrective Maintenance
- Predictive Maintenance
- Condition-Based Maintenance
- Emergency Repair

**Priority Levels:**
- Emergency (Red)
- Critical (Orange)
- High (Yellow)
- Medium (Blue)
- Low (Green)

**Auto-Assignment:**
- Intelligent technician matching based on skills, workload, location

---

## Slide 11: Mobile Interface

### Field Technician App

**Mobile Features:**
- 📱 View assigned work orders
- 📷 Scan asset QR codes
- ✅ Update work order status
- 📝 Complete checklists
- 💾 Offline mode with auto-sync

**Accessing Mobile Interface:**
- URL: `http://172.24.13.88:8000/mobile/work_orders`
- Optimized for smartphones and tablets
- Works offline with automatic synchronization

**Demo:** Mobile work order management

---

## Slide 12: IoT Integration

### Unified Monitoring System

**Monitored Device Types:**
- Network devices (SNMP)
- IoT sensors (MQTT, HTTP)
- CCTV cameras (ONVIF)
- Environmental sensors
- Power systems

**Telemetry Data:**
- Real-time metrics (CPU, memory, temperature, voltage)
- Historical trends
- Threshold-based alerting

**Alert Escalation:**
- Critical alerts → Auto-create work orders
- High alerts → Notify maintenance team
- Medium/Low alerts → Log for review

---

## Slide 13: Risk Management

### Asset Risk Assessment

**Risk Register:**
- Inherent risk level (1-25 scale)
- Residual risk level (after controls)
- Risk types (Operational, Financial, Safety, Cybersecurity)
- Mitigation strategies

**Risk Calculation:**
```
Risk Score = Likelihood × Impact
```

**Risk Levels:**
- Low (1-5): Accept
- Medium (6-12): Monitor
- High (13-20): Mitigate
- Very High (21-25): Urgent action

**Integration:**
- High-risk assets flagged in dashboard
- Automatic risk assessment triggers

---

## Slide 14: Vendor Management

### Service Provider Tracking

**Vendor Profile:**
- Contact information
- Certifications and compliance
- Insurance coverage
- Performance ratings

**SLA Contracts:**
- Service level agreements
- Response time commitments
- KPI tracking
- Contract renewal alerts

**SLA KPIs:**
- Response time adherence
- Resolution time
- First-time fix rate
- Customer satisfaction

**Automation:**
- Auto-check vendor compliance daily
- Contract expiry notifications
- Performance score calculation

---

## Slide 15: Reports & Analytics

### Data-Driven Decision Making

**Available Reports:**
1. **Asset Utilization Report** - Usage patterns and efficiency
2. **Maintenance Cost Analysis** - Cost breakdown by asset/category
3. **Asset Downtime Report** - Availability and MTTR analysis
4. **Asset Health Dashboard** - Real-time health overview
5. **Work Order Performance** - Completion rates and SLA adherence
6. **Risk Classification** - Risk distribution across assets
7. **Vendor Performance** - SLA compliance and ratings

**Dashboard Charts:**
- Asset Health Distribution (Donut)
- Work Order Status (Pie)
- Maintenance Cost Trend (Line)
- Risk Classification (Bar)

**Number Cards:**
- Total Assets, Critical Assets, Maintenance Due, Open Work Orders, Avg Health

---

## Slide 16: Advanced Automation

### Intelligent Features

**Predictive Maintenance:**
- Failure probability calculation
- MTBF-based predictions
- Auto-generate maintenance alerts

**Spare Parts Auto-Reorder:**
- Dynamic reorder point calculation
- Automatic purchase requests
- Inventory optimization

**Intelligent Work Order Assignment:**
- Skills matching
- Workload balancing
- Location proximity
- Performance history

**All automation runs automatically via scheduled jobs**

---

## Slide 17: Best Practices

### Tips for Success

**Asset Management:**
- ✅ Keep asset data up-to-date
- ✅ Regularly review health scores
- ✅ Maintain accurate location information
- ✅ Document all maintenance activities

**Maintenance Planning:**
- ✅ Schedule preventive maintenance proactively
- ✅ Track spare parts inventory
- ✅ Monitor SLA compliance
- ✅ Use mobile app for field work

**Risk Management:**
- ✅ Conduct regular risk assessments
- ✅ Prioritize high-risk assets
- ✅ Document mitigation strategies
- ✅ Review risk register quarterly

**Reporting:**
- ✅ Generate reports monthly
- ✅ Share insights with stakeholders
- ✅ Track KPIs consistently
- ✅ Use data for continuous improvement

---

## Slide 18: Q&A and Next Steps

### Questions & Answers

**Common Questions:**
- How do I create my first asset?
- How do I assign work orders to technicians?
- How do I access the mobile interface?
- How do I generate reports?
- How do I set up IoT monitoring?

**Next Steps:**
1. Practice creating assets in the system
2. Set up maintenance schedules
3. Create and complete work orders
4. Generate your first report
5. Explore mobile interface

**Support Resources:**
- User Manual: `ASSET_MANAGEMENT_USER_GUIDE.md`
- Technical Guide: `ASSET_MANAGEMENT_TECHNICAL_GUIDE.md`
- Quick Reference: `ASSET_MANAGEMENT_QUICK_REFERENCE.md`

---

## Slide 19: Thank You

### Contact Information

**System Administrator:**
- Email: admin@kplc.co.ke
- Phone: +254 XXX XXX XXX

**Technical Support:**
- Email: support@prismod.co.ke
- Phone: +254 XXX XXX XXX

**Training Resources:**
- Video Tutorials: Available on internal portal
- Documentation: `/apps/sigma/sigma/` directory
- Practice Environment: http://172.24.13.88:8000

**Remember:** Asset Management is a continuous improvement process!

---

**End of Presentation**

