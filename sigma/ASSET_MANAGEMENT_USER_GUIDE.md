# Asset Management Module - User Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Managing Assets](#managing-assets)
4. [Maintenance Management](#maintenance-management)
5. [Work Orders](#work-orders)
6. [Risk Management](#risk-management)
7. [Vendor Management](#vendor-management)
8. [Reports & Analytics](#reports--analytics)
9. [Best Practices](#best-practices)

---

## 1. Introduction

The Asset Management module helps you manage your organization's assets throughout their lifecycle, from acquisition to disposal. It follows ISO 55000 standards and integrates with the Unified Monitoring system for real-time asset health tracking.

### Key Features
- **Asset Lifecycle Management**: Track assets from planning to disposal
- **Maintenance Scheduling**: Preventive, predictive, and condition-based maintenance
- **Work Order Management**: Create and track maintenance work orders
- **Risk Management**: ISO 31000-compliant risk assessment
- **Vendor Management**: Track vendors and SLA contracts
- **Real-time Monitoring**: Integration with IoT devices and telemetry
- **Compliance Tracking**: ISO 55000, ISO 14224, NIST compliance

---

## 2. Getting Started

### Accessing the Module

1. Log in to Sigma ERP
2. Navigate to the **Asset Management** workspace
3. You'll see tiles for:
   - Assets
   - Maintenance Schedules
   - Work Orders
   - Risk Registers
   - Audits
   - Vendors
   - Reports

### Initial Setup

Before creating assets, set up:

1. **Asset Categories** (`/app/asset-category-sigma`)
   - Define categories like "IT Infrastructure", "Power Distribution", "Vehicles"
   - Set maintenance strategies and expected useful life

2. **Asset Locations** (`/app/asset-location`)
   - Create hierarchical locations (e.g., "Nairobi HQ" > "Building A" > "Floor 3")
   - Add GPS coordinates if needed

3. **Vendors** (`/app/asset-vendor`)
   - Add vendors who supply or maintain assets
   - Track certifications and performance metrics

---

## 3. Managing Assets

### Creating a New Asset

1. Go to **Asset List** (`/app/asset`)
2. Click **New**
3. Fill in required fields:
   - **Asset Name**: Descriptive name (e.g., "Server - DC-01")
   - **Asset Category**: Select from dropdown
   - **Asset Location**: Select location
   - **Lifecycle Status**: Current status (Planned, Operational, etc.)
   - **Criticality Rating**: Low, Medium, High, or Critical

4. Fill in ISO 55000 compliance fields:
   - **Commissioning Date**: When asset was put into service
   - **Expected End of Life**: Estimated disposal date
   - **Condition Index**: Current condition (0-100%)
   - **Health Score**: Overall health (0-100%)

5. Click **Save** and then **Submit**

### Viewing Asset Details

- **Overview Tab**: Basic information and status
- **Maintenance Tab**: Linked maintenance schedules and work orders
- **Risk Tab**: Associated risks and audits
- **Monitoring Tab**: Real-time telemetry data (if monitored device linked)
- **Compliance Tab**: ISO compliance status

### Asset Lifecycle Statuses

- **Planned**: Asset planned but not yet acquired
- **Procurement**: In procurement process
- **Installation**: Being installed
- **Commissioning**: Being commissioned
- **Operational**: In active use
- **Maintenance**: Under maintenance
- **Upgrade**: Being upgraded
- **Decommissioning**: Being decommissioned
- **Disposal**: Disposed

---

## 4. Maintenance Management

### Creating a Maintenance Schedule

1. Go to **Asset Maintenance Schedule** (`/app/asset-maintenance-schedule`)
2. Click **New**
3. Fill in:
   - **Asset**: Select asset
   - **Maintenance Type**: Preventive, Predictive, or Condition-Based
   - **Frequency**: Daily, Weekly, Monthly, Quarterly, Annually
   - **Start Date**: When schedule begins
   - **Estimated Duration**: Hours required
   - **Estimated Cost**: Expected cost

4. Click **Save** and **Submit**

### Maintenance Types

- **Preventive Maintenance**: Scheduled maintenance at regular intervals
- **Predictive Maintenance**: Based on MTBF and condition monitoring
- **Condition-Based Maintenance**: Triggered by condition thresholds
- **Corrective Maintenance**: Reactive maintenance after failure

### Viewing Maintenance Due

Use the **Maintenance Due Report** to see:
- Upcoming maintenance schedules
- Overdue maintenance
- Maintenance due this week/month
- Total estimated costs

---

## 5. Work Orders

### Creating a Work Order

1. Go to **Asset Work Order** (`/app/asset-work-order`)
2. Click **New**
3. Fill in:
   - **Asset**: Select asset
   - **Work Order Type**: Preventive, Corrective, Inspection, etc.
   - **Priority**: Low, Medium, High, Critical
   - **Description**: Detailed description of work
   - **Scheduled Start/End Date**: When work should be done
   - **Assigned To**: Technician or team

4. Click **Save**

### Work Order Workflow

1. **Open**: Work order created
2. **Assigned**: Assigned to technician
3. **In Progress**: Work started
4. **On Hold**: Temporarily paused
5. **Completed**: Work finished
6. **Cancelled**: Work order cancelled

### Tracking SLA Compliance

- Link work orders to **SLA Contracts**
- System automatically tracks:
  - Response time
  - Resolution time
  - SLA compliance status

---

## 6. Risk Management

### Creating a Risk Register

1. Go to **Asset Risk Register** (`/app/asset-risk-register`)
2. Click **New**
3. Fill in:
   - **Asset**: Select asset
   - **Risk Title**: Brief description
   - **Risk Category**: Operational, Financial, Safety, etc.
   - **Likelihood Score**: 1-5 (Rare to Almost Certain)
   - **Consequence Score**: 1-5 (Insignificant to Catastrophic)
   - **Risk Treatment Strategy**: Avoid, Mitigate, Transfer, Accept
   - **Control Measures**: What controls are in place
   - **Control Effectiveness**: 0-100%

4. System automatically calculates:
   - **Inherent Risk Score**: Likelihood × Consequence
   - **Residual Risk Score**: After controls applied
   - **Risk Classification**: Low, Medium, High, Very High

5. Click **Save** and **Submit**

### Conducting Audits

1. Go to **Asset Audit** (`/app/asset-audit`)
2. Click **New**
3. Fill in audit details and add findings
4. System calculates compliance percentage
5. Submit audit report

---

## 7. Vendor Management

### Managing Vendors

1. Go to **Asset Vendor** (`/app/asset-vendor`)
2. Add vendor information:
   - Contact details
   - Certifications (ISO 9001, ISO 14001, etc.)
   - Insurance coverage
   - Performance metrics

### Creating SLA Contracts

1. Go to **SLA Contract** (`/app/sla-contract`)
2. Click **New**
3. Fill in contract details:
   - Vendor
   - Contract dates
   - Scope of work
   - Financial terms
   - SLA terms (response time, resolution time, availability)

4. Add **SLA KPIs** in child table:
   - KPI name and category
   - Target value
   - Measurement frequency

5. Submit contract

### Tracking Vendor Performance

Use the **Vendor Performance Report** to monitor:
- Vendor ratings
- On-time delivery rates
- Quality ratings
- Response times
- Defect rates

---

## 8. Reports & Analytics

### Available Reports

1. **Maintenance Due Report**
   - Upcoming and overdue maintenance
   - Filters: Asset, Category, Location, Criticality
   - Charts: Status distribution

2. **Asset Lifecycle Report**
   - Asset age and remaining life
   - End-of-life predictions
   - Filters: Category, Location, Lifecycle Status

3. **Asset Criticality Matrix**
   - Assets by criticality and risk
   - Risk classification distribution
   - Filters: Criticality, Risk Classification

4. **Compliance Status Report**
   - ISO 55000, ISO 14224, NIST compliance
   - Last audit dates
   - Certification status

5. **Vendor Performance Report**
   - Vendor ratings and metrics
   - Contract compliance
   - Filters: Vendor Status, Vendor Type

### Running Reports

1. Navigate to report URL
2. Set filters as needed
3. Click **Refresh**
4. Export to Excel/PDF if needed

---

## 9. Best Practices

### Asset Management
- ✅ Keep asset information up-to-date
- ✅ Regularly update condition index and health scores
- ✅ Link assets to monitored devices for real-time tracking
- ✅ Review and update lifecycle status regularly

### Maintenance
- ✅ Create maintenance schedules for all critical assets
- ✅ Use preventive maintenance to reduce failures
- ✅ Track actual vs. estimated costs
- ✅ Review maintenance history before planning work

### Risk Management
- ✅ Conduct regular risk assessments
- ✅ Update risk registers when conditions change
- ✅ Implement and track control measures
- ✅ Review residual risks quarterly

### Vendor Management
- ✅ Keep vendor certifications up-to-date
- ✅ Monitor SLA compliance regularly
- ✅ Update KPI actual values monthly
- ✅ Review vendor performance quarterly

---

## 📞 Need Help?

- **Documentation**: See ASSET_MANAGEMENT_QUICK_START.md
- **Support**: info@prismod.co.ke
- **Training**: Contact your system administrator

---

**Version**: 1.0  
**Last Updated**: November 19, 2025

