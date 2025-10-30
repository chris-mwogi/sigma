# Sigma Frontend - Module Reference Guide

## Module Overview

The Sigma frontend consists of 13 integrated modules organized into 3 categories:

---

## 🔒 Security Modules (5)

### 1. Cases
- **Route**: `/cases`
- **Component**: `src/views/cases/CaseList.vue`
- **Purpose**: Manage security cases and incidents
- **Icon**: 📋
- **Features**: Case tracking, status management, case details

### 2. Incidents
- **Route**: `/incidents`
- **Component**: `src/views/incidents/IncidentList.vue`
- **Purpose**: Track and report security incidents
- **Icon**: ⚠️
- **Features**: Incident reporting, severity levels, incident tracking

### 3. Access Control
- **Route**: `/access-control`
- **Component**: `src/views/access-control/AccessControl.vue`
- **Purpose**: Manage access permissions and credentials
- **Icon**: 🔐
- **Features**: Permission management, access logs, credential control

### 4. Guard Monitoring
- **Route**: `/guard-monitoring`
- **Component**: `src/views/guard-monitoring/GuardMonitoring.vue`
- **Purpose**: Monitor guard activities and schedules
- **Icon**: 👮
- **Features**: Guard tracking, schedule management, activity logs

### 5. Risk Assessment
- **Route**: `/risk-assessment`
- **Component**: `src/views/risk-assessment/RiskAssessment.vue`
- **Purpose**: Assess and manage security risks
- **Icon**: 📊
- **Features**: Risk evaluation, threat analysis, mitigation planning

---

## 📦 Asset & Inventory (3)

### 6. Assets
- **Route**: `/assets`
- **Component**: `src/views/assets/AssetList.vue`
- **Purpose**: Track and manage company assets
- **Icon**: 🏢
- **Features**: Asset inventory, asset details, asset tracking

### 7. Vehicle Management
- **Route**: `/vehicle-management`
- **Component**: `src/views/vehicle-management/VehicleManagementDashboard.vue`
- **Purpose**: Manage fleet vehicles and tracking
- **Icon**: 🚗
- **Features**: 
  - Total vehicles count
  - Maintenance tracking
  - Availability status
  - On-road tracking
  - Driver assignment
  - Fuel monitoring
  - Mileage tracking

### 8. Visitor Management
- **Route**: `/visitor-management`
- **Component**: `src/views/visitor-management/VisitorManagementDashboard.vue`
- **Purpose**: Track and manage visitor access
- **Icon**: 👥
- **Features**:
  - Visitor registration
  - Check-in/check-out tracking
  - Pre-registration
  - Host assignment
  - Access logs
  - Visitor history

---

## 💼 Support & Operations (5)

### 9. Helpdesk
- **Route**: `/helpdesk`
- **Component**: `src/views/helpdesk/HelpdeskDashboard.vue`
- **Purpose**: Support ticket management system
- **Icon**: 💬
- **Features**:
  - Open tickets tracking
  - Pending tickets
  - Resolved tickets
  - Average resolution time
  - Ticket list with status
  - Quick actions

### 10. Support
- **Route**: `/support`
- **Component**: `src/views/support/SupportDashboard.vue`
- **Purpose**: Technical support and issue resolution
- **Icon**: 🆘
- **Features**:
  - Active issues tracking
  - Critical issues
  - Resolved today count
  - Average response time
  - Support cases list
  - Support resources

### 11. Telephony
- **Route**: `/telephony`
- **Component**: `src/views/telephony/TelephonyDashboard.vue`
- **Purpose**: Communication and call management
- **Icon**: ☎️
- **Features**:
  - Active calls tracking
  - Total calls today
  - Average call duration
  - Quality score
  - Call log
  - Communication tools

### 12. Projects
- **Route**: `/projects`
- **Component**: `src/views/projects/ProjectsDashboard.vue`
- **Purpose**: Project management and tracking
- **Icon**: 📁
- **Features**:
  - Active projects count
  - In-progress projects
  - Completed projects
  - Average completion rate
  - Project list with progress
  - Project actions

### 13. CRM
- **Route**: `/crm`
- **Component**: `src/views/crm/CRMDashboard.vue`
- **Purpose**: Customer relationship management
- **Icon**: 👔
- **Features**:
  - Total customers
  - Active leads
  - Total revenue
  - Conversion rate
  - Customer list
  - CRM tools

---

## Dashboard Component Structure

All dashboard components follow a consistent pattern:

```vue
<template>
  <div class="module-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Module Name</h1>
      <p class="subtitle">Module description</p>
    </div>

    <!-- KPI Cards (4 metrics) -->
    <div class="grid grid-4">
      <div class="kpi-card">...</div>
      <div class="kpi-card">...</div>
      <div class="kpi-card">...</div>
      <div class="kpi-card">...</div>
    </div>

    <!-- Content Grid (2 columns) -->
    <div class="grid grid-2 mt-3">
      <!-- Data List Card -->
      <div class="card">
        <div class="card-header">
          <h2>Recent Items</h2>
          <button>+ Add</button>
        </div>
        <div class="card-body">
          <!-- List items -->
        </div>
      </div>

      <!-- Actions Card -->
      <div class="card">
        <div class="card-header">
          <h2>Quick Actions</h2>
        </div>
        <div class="card-body">
          <!-- Action buttons -->
        </div>
      </div>
    </div>
  </div>
</template>
```

---

## Color Coding

### KPI Card Colors
- **Primary** (Deep Blue): Main metrics
- **Warning** (Orange): Caution metrics
- **Success** (Green): Positive metrics
- **Info** (Electric Blue): Information metrics

### Status Badges
- **Available**: Green background
- **On Road**: Blue background
- **Maintenance**: Orange background
- **Checked In**: Green background
- **Checked Out**: Gray background

---

## Navigation Structure

### Sidebar Menu
```
📊 Dashboard
├── 📋 Cases
├── ⚠️ Incidents
├── 🔐 Access Control
├── 👮 Guard Monitoring
├── 🏢 Assets
├── 📊 Risk Assessment
├── 🚗 Vehicle Management
├── 👥 Visitor Management
├── ─────────────────
├── 💬 Helpdesk
├── 🆘 Support
├── ☎️ Telephony
├── 📁 Projects
└── 👔 CRM
```

---

## Responsive Breakpoints

- **Desktop** (1024px+): Full layout with sidebar
- **Tablet** (768px-1024px): Adjusted grid columns
- **Mobile** (480px-768px): Single column, drawer sidebar
- **Small Mobile** (<480px): Optimized for small screens

---

## File Organization

```
src/views/
├── Dashboard.vue (Landing page)
├── Login.vue
├── cases/
│   ├── CaseList.vue
│   ├── CaseDetail.vue
│   └── CaseForm.vue
├── incidents/
│   ├── IncidentList.vue
│   └── IncidentDetail.vue
├── access-control/
│   └── AccessControl.vue
├── guard-monitoring/
│   └── GuardMonitoring.vue
├── assets/
│   ├── AssetList.vue
│   └── AssetDetail.vue
├── risk-assessment/
│   └── RiskAssessment.vue
├── vehicle-management/
│   └── VehicleManagementDashboard.vue
├── visitor-management/
│   └── VisitorManagementDashboard.vue
├── helpdesk/
│   └── HelpdeskDashboard.vue
├── support/
│   └── SupportDashboard.vue
├── telephony/
│   └── TelephonyDashboard.vue
├── projects/
│   └── ProjectsDashboard.vue
└── crm/
    └── CRMDashboard.vue
```

---

## Quick Links

- **Router Config**: `src/router/index.js`
- **Main Layout**: `src/App.vue`
- **Styles**: `src/assets/styles/main.css`
- **Main Entry**: `src/main.js`
- **Build Config**: `vite.config.js`

---

## Development Tips

1. **Add New Module**
   - Create component in `src/views/module-name/`
   - Add route in `src/router/index.js`
   - Add sidebar link in `src/App.vue`

2. **Modify Dashboard**
   - Edit `src/views/Dashboard.vue`
   - Update module list in the `modules` array
   - Rebuild with `npm run build`

3. **Update Colors**
   - Edit CSS variables in `src/assets/styles/main.css`
   - Changes apply globally to all components

4. **Test Responsive**
   - Use browser DevTools
   - Test at 480px, 768px, 1024px breakpoints
   - Test on actual mobile devices

---

## Status

✅ All 13 modules implemented
✅ All routes configured
✅ All navigation links added
✅ Build successful
✅ Ready for deployment

