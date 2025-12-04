# Asset Management Module - Administrator Guide

## 📖 Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation & Configuration](#installation--configuration)
3. [Scheduled Jobs](#scheduled-jobs)
4. [Integration Management](#integration-management)
5. [Performance Optimization](#performance-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Backup & Recovery](#backup--recovery)
8. [Security & Permissions](#security--permissions)

---

## 1. System Architecture

### Module Structure

```
sigma/
├── sigma_asset_integrations/
│   ├── doctype/
│   │   ├── asset_category_sigma/
│   │   ├── asset_location/
│   │   ├── asset_maintenance_schedule/
│   │   ├── asset_work_order/
│   │   ├── asset_risk_register/
│   │   ├── asset_audit/
│   │   ├── asset_audit_finding/
│   │   ├── asset_vendor/
│   │   ├── sla_contract/
│   │   └── sla_kpi/
│   ├── report/
│   │   ├── maintenance_due_report/
│   │   ├── asset_lifecycle_report/
│   │   ├── asset_criticality_matrix/
│   │   ├── compliance_status_report/
│   │   └── vendor_performance_report/
│   └── automation/
│       ├── scheduled_jobs.py
│       └── contract_automation.py
```

### Database Schema

**Core Tables**:
- `tabAsset Category Sigma`: Asset categories with ISO 55000 fields
- `tabAsset Location`: Hierarchical locations
- `tabAsset`: Enhanced with ISO 55000 compliance fields
- `tabAsset Maintenance Schedule`: Maintenance scheduling
- `tabAsset Work Order`: Work order management
- `tabAsset Risk Register`: Risk management
- `tabAsset Audit`: Compliance auditing
- `tabAsset Vendor`: Vendor management
- `tabSLA Contract`: SLA contract management

**Child Tables**:
- `tabAsset Audit Finding`: Audit findings
- `tabSLA KPI`: SLA KPIs

### Integration Points

- **Monitoring Platform**: Real-time telemetry ingestion
- **Monitored Device**: Asset-device mapping
- **Telemetry Event**: Health score calculations
- **Monitoring Alert**: Automatic work order creation

---

## 2. Installation & Configuration

### Prerequisites

- Frappe Framework v14+
- ERPNext v14+
- Sigma app installed
- Unified Monitoring system configured

### Installation Steps

1. **Pull latest code**:
   ```bash
   cd ~/frappe-bench/apps/sigma
   git pull origin main
   ```

2. **Run migrations**:
   ```bash
   bench --site <site-name> migrate
   ```

3. **Clear cache**:
   ```bash
   bench --site <site-name> clear-cache
   ```

4. **Restart services**:
   ```bash
   bench restart
   ```

### Initial Configuration

1. **Create Asset Categories**:
   - Navigate to `/app/asset-category-sigma`
   - Create categories for your organization
   - Set maintenance strategies and MTBF values

2. **Create Asset Locations**:
   - Navigate to `/app/asset-location`
   - Create hierarchical location structure
   - Add GPS coordinates if needed

3. **Configure Scheduled Jobs**:
   - Jobs are automatically configured in `hooks.py`
   - Verify jobs are running: `bench --site <site-name> show-scheduler-status`

4. **Set Up Permissions**:
   - Configure role permissions for each DocType
   - Recommended roles: Asset Manager, Maintenance Technician, Auditor

---

## 3. Scheduled Jobs

### Hourly Jobs

#### 1. Auto-escalate Critical Alerts
**Function**: `sigma.sigma_asset_integrations.automation.scheduled_jobs.auto_escalate_critical_alerts`  
**Purpose**: Creates work orders from critical monitoring alerts  
**Execution**: Every hour  
**Log Location**: `~/frappe-bench/logs/scheduler.log`

**Manual Trigger**:
```python
bench --site <site-name> console
>>> from sigma.sigma_asset_integrations.automation.scheduled_jobs import auto_escalate_critical_alerts
>>> auto_escalate_critical_alerts()
```

#### 2. Auto-update Asset Health
**Function**: `sigma.sigma_asset_integrations.automation.scheduled_jobs.auto_update_asset_health`  
**Purpose**: Updates asset health scores from telemetry data  
**Execution**: Every hour  

**Manual Trigger**:
```python
bench --site <site-name> console
>>> from sigma.sigma_asset_integrations.automation.scheduled_jobs import auto_update_asset_health
>>> auto_update_asset_health()
```

### Daily Jobs

#### 1. Auto-generate Maintenance Schedules
**Function**: `sigma.sigma_asset_integrations.automation.scheduled_jobs.auto_generate_maintenance_schedules`  
**Purpose**: Creates maintenance schedules based on MTBF and condition  
**Execution**: Daily at midnight  

#### 2. Check Contract Expiry
**Function**: `sigma.sigma_asset_integrations.automation.contract_automation.check_contract_expiry`  
**Purpose**: Sends notifications for expiring contracts  
**Execution**: Daily at midnight  

#### 3. Update Contract Performance
**Function**: `sigma.sigma_asset_integrations.automation.contract_automation.update_contract_performance`  
**Purpose**: Updates SLA contract performance metrics  
**Execution**: Daily at midnight  

#### 4. Check Vendor Compliance
**Function**: `sigma.sigma_asset_integrations.automation.contract_automation.check_vendor_compliance`  
**Purpose**: Checks vendor certifications and insurance expiry  
**Execution**: Daily at midnight  

### Monitoring Scheduled Jobs

**Check scheduler status**:
```bash
bench --site <site-name> show-scheduler-status
```

**View scheduler logs**:
```bash
tail -f ~/frappe-bench/logs/scheduler.log
```

**Disable a job** (in `hooks.py`):
```python
scheduler_events = {
    "hourly": [
        # "sigma.sigma_asset_integrations.automation.scheduled_jobs.auto_escalate_critical_alerts",  # Disabled
    ]
}
```

---

## 4. Integration Management

### Monitoring Platform Integration

**Configuration**:
1. Ensure Monitoring Platform is configured
2. Create Monitored Devices for assets
3. Link assets to monitored devices via `monitored_device` field

**Telemetry Flow**:
```
IoT Device → Webhook API → Telemetry Event → Asset Health Update
```

**Troubleshooting**:
- Check webhook logs: `~/frappe-bench/logs/web.log`
- Verify monitored device links: `SELECT * FROM tabAsset WHERE monitored_device IS NOT NULL`
- Check telemetry events: `/app/telemetry-event`

### Work Order Integration

**Automatic Work Order Creation**:
- Critical alerts automatically create work orders
- Configured in `auto_escalate_critical_alerts()` job
- Work orders linked to monitoring alerts

**Manual Integration**:
```python
# Create work order from alert
alert = frappe.get_doc("Monitoring Alert", "ALERT-001")
work_order = frappe.get_doc({
    "doctype": "Asset Work Order",
    "asset": alert.monitored_device,
    "work_order_type": "Corrective Maintenance",
    "priority": "Critical",
    "description": alert.alert_message,
    "monitoring_alert": alert.name
})
work_order.insert()
```

---

## 5. Performance Optimization

### Database Indexing

**Recommended Indexes**:
```sql
-- Asset table
CREATE INDEX idx_asset_category ON `tabAsset`(asset_category_sigma);
CREATE INDEX idx_asset_location ON `tabAsset`(asset_location);
CREATE INDEX idx_asset_criticality ON `tabAsset`(criticality_rating);
CREATE INDEX idx_asset_lifecycle ON `tabAsset`(lifecycle_status);

-- Maintenance Schedule
CREATE INDEX idx_schedule_asset ON `tabAsset Maintenance Schedule`(asset);
CREATE INDEX idx_schedule_status ON `tabAsset Maintenance Schedule`(schedule_status);

-- Work Order
CREATE INDEX idx_wo_asset ON `tabAsset Work Order`(asset);
CREATE INDEX idx_wo_status ON `tabAsset Work Order`(work_order_status);
```

### Caching

**Enable Redis caching**:
```bash
# In site_config.json
{
    "redis_cache": "redis://localhost:13000",
    "redis_queue": "redis://localhost:11000"
}
```

### Query Optimization

**Use filters in reports**:
- Always filter by date range
- Use asset category/location filters
- Limit result sets to < 1000 records

---

## 6. Troubleshooting

### Common Issues

#### 1. Scheduled Jobs Not Running

**Symptoms**: Maintenance schedules not auto-generated, alerts not escalated

**Solution**:
```bash
# Check scheduler status
bench --site <site-name> show-scheduler-status

# Enable scheduler
bench --site <site-name> enable-scheduler

# Restart scheduler
bench restart
```

#### 2. Asset Health Not Updating

**Symptoms**: Health scores remain static despite telemetry data

**Solution**:
- Verify monitored device link: Check `asset.monitored_device` field
- Check telemetry events: `/app/telemetry-event`
- Manually trigger health update job
- Check scheduler logs for errors

#### 3. Work Orders Not Created from Alerts

**Symptoms**: Critical alerts exist but no work orders created

**Solution**:
- Check alert severity: Must be "Critical" or "High"
- Verify alert status: Must be "Open" or "Acknowledged"
- Check monitored device link to asset
- Review scheduler logs

---

## 7. Backup & Recovery

### Backup Strategy

**Daily Backups**:
```bash
# Automated backup
bench --site <site-name> backup --with-files

# Backup location
~/frappe-bench/sites/<site-name>/private/backups/
```

**Backup Retention**:
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 12 months

### Recovery Procedure

**Restore from backup**:
```bash
# Restore database
bench --site <site-name> restore <backup-file>

# Restore files
bench --site <site-name> restore --with-files <backup-file>
```

---

## 8. Security & Permissions

### Role-Based Access Control

**Recommended Roles**:
- **Asset Manager**: Full access to all asset management features
- **Maintenance Technician**: Access to work orders and maintenance schedules
- **Auditor**: Access to audits and compliance reports
- **Vendor Manager**: Access to vendor and contract management

### Permission Configuration

**Asset DocType**:
- Read: All roles
- Write: Asset Manager, Maintenance Technician
- Create: Asset Manager
- Delete: Asset Manager
- Submit: Asset Manager

**Work Order DocType**:
- Read: All roles
- Write: Maintenance Technician, Asset Manager
- Create: Maintenance Technician, Asset Manager
- Submit: Maintenance Technician

---

## 📞 Support

For technical support:
- **Email**: info@prismod.co.ke
- **Documentation**: See ASSET_MANAGEMENT_FINAL_SUMMARY.md
- **Logs**: `~/frappe-bench/logs/`

---

**Version**: 1.0  
**Last Updated**: November 19, 2025

