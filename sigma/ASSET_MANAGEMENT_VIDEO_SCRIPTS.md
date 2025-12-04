# Asset Management System - Video Tutorial Scripts

## Video 1: Getting Started with Asset Management (10 minutes)

### Script

**[INTRO - 0:00-0:30]**

"Welcome to the Asset Management System training series. I'm [Name], and in this video, we'll introduce you to the Asset Management System and show you how to navigate the interface.

This system is ISO 55000/55001 compliant and designed specifically for managing assets throughout their entire lifecycle - from procurement to disposal.

Let's get started!"

**[SECTION 1: Accessing the System - 0:30-2:00]**

"First, let's access the system. Open your web browser and navigate to http://172.24.13.88:8000

[Screen: Show login page]

Enter your credentials and click Login.

[Screen: Show successful login]

Once logged in, you'll see the Home workspace. On the left sidebar, you'll find all the Sigma modules.

[Screen: Highlight sidebar]

Click on 'Asset Management' to access the Asset Management workspace.

[Screen: Click and show Asset Management workspace]

This is your main dashboard. Let's explore what you see here."

**[SECTION 2: Dashboard Overview - 2:00-4:00]**

"At the top, you'll see five number cards showing key metrics:

[Screen: Highlight each card]

1. Total Assets - The total number of assets in the system
2. Critical Assets - Assets with critical health status
3. Maintenance Due - Assets requiring maintenance
4. Open Work Orders - Active work orders
5. Average Asset Health - Overall health score

Below that, you'll see four dashboard charts:

[Screen: Highlight each chart]

1. Asset Health Distribution - Shows how many assets are in each health category
2. Work Order Status - Current status of all work orders
3. Maintenance Cost Trend - Monthly maintenance costs over time
4. Risk Classification - Distribution of assets by risk level

These give you a real-time overview of your asset management operations."

**[SECTION 3: Navigation - 4:00-6:00]**

"Let's look at the main sections in the workspace.

[Screen: Scroll to shortcuts section]

The Shortcuts section provides quick access to:
- Assets - View all assets
- Work Orders - Manage maintenance work
- Maintenance Schedules - Plan preventive maintenance
- Risk Register - Track asset risks

[Screen: Scroll to links section]

The Links section is organized into categories:

1. **Assets** - Asset list, categories, locations
2. **Maintenance** - Schedules, work orders, spare parts
3. **Monitoring** - IoT devices, alerts, telemetry
4. **Risk & Compliance** - Risk register, audits
5. **Vendors** - Vendor profiles, SLA contracts
6. **Reports** - All available reports

You can click any of these links to access that feature."

**[SECTION 4: Quick Tour - 6:00-9:00]**

"Let's take a quick tour of the main features.

[Screen: Click on 'Asset' shortcut]

This is the Asset List view. You can see all your assets here, with filters on the left to narrow down your search.

[Screen: Show filters]

You can filter by lifecycle status, criticality, health status, category, and location.

[Screen: Click back button]

[Screen: Click on 'Asset Work Order' shortcut]

This is the Work Order List. You can see all maintenance work orders, their status, priority, and assigned technician.

[Screen: Show work order list]

The color coding helps you quickly identify priority levels - red for emergency, orange for critical, and so on.

[Screen: Click back button]

[Screen: Click on 'Asset Health Dashboard' report]

This report shows detailed health metrics for all your assets, including health score, operating hours, and last maintenance date.

[Screen: Show report]

You can export this data to Excel or PDF using the buttons at the top."

**[SECTION 5: Wrap Up - 9:00-10:00]**

"That's a quick overview of the Asset Management System interface.

In the next videos, we'll dive deeper into:
- Creating and managing assets
- Setting up maintenance schedules
- Creating and completing work orders
- Using the mobile interface
- Generating reports

Remember, you can always return to the Asset Management workspace by clicking 'Asset Management' in the left sidebar.

Thanks for watching! See you in the next video."

**[OUTRO - 10:00]**

[Screen: Show contact information and next video preview]

---

## Video 2: Creating and Managing Assets (15 minutes)

### Script

**[INTRO - 0:00-0:30]**

"Welcome back! In this video, we'll learn how to create and manage assets in the system.

We'll cover:
- Creating asset categories and locations
- Adding a new asset
- Updating asset information
- Tracking asset health
- Linking IoT devices

Let's begin!"

**[SECTION 1: Asset Categories - 0:30-3:00]**

"Before creating assets, we need to set up asset categories.

[Screen: Navigate to Asset Category Sigma]

Click on 'Asset Category Sigma' in the Assets section.

[Screen: Show category list]

You'll see existing categories like IT Equipment, Network Devices, Security Systems, etc.

Let's create a new category. Click the 'New' button.

[Screen: Show new category form]

Fill in the required fields:

1. **Category Name** - e.g., 'Network Switches'
2. **Asset Type** - Select 'IT Equipment'
3. **Maintenance Strategy** - Select 'Preventive Maintenance'
4. **MTBF Hours** - Mean Time Between Failures, e.g., 50000
5. **Enable Predictive Maintenance** - Check this box
6. **Failure Probability Threshold** - e.g., 70%

[Screen: Fill in fields]

You can also configure:
- Depreciation templates
- Risk classification
- IoT monitoring flags

Click 'Save' to create the category.

[Screen: Click Save]

Great! Now we have a category for our assets."

**[SECTION 2: Asset Locations - 3:00-5:00]**

"Next, let's set up asset locations.

[Screen: Navigate to Asset Location]

Click on 'Asset Location' in the Assets section.

[Screen: Show location list]

Locations are hierarchical - Site, Building, Floor, Room.

Let's create a new location. Click 'New'.

[Screen: Show new location form]

Fill in:

1. **Location Name** - e.g., 'Server Room 301'
2. **Location Type** - Select 'Room'
3. **Parent Location** - Select '3rd Floor'
4. **GPS Latitude** - e.g., -1.2921
5. **GPS Longitude** - e.g., 36.8219
6. **Capacity** - e.g., 20 assets

[Screen: Fill in fields]

You can also add:
- Address
- Environmental conditions
- Access control requirements

Click 'Save'.

[Screen: Click Save]

Perfect! Now we can assign assets to this location."

**[SECTION 3: Creating an Asset - 5:00-10:00]**

"Now let's create an asset.

[Screen: Navigate to Asset list]

Click on 'Asset' in the Assets section, then click 'New'.

[Screen: Show new asset form]

The form has several sections. Let's fill them in:

**Basic Information:**
1. **Asset Name** - e.g., 'Cisco Switch SW-301-01'
2. **Asset Category** - Select 'Network Switches'
3. **Asset Location** - Select 'Server Room 301'
4. **Serial Number** - e.g., 'FCW2234G0XX'

[Screen: Fill in basic info]

**Lifecycle Information:**
1. **Lifecycle Status** - Select 'Operational'
2. **Criticality Rating** - Select 'High'
3. **Purchase Date** - Select date
4. **Warranty Expiry Date** - Select date

[Screen: Fill in lifecycle info]

**Technical Details:**
1. **Manufacturer** - e.g., 'Cisco Systems'
2. **Model** - e.g., 'Catalyst 2960-X'
3. **Specifications** - Enter technical specs
4. **Total Operating Hours** - e.g., 8760

[Screen: Fill in technical details]

**Financial Information:**
1. **Purchase Cost** - e.g., 150000
2. **Current Value** - Auto-calculated based on depreciation

[Screen: Show financial section]

**Health Monitoring:**
The health score will be auto-updated from IoT telemetry data.

[Screen: Show health section]

Click 'Save' to create the asset.

[Screen: Click Save]

Excellent! Your asset is now in the system."

**[SECTION 4: Linking IoT Devices - 10:00-12:00]**

"To enable real-time monitoring, let's link an IoT device to this asset.

[Screen: Navigate to Monitored Device]

Click on 'Monitored Device' in the Monitoring section, then click 'New'.

[Screen: Show new monitored device form]

Fill in:

1. **Device ID** - e.g., 'SW-301-01'
2. **Device Type** - Select 'Network Device'
3. **Asset** - Select our newly created asset
4. **Monitoring Platform** - Select your monitoring platform
5. **IP Address** - e.g., '192.168.1.10'
6. **SNMP Community** - If using SNMP

[Screen: Fill in fields]

Click 'Save'.

[Screen: Click Save]

Now the system will automatically collect telemetry data from this device and update the asset's health score."

**[SECTION 5: Updating Assets - 12:00-14:00]**

"To update an asset, simply open it from the Asset list.

[Screen: Open asset]

You can update any field, add notes, or change the location.

[Screen: Show editing]

Important fields to keep updated:
- Operating hours
- Location (if moved)
- Health status
- Maintenance notes

Click 'Save' after making changes.

[Screen: Click Save]

You can also view the asset's history by clicking the 'Timeline' button.

[Screen: Show timeline]

This shows all changes, work orders, and maintenance activities."

**[SECTION 6: Wrap Up - 14:00-15:00]**

"That's how you create and manage assets!

Key takeaways:
- Set up categories and locations first
- Fill in all required asset information
- Link IoT devices for real-time monitoring
- Keep asset data up-to-date

In the next video, we'll learn how to set up maintenance schedules.

Thanks for watching!"

**[OUTRO - 15:00]**

---

## Video 3: Maintenance Scheduling (12 minutes)

### Script

**[INTRO - 0:00-0:30]**

"Welcome back! In this video, we'll learn how to set up maintenance schedules for your assets.

Proper maintenance scheduling is key to:
- Preventing unexpected failures
- Extending asset lifespan
- Reducing maintenance costs
- Ensuring compliance

Let's get started!"

**[SECTION 1: Understanding Schedule Types - 0:30-2:00]**

"The system supports four types of maintenance schedules:

[Screen: Show schedule type diagram]

1. **Time-Based** - Fixed intervals (daily, weekly, monthly, yearly)
   Example: Monthly generator inspection

2. **Usage-Based** - Based on operating hours
   Example: Every 5000 hours of operation

3. **Condition-Based** - Triggered by sensor thresholds
   Example: When temperature exceeds 80°C

4. **Predictive** - Based on MTBF and failure probability
   Example: When failure probability exceeds 70%

Each type has its use cases. Let's see how to create them."

**[SECTION 2: Creating a Time-Based Schedule - 2:00-5:00]**

"Let's create a preventive maintenance schedule for our network switch.

[Screen: Navigate to Asset Maintenance Schedule]

Click on 'Asset Maintenance Schedule', then click 'New'.

[Screen: Show new schedule form]

Fill in:

1. **Asset** - Select 'Cisco Switch SW-301-01'
2. **Schedule Name** - e.g., 'Monthly Switch Inspection'
3. **Maintenance Type** - Select 'Preventive Maintenance'
4. **Schedule Type** - Select 'Time-Based'

[Screen: Fill in basic fields]

**Time-Based Configuration:**
1. **Frequency** - Select 'Monthly'
2. **Start Date** - Select start date
3. **Next Due Date** - Auto-calculated

[Screen: Fill in time-based fields]

**Maintenance Details:**
1. **Estimated Duration** - e.g., 2 hours
2. **Estimated Cost** - e.g., 5000
3. **Required Skills** - e.g., 'Network Administration'
4. **Required Tools** - e.g., 'Cable tester, Multimeter'

[Screen: Fill in maintenance details]

**Checklist Items:**
Add tasks to be performed:
- Check port status
- Verify VLAN configuration
- Test connectivity
- Clean dust from vents
- Check temperature

[Screen: Add checklist items]

Click 'Save' and then 'Submit' to activate the schedule.

[Screen: Save and submit]

The system will now automatically create work orders based on this schedule."

**[SECTION 3: Creating a Usage-Based Schedule - 5:00-7:00]**

"Now let's create a usage-based schedule.

[Screen: Click New]

Fill in basic information, then:

1. **Schedule Type** - Select 'Usage-Based'
2. **Operating Hours Threshold** - e.g., 5000 hours
3. **Current Operating Hours** - Auto-fetched from asset

[Screen: Fill in usage-based fields]

The system will create a work order when the asset reaches the threshold.

Click 'Save' and 'Submit'.

[Screen: Save and submit]"

**[SECTION 4: Creating a Condition-Based Schedule - 7:00-9:00]**

"For condition-based maintenance, we need IoT sensors.

[Screen: Click New]

Fill in basic information, then:

1. **Schedule Type** - Select 'Condition-Based'

[Screen: Select condition-based]

**Condition Triggers:**
Add trigger conditions:
- Metric: Temperature
- Operator: Greater Than
- Threshold: 80
- Unit: °C

[Screen: Add condition trigger]

You can add multiple conditions (AND/OR logic).

The system monitors telemetry data and creates work orders when conditions are met.

Click 'Save' and 'Submit'.

[Screen: Save and submit]"

**[SECTION 5: Creating a Predictive Schedule - 9:00-11:00]**

"Finally, let's create a predictive maintenance schedule.

[Screen: Click New]

Fill in basic information, then:

1. **Schedule Type** - Select 'Predictive'
2. **MTBF Hours** - e.g., 50000 (from asset category)
3. **Failure Probability Threshold** - e.g., 70%

[Screen: Fill in predictive fields]

The system calculates failure probability based on:
- Operating hours vs MTBF
- Health score trend
- Recent alert frequency
- Maintenance history

When probability exceeds the threshold, a work order is created.

Click 'Save' and 'Submit'.

[Screen: Save and submit]"

**[SECTION 6: Wrap Up - 11:00-12:00]**

"That's how you set up maintenance schedules!

Key takeaways:
- Choose the right schedule type for each asset
- Set realistic frequencies and thresholds
- Include detailed checklists
- Submit schedules to activate them

The system will automatically:
- Create work orders from schedules
- Send notifications
- Track compliance

In the next video, we'll learn how to manage work orders.

Thanks for watching!"

**[OUTRO - 12:00]**

---

## Video 4: Work Order Management (15 minutes)

### Script

**[INTRO - 0:00-0:30]**

"Welcome back! In this video, we'll learn how to manage work orders from creation to completion.

Work orders are the heart of maintenance management. We'll cover:
- Creating work orders
- Assigning to technicians
- Updating status
- Completing work orders
- Using the mobile interface

Let's begin!"

**[SECTION 1: Work Order Workflow - 0:30-2:00]**

"First, let's understand the work order workflow:

[Screen: Show workflow diagram]

1. **Draft** - Initial creation
2. **Scheduled** - Date and time set
3. **Assigned** - Technician assigned
4. **In Progress** - Work started
5. **Completed** - Work finished
6. **Closed** - Reviewed and closed

Each status has specific actions and requirements."

**[SECTION 2: Creating a Work Order - 2:00-5:00]**

"Let's create a work order manually.

[Screen: Navigate to Asset Work Order]

Click on 'Asset Work Order', then click 'New'.

[Screen: Show new work order form]

Fill in:

1. **Asset** - Select the asset
2. **Work Order Type** - Select type (Preventive, Corrective, etc.)
3. **Priority** - Select priority level
4. **Work Description** - Describe the work to be done

[Screen: Fill in basic fields]

**Scheduling:**
1. **Scheduled Start Date** - When to start
2. **Scheduled End Date** - When to finish
3. **Estimated Duration** - Hours required

[Screen: Fill in scheduling]

**Requirements:**
1. **Required Skills** - e.g., 'Electrical Engineering'
2. **Required Tools** - e.g., 'Multimeter, Screwdriver set'
3. **Safety Requirements** - e.g., 'PPE required, Lockout/Tagout'

[Screen: Fill in requirements]

**Spare Parts:**
Add required spare parts from inventory.

[Screen: Add spare parts]

Click 'Save' to create the work order.

[Screen: Click Save]"

**[SECTION 3: Assigning Work Orders - 5:00-7:00]**

"Now let's assign the work order to a technician.

[Screen: Open work order]

You have two options:

**Option 1: Manual Assignment**
1. Click 'Assign To' field
2. Select technician from list
3. Click 'Save'

[Screen: Show manual assignment]

**Option 2: Auto-Assignment**
The system can automatically assign based on:
- Skills matching
- Current workload
- Location proximity
- Performance history

[Screen: Show auto-assignment]

Once assigned, the technician receives a notification and can view the work order on their mobile device."

**[SECTION 4: Starting Work - 7:00-9:00]**

"When the technician is ready to start work:

[Screen: Open work order]

1. Change status to 'In Progress'
2. Set 'Actual Start Date' to current time
3. Click 'Save'

[Screen: Update status]

The system tracks:
- Start time
- Duration
- Progress updates

Technicians can also start work from the mobile app with one tap."

**[SECTION 5: Completing Work - 9:00-12:00]**

"When work is finished:

[Screen: Open work order]

1. Update checklist items - mark each task as completed
2. Add completion notes - describe what was done
3. Enter actual cost - if different from estimated
4. Set 'Actual End Date' to current time
5. Change status to 'Completed'

[Screen: Fill in completion details]

Click 'Save' and then 'Submit' to finalize.

[Screen: Submit work order]

The system automatically:
- Calculates actual duration
- Updates asset maintenance history
- Updates health score
- Closes related alerts"

**[SECTION 6: Mobile Interface - 12:00-14:00]**

"Technicians can manage work orders from their mobile devices.

[Screen: Show mobile interface]

Access the mobile interface at:
http://172.24.13.88:8000/mobile/work_orders

[Screen: Show mobile URL]

**Mobile Features:**
- View assigned work orders
- Filter by status
- Start/complete work orders
- Update checklist items
- Scan asset QR codes
- Work offline with auto-sync

[Screen: Demo mobile features]

This makes it easy for field technicians to update work orders in real-time."

**[SECTION 7: Wrap Up - 14:00-15:00]**

"That's how you manage work orders!

Key takeaways:
- Create detailed work orders with all requirements
- Assign to the right technician
- Track progress in real-time
- Complete with detailed notes
- Use mobile interface for field work

In the next video, we'll learn how to generate reports and analytics.

Thanks for watching!"

**[OUTRO - 15:00]**

---

## Video 5: Reports and Analytics (12 minutes)

### Script

**[INTRO - 0:00-0:30]**

"Welcome to the final video in our Asset Management training series!

In this video, we'll learn how to generate reports and use analytics to make data-driven decisions.

We'll cover:
- Dashboard overview
- Running reports
- Exporting data
- Interpreting analytics

Let's dive in!"

**[SECTION 1: Dashboard Overview - 0:30-3:00]**

"Let's start with the Asset Management dashboard.

[Screen: Show Asset Management workspace]

The dashboard provides real-time insights:

**Number Cards:**
- Total Assets: 150
- Critical Assets: 5
- Maintenance Due: 12
- Open Work Orders: 8
- Avg Asset Health: 85

[Screen: Highlight each card]

**Charts:**
1. **Asset Health Distribution** - Shows 60% Excellent, 25% Good, 10% Fair, 5% Poor
2. **Work Order Status** - Shows 40% In Progress, 30% Assigned, 30% Scheduled
3. **Maintenance Cost Trend** - Shows monthly costs over 12 months
4. **Risk Classification** - Shows risk distribution

[Screen: Highlight each chart]

These give you an at-a-glance view of your asset management operations."

**[SECTION 2: Asset Utilization Report - 3:00-5:00]**

"Let's run the Asset Utilization Report.

[Screen: Click on Asset Utilization Report]

This report shows:
- Asset name and category
- Operating hours
- Utilization percentage
- Downtime hours
- Availability percentage

[Screen: Show report results]

You can filter by:
- Date range
- Asset category
- Location
- Criticality

[Screen: Show filters]

To export, click the 'Export' button and select format (Excel or PDF).

[Screen: Show export options]"

**[SECTION 3: Maintenance Cost Analysis - 5:00-7:00]**

"Next, let's look at the Maintenance Cost Analysis Report.

[Screen: Click on Maintenance Cost Analysis]

This report shows:
- Total maintenance cost
- Cost by asset
- Cost by category
- Cost by work order type
- Cost trends over time

[Screen: Show report results]

The chart at the bottom visualizes cost trends.

[Screen: Show chart]

This helps you:
- Identify high-cost assets
- Budget for future maintenance
- Optimize maintenance strategies"

**[SECTION 4: Asset Downtime Report - 7:00-9:00]**

"The Asset Downtime Report is crucial for availability tracking.

[Screen: Click on Asset Downtime Report]

This report shows:
- Total downtime hours
- MTTR (Mean Time To Repair)
- MTBF (Mean Time Between Failures)
- Availability percentage
- Downtime by category

[Screen: Show report results]

Use this to:
- Identify problematic assets
- Improve maintenance processes
- Meet SLA commitments"

**[SECTION 5: Custom Filters and Exports - 9:00-11:00]**

"All reports support custom filters.

[Screen: Show filter panel]

You can filter by:
- Date range
- Asset category
- Location
- Criticality
- Health status
- And more...

[Screen: Apply filters]

After filtering, export your data:

1. Click 'Export' button
2. Select format (Excel, PDF, CSV)
3. Download file

[Screen: Show export process]

You can also schedule reports to run automatically and email results."

**[SECTION 6: Wrap Up - 11:00-12:00]**

"That's how you use reports and analytics!

Key takeaways:
- Use the dashboard for real-time insights
- Run reports regularly to track performance
- Export data for presentations and analysis
- Use filters to focus on specific areas

**Congratulations!** You've completed the Asset Management training series.

You now know how to:
✅ Navigate the system
✅ Create and manage assets
✅ Set up maintenance schedules
✅ Manage work orders
✅ Generate reports and analytics

Start using the system and remember - practice makes perfect!

For additional support, refer to:
- User Manual
- Technical Guide
- Quick Reference Cards

Thanks for watching, and happy asset managing!"

**[OUTRO - 12:00]**

---

**End of Video Scripts**

