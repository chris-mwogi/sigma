# Sigma ERPNext Integrations

Comprehensive integration module connecting Sigma Security Management Platform with ERPNext applications.

## Overview

This module provides bidirectional synchronization between Sigma and ERPNext, covering **7 key integration points**:

1. **Stock Management** - Asset ↔ Item synchronization
2. **Buying/Acquisition** - Purchase Receipt → Asset creation
3. **Selling/Disposal** - Asset disposal → Sales Order
4. **Support/Maintenance** - Asset maintenance lifecycle management ⭐ **NEW**
5. **CRM** - Visitor ↔ Contact synchronization
6. **Projects** - Case ↔ Project/Task mapping
7. **Helpdesk** - Case ↔ Ticket synchronization

## Architecture

### Integration Pattern: Hybrid Extension Model

- **Extends** ERPNext modules with custom fields (doesn't modify core)
- **Uses** Frappe hooks for real-time synchronization
- **Provides** unified API layer for integration operations
- **Tracks** all integration operations in Integration Log

### Module Structure

```
sigma_erpnext_integrations/
├── api/                          # Integration API layer
│   ├── integration_api.py        # Unified API with error handling
│   ├── stock_integration.py      # Asset ↔ Item sync
│   ├── buying_integration.py     # Purchase Receipt → Asset
│   ├── selling_integration.py    # Asset disposal → Sales Order
│   ├── support_integration.py    # Maintenance lifecycle ⭐
│   ├── crm_integration.py        # Visitor ↔ Contact
│   ├── projects_integration.py   # Case ↔ Project
│   └── helpdesk_integration.py   # Case ↔ Ticket
├── custom_fields/                # Custom field definitions
│   ├── custom_fields.json        # All custom fields
│   └── __init__.py               # Installation functions
├── doctype/                      # Custom DocTypes
│   ├── integration_log/          # Integration operation logging
│   └── sigma_integration_settings/  # Configuration settings
├── sync_handlers/                # Scheduled synchronization
│   └── scheduled_sync.py         # Batch sync jobs
├── hooks.py                      # Integration hooks configuration
└── install.py                    # Installation scripts

```

## Key Features

### 1. Stock Integration (Asset ↔ Item)

**Automatic Synchronization:**
- Asset created → Item created in Stock
- Asset updated → Item updated
- Item updated → Asset updated (bidirectional)

**Features:**
- Automatic Item Group assignment
- Valuation rate sync
- Location tracking
- Stock Entry creation

**API Methods:**
```python
# Sync asset to item
StockIntegration.sync_asset_to_item(asset_doc)

# Create stock entry for asset
StockIntegration.create_stock_entry_for_asset(asset_name, warehouse, qty)

# Get stock balance
StockIntegration.get_asset_stock_balance(asset_name)
```

### 2. Support/Maintenance Integration ⭐ **NEW KEY FEATURE**

**Preventive Maintenance:**
- Automatic Maintenance Schedule creation for assets
- Configurable maintenance frequency (Weekly/Monthly/Quarterly/Yearly)
- Scheduled maintenance tracking

**Corrective Maintenance:**
- Incident Report → Maintenance Visit creation
- Asset status updates based on maintenance completion
- Maintenance history tracking

**Features:**
- Asset downtime recording
- Maintenance cost tracking
- Warranty management
- SLA tracking
- Maintenance history reports

**API Methods:**
```python
# Sync asset maintenance schedule
SupportIntegration.sync_asset_maintenance(asset_doc)

# Create maintenance visit from incident
SupportIntegration.create_maintenance_visit_from_incident(incident_doc)

# Update asset from maintenance visit
SupportIntegration.update_asset_from_maintenance_visit(visit_doc)

# Manual maintenance request
SupportIntegration.create_maintenance_request(asset_name, issue_description, priority)

# Get maintenance history
SupportIntegration.get_asset_maintenance_history(asset_name)
```

### 3. Buying Integration (Procurement)

**Purchase Workflow:**
- Asset → Material Request (Purchase Request)
- Purchase Receipt → Asset creation (automatic)
- Procurement status tracking

**API Methods:**
```python
# Create purchase request
BuyingIntegration.create_purchase_request(asset_name, supplier, expected_delivery_date)

# Get procurement status
BuyingIntegration.get_asset_procurement_status(asset_name)
```

### 4. Selling Integration (Disposal)

**Disposal Workflow:**
- Asset disposal → Sales Order creation
- Asset status update to "Disposed"

**API Methods:**
```python
# Create disposal request
SellingIntegration.create_disposal_request(asset_name, disposal_reason, estimated_value)
```

### 5. CRM Integration (Visitor Management)

**Visitor → Contact Sync:**
- Visitor created → Contact created
- Visitor updated → Contact updated
- Activity tracking

### 6. Projects Integration

**Case → Project Mapping:**
- High/Critical priority cases → Project creation
- Case tracking as project tasks

### 7. Helpdesk Integration

**Case → Ticket Sync:**
- Case created → Helpdesk Ticket created
- Case status → Ticket status sync
- Bidirectional comment sync

## Installation

### Prerequisites

1. **Frappe/ERPNext** installed
2. **Sigma** app installed
3. Optional: **Frappe Helpdesk** for helpdesk integration

### Install Steps

1. The integration module is automatically installed with Sigma app

2. After installation, custom fields are automatically created

3. Configure integration settings:
   ```
   Setup > Sigma Integration Settings
   ```

4. Enable/disable specific integrations as needed

### Manual Installation

If you need to manually install custom fields:

```python
from sigma.sigma_erpnext_integrations.custom_fields import install_custom_fields
install_custom_fields()
```

## Configuration

### Integration Settings

Navigate to: **Setup > Sigma Integration Settings**

**Available Settings:**
- Enable/disable each integration module
- Auto-sync configuration
- Sync interval (default: 1 hour)
- Last sync timestamp

### Custom Fields Added

**Asset DocType:**
- `sigma_item_code` - Linked Stock Item
- `sigma_maintenance_schedule` - Maintenance Schedule
- `sigma_purchase_request` - Purchase Request
- `sigma_purchase_receipt` - Purchase Receipt
- `sigma_disposal_order` - Disposal Sales Order
- `requires_maintenance` - Maintenance flag
- `maintenance_frequency` - Maintenance frequency
- `sigma_last_stock_sync` - Last sync timestamp
- `sigma_last_support_sync` - Last support sync

**Item DocType:**
- `sigma_asset` - Linked Sigma Asset
- `sigma_asset_category` - Asset category
- `sigma_location` - Asset location
- `sigma_is_security_asset` - Security asset flag

**Maintenance Schedule DocType:**
- `sigma_asset` - Linked Asset
- `sigma_asset_location` - Asset location
- `sigma_asset_category` - Asset category

**Maintenance Visit DocType:**
- `sigma_asset` - Linked Asset
- `sigma_incident` - Related Incident
- `sigma_incident_type` - Incident type
- `sigma_priority` - Priority level

**Purchase Receipt Item DocType:**
- `sigma_is_security_asset` - Security asset flag
- `sigma_asset` - Created Asset reference
- `sigma_asset_category` - Asset category
- `sigma_location` - Asset location

**Visitor/Contact DocTypes:**
- Bidirectional linking fields

**Case Record DocType:**
- `sigma_ticket` - Helpdesk Ticket
- `sigma_project` - Project

**Incident Report DocType:**
- `sigma_maintenance_visit` - Maintenance Visit

## Usage Examples

### Example 1: Create Asset with Auto-Sync

```python
# Create asset - automatically syncs to Stock and creates Maintenance Schedule
asset = frappe.get_doc({
    "doctype": "Asset",
    "asset_name": "Security Camera - Main Gate",
    "asset_category": "Surveillance",
    "location": "Main Gate",
    "purchase_amount": 50000,
    "requires_maintenance": 1,
    "maintenance_frequency": "Monthly"
})
asset.insert()

# Asset is now synced to:
# 1. Stock Item (sigma_item_code populated)
# 2. Maintenance Schedule (sigma_maintenance_schedule populated)
```

### Example 2: Create Maintenance Request

```python
# Create maintenance request for an asset
visit_name = SupportIntegration.create_maintenance_request(
    asset_name="ASSET-00001",
    issue_description="Camera not recording properly",
    priority="High"
)

# Maintenance Visit created and asset status updated to "Under Maintenance"
```

### Example 3: Purchase Receipt → Asset

```python
# Create Purchase Receipt with security asset flag
pr = frappe.get_doc({
    "doctype": "Purchase Receipt",
    "supplier": "Security Equipment Ltd",
    "items": [{
        "item_code": "CAM-001",
        "qty": 1,
        "rate": 50000,
        "sigma_is_security_asset": 1,  # Flag as security asset
        "sigma_asset_category": "Surveillance",
        "sigma_location": "Main Gate"
    }]
})
pr.insert()
pr.submit()

# Asset automatically created from Purchase Receipt
```

### Example 4: Manual Sync

```python
# Manually trigger sync for specific asset
from sigma.sigma_erpnext_integrations.api.integration_api import SigmaIntegrationAPI

SigmaIntegrationAPI.manual_sync(
    source_doctype="Asset",
    source_name="ASSET-00001",
    target_integration="support"  # or "stock", "buying", etc.
)
```

### Example 5: Get Integration Status

```python
# Check integration status for an asset
status = SigmaIntegrationAPI.get_integration_status("Asset", "ASSET-00001")

# Returns:
# {
#     "stock": {"synced": True, "target_doc": "ITEM-00001", "last_sync": "2025-10-27 10:00:00"},
#     "support": {"synced": True, "target_doc": "MAINT-SCH-00001", "last_sync": "2025-10-27 10:00:00"}
# }
```

## Integration Hooks

All hooks are configured in `hooks.py` and automatically registered:

### Document Events (Real-Time Sync)

- **Asset**: `after_insert`, `on_update` → Stock & Support sync
- **Item**: `on_update` → Asset sync
- **Purchase Receipt**: `on_submit` → Asset creation
- **Maintenance Visit**: `on_submit`, `on_update` → Asset status update
- **Incident Report**: `after_insert` → Maintenance Visit creation
- **Visitor**: `after_insert`, `on_update` → Contact sync
- **Case Record**: `after_insert`, `on_update` → Ticket & Project sync

### Scheduled Tasks (Batch Sync)

- **Hourly**: Sync pending assets, sync maintenance schedules
- **Daily**: Full sync, cleanup old logs (90+ days)

## Integration Log

All integration operations are logged in **Integration Log** DocType:

**Fields:**
- Integration Type
- Status (Success/Failed/Pending)
- Timestamp
- Source DocType/Name
- Target DocType/Name
- Details (JSON)
- Error Message

**Access:** Navigate to **Sigma ERPNext Integrations > Integration Log**

## Error Handling

The integration uses the `@safe_integration_call` decorator for robust error handling:

- **Errors are logged** but don't block document save
- **User notifications** via msgprint for integration warnings
- **Detailed error logs** in Error Log DocType
- **Integration Log** tracks all operations

## Troubleshooting

### Integration Not Working

1. Check if ERPNext is installed:
   ```python
   frappe.get_installed_apps()
   ```

2. Check integration settings:
   ```
   Setup > Sigma Integration Settings
   ```

3. Check Integration Log for errors:
   ```
   Sigma ERPNext Integrations > Integration Log
   ```

### Custom Fields Not Appearing

Reinstall custom fields:
```python
from sigma.sigma_erpnext_integrations.custom_fields import install_custom_fields
install_custom_fields()
```

### Sync Not Happening

1. Check if auto-sync is enabled in Integration Settings
2. Check scheduler is running: `bench doctor`
3. Manually trigger sync using API methods

## API Reference

See individual integration modules for detailed API documentation:

- `api/integration_api.py` - Core API functions
- `api/stock_integration.py` - Stock integration
- `api/support_integration.py` - Support/Maintenance integration
- `api/buying_integration.py` - Buying integration
- `api/selling_integration.py` - Selling integration
- `api/crm_integration.py` - CRM integration
- `api/projects_integration.py` - Projects integration
- `api/helpdesk_integration.py` - Helpdesk integration

## Support

For issues or questions:
- Check Integration Log for error details
- Review Error Log for stack traces
- Contact: info@prismod.co.ke

## License

MIT License - Copyright (c) 2025 Prismod Technologies Limited

