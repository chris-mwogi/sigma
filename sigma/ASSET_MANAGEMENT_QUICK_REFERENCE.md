# Asset Management System - Quick Reference Cards

## Card 1: Common Tasks

### Creating an Asset
1. Navigate to **Asset Management** workspace
2. Click **Asset** → **New**
3. Fill in required fields:
   - Asset Name
   - Asset Category
   - Asset Location
   - Serial Number
4. Set **Lifecycle Status** and **Criticality Rating**
5. Click **Save**

### Creating a Maintenance Schedule
1. Navigate to **Asset Maintenance Schedule**
2. Click **New**
3. Select **Asset** and **Schedule Type**
4. Set **Frequency** or **Threshold**
5. Add **Checklist Items**
6. Click **Save** → **Submit**

### Creating a Work Order
1. Navigate to **Asset Work Order**
2. Click **New**
3. Select **Asset** and **Work Order Type**
4. Set **Priority** and **Schedule Dates**
5. Add **Requirements** and **Spare Parts**
6. Click **Save**

### Assigning a Work Order
1. Open the **Work Order**
2. Select **Assigned To** (technician)
3. Change **Workflow State** to **Assigned**
4. Click **Save**

### Completing a Work Order
1. Open the **Work Order**
2. Update **Checklist Items**
3. Add **Completion Notes**
4. Set **Actual End Date**
5. Change **Workflow State** to **Completed**
6. Click **Save** → **Submit**

---

## Card 2: Keyboard Shortcuts

### Global Shortcuts
- **Ctrl + K** - Quick search (Awesome Bar)
- **Ctrl + G** - Go to list
- **Ctrl + S** - Save document
- **Ctrl + Shift + S** - Save and submit
- **Esc** - Close dialog/modal

### List View Shortcuts
- **Ctrl + N** - New document
- **Ctrl + F** - Focus on search
- **Ctrl + E** - Export list
- **Ctrl + P** - Print list

### Form View Shortcuts
- **Ctrl + B** - Toggle sidebar
- **Ctrl + Shift + P** - Print document
- **Ctrl + Shift + E** - Email document
- **Ctrl + Shift + D** - Duplicate document

### Navigation Shortcuts
- **Alt + ←** - Go back
- **Alt + →** - Go forward
- **Alt + Home** - Go to home

---

## Card 3: Field Descriptions

### Asset Fields

| Field | Description | Required |
|-------|-------------|----------|
| **Asset Name** | Unique name for the asset | Yes |
| **Asset Category** | Category classification | Yes |
| **Asset Location** | Physical location | Yes |
| **Serial Number** | Manufacturer serial number | No |
| **Lifecycle Status** | Current lifecycle stage | Yes |
| **Criticality Rating** | Business criticality (Low/Medium/High/Critical) | Yes |
| **Health Score** | Current health (0-100) | Auto |
| **Health Status** | Health category (Excellent/Good/Fair/Poor/Critical) | Auto |
| **Purchase Date** | Date of purchase | No |
| **Warranty Expiry** | Warranty end date | No |
| **Total Operating Hours** | Cumulative operating hours | No |

### Work Order Fields

| Field | Description | Required |
|-------|-------------|----------|
| **Asset** | Asset being maintained | Yes |
| **Work Order Type** | Type of maintenance | Yes |
| **Priority** | Urgency level | Yes |
| **Workflow State** | Current status | Auto |
| **Scheduled Start Date** | Planned start | Yes |
| **Scheduled End Date** | Planned end | Yes |
| **Assigned To** | Technician assigned | No |
| **Estimated Duration** | Expected hours | No |
| **Actual Duration** | Actual hours taken | Auto |
| **Estimated Cost** | Budgeted cost | No |
| **Actual Cost** | Real cost incurred | No |

### Maintenance Schedule Fields

| Field | Description | Required |
|-------|-------------|----------|
| **Asset** | Asset to maintain | Yes |
| **Schedule Name** | Descriptive name | Yes |
| **Maintenance Type** | Type of maintenance | Yes |
| **Schedule Type** | Time/Usage/Condition/Predictive | Yes |
| **Frequency** | How often (for time-based) | Conditional |
| **Operating Hours Threshold** | Hours trigger (for usage-based) | Conditional |
| **Next Due Date** | Next scheduled date | Auto |
| **Schedule Status** | Current status | Auto |

---

## Card 4: Status Meanings

### Lifecycle Status
- **Planned** - Asset identified, not yet procured
- **Procurement** - Purchase in progress
- **Installation** - Being installed
- **Commissioning** - Testing and validation
- **Operational** - In active service ✅
- **Maintenance** - Under maintenance
- **Upgrade** - Being upgraded
- **Decommissioning** - Being removed from service
- **Disposal** - Disposed or sold

### Health Status
- **Excellent** (90-100) - 🟢 Optimal performance
- **Good** (70-89) - 🟡 Normal operation
- **Fair** (50-69) - 🟠 Requires attention
- **Poor** (30-49) - 🔴 Immediate action needed
- **Critical** (0-29) - ⚫ Emergency intervention

### Work Order Status (Workflow State)
- **Draft** - Initial creation
- **Scheduled** - Date and time set
- **Assigned** - Technician assigned
- **In Progress** - Work started ⚙️
- **On Hold** - Temporarily paused
- **Completed** - Work finished ✅
- **Cancelled** - Work cancelled ❌
- **Closed** - Reviewed and closed

### Priority Levels
- **Emergency** - 🔴 Immediate action (< 1 hour)
- **Critical** - 🟠 Urgent (< 4 hours)
- **High** - 🟡 Important (< 24 hours)
- **Medium** - 🔵 Normal (< 3 days)
- **Low** - 🟢 Routine (< 1 week)

### Schedule Status
- **Scheduled** - Active and on schedule
- **Due** - Due within 7 days
- **Overdue** - Past due date ⚠️
- **Completed** - Maintenance completed
- **Suspended** - Temporarily inactive

---

## Card 5: Mobile Interface

### Accessing Mobile Interface
**URL:** `http://172.24.13.88:8000/mobile/work_orders`

### Mobile Features
- ✅ View assigned work orders
- ✅ Filter by status (All/Assigned/In Progress/Scheduled)
- ✅ Start work orders
- ✅ Complete work orders
- ✅ Update checklist items
- ✅ Scan asset QR codes
- ✅ Work offline with auto-sync

### Starting a Work Order (Mobile)
1. Open work order from list
2. Tap **Start Work** button
3. Confirm start time
4. Work order status changes to **In Progress**

### Completing a Work Order (Mobile)
1. Open work order
2. Complete all checklist items
3. Add completion notes
4. Enter actual cost (if applicable)
5. Tap **Complete Work** button
6. Confirm completion

### Scanning Assets (Mobile)
1. Tap **Scan Asset** button
2. Allow camera access
3. Point camera at QR code/barcode
4. View asset details
5. Create work order if needed

### Offline Mode
- Work orders automatically cached
- Changes saved locally
- Auto-sync when connection restored
- Sync status indicator shows pending changes

---

## Card 6: Reports & Analytics

### Available Reports

| Report | Purpose | Key Metrics |
|--------|---------|-------------|
| **Asset Utilization** | Track asset usage | Operating hours, Utilization %, Downtime |
| **Maintenance Cost Analysis** | Analyze costs | Total cost, Cost by asset, Cost trends |
| **Asset Downtime** | Monitor availability | Downtime hours, MTTR, MTBF, Availability % |
| **Asset Health Dashboard** | Health overview | Health scores, Critical assets, Trends |
| **Work Order Performance** | Track efficiency | Completion rate, SLA adherence, Duration |
| **Risk Classification** | Risk distribution | Risk levels, High-risk assets, Mitigation status |
| **Vendor Performance** | Vendor tracking | SLA compliance, Response time, Ratings |

### Running a Report
1. Navigate to **Asset Management** workspace
2. Click on report name in **Reports** section
3. Set **Filters** (date range, category, location, etc.)
4. Click **Refresh** to generate
5. View results and charts

### Exporting Reports
1. Click **Export** button
2. Select format:
   - **Excel** - For data analysis
   - **PDF** - For presentations
   - **CSV** - For import to other systems
3. Download file

### Dashboard Charts
- **Asset Health Distribution** - Donut chart showing health categories
- **Work Order Status** - Pie chart showing workflow states
- **Maintenance Cost Trend** - Line chart showing monthly costs
- **Risk Classification** - Bar chart showing risk levels

---

## Card 7: Troubleshooting

### Common Issues & Solutions

**Issue:** Can't create asset
- ✅ Check if asset category exists
- ✅ Check if asset location exists
- ✅ Verify you have "Create" permission
- ✅ Ensure all required fields are filled

**Issue:** Work order not auto-assigned
- ✅ Check if technicians have "Maintenance Technician" role
- ✅ Verify technician skills match requirements
- ✅ Check if technicians are enabled
- ✅ Ensure work order is in "Scheduled" status

**Issue:** Health score not updating
- ✅ Check if asset has linked monitored device
- ✅ Verify monitored device is active
- ✅ Check if telemetry data is being received
- ✅ Wait for hourly auto-update job

**Issue:** Maintenance schedule not creating work orders
- ✅ Ensure schedule is submitted (not draft)
- ✅ Check if next due date has passed
- ✅ Verify schedule status is not "Suspended"
- ✅ Wait for daily auto-generation job

**Issue:** Mobile interface not loading
- ✅ Check internet connection
- ✅ Verify URL is correct
- ✅ Clear browser cache
- ✅ Try different browser

**Issue:** Report showing no data
- ✅ Check date range filters
- ✅ Verify data exists for selected filters
- ✅ Clear filters and try again
- ✅ Check if you have read permissions

---

## Card 8: Best Practices

### Asset Management
- ✅ Create asset categories before creating assets
- ✅ Use hierarchical locations (Site → Building → Floor → Room)
- ✅ Always enter serial numbers for trackability
- ✅ Set realistic criticality ratings
- ✅ Link IoT devices for real-time monitoring
- ✅ Keep asset data up-to-date
- ✅ Document all changes in notes

### Maintenance Planning
- ✅ Use preventive maintenance for critical assets
- ✅ Set up predictive maintenance for high-value assets
- ✅ Create detailed checklists for consistency
- ✅ Estimate durations and costs accurately
- ✅ Schedule maintenance during low-usage periods
- ✅ Track spare parts requirements
- ✅ Review and adjust schedules quarterly

### Work Order Management
- ✅ Prioritize work orders correctly
- ✅ Assign to technicians with right skills
- ✅ Start work orders on time
- ✅ Update status in real-time
- ✅ Complete checklists thoroughly
- ✅ Document all work performed
- ✅ Enter actual costs for budgeting

### Risk Management
- ✅ Conduct risk assessments for all critical assets
- ✅ Review risk register monthly
- ✅ Implement mitigation strategies for high risks
- ✅ Document all risk incidents
- ✅ Update risk levels after mitigation
- ✅ Link risks to compliance requirements

### Reporting
- ✅ Generate reports monthly
- ✅ Share insights with stakeholders
- ✅ Track KPIs consistently
- ✅ Use data for continuous improvement
- ✅ Export reports for presentations
- ✅ Archive reports for historical analysis

---

## Card 9: Contact Information

### System Access
**URL:** `http://172.24.13.88:8000`
**Mobile URL:** `http://172.24.13.88:8000/mobile/work_orders`

### Support Contacts

**System Administrator:**
- Email: admin@kplc.co.ke
- Phone: +254 XXX XXX XXX
- Available: Mon-Fri, 8:00 AM - 5:00 PM

**Technical Support:**
- Email: support@prismod.co.ke
- Phone: +254 XXX XXX XXX
- Available: 24/7 for critical issues

**Training Resources:**
- User Manual: `ASSET_MANAGEMENT_USER_GUIDE.md`
- Technical Guide: `ASSET_MANAGEMENT_TECHNICAL_GUIDE.md`
- Video Tutorials: `ASSET_MANAGEMENT_VIDEO_SCRIPTS.md`
- Training Presentation: `ASSET_MANAGEMENT_TRAINING_PRESENTATION.md`

### Emergency Procedures

**System Down:**
1. Contact technical support immediately
2. Document the issue (screenshots, error messages)
3. Use backup procedures if available

**Data Loss:**
1. Contact system administrator
2. Do not make further changes
3. Restore from latest backup

**Security Incident:**
1. Report to system administrator immediately
2. Change your password
3. Document the incident

---

**End of Quick Reference Cards**

