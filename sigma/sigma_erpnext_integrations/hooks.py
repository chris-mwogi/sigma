"""
Sigma ERPNext Integrations - Hooks Configuration

This file defines all integration hooks for bidirectional synchronization
between Sigma and ERPNext modules.
"""

app_name = "sigma_erpnext_integrations"

# Document Events - Integration Hooks
# ====================================

doc_events = {
    # Asset Management ↔ Stock Integration
    "Asset": {
        "after_insert": [
            "sigma.sigma_erpnext_integrations.api.stock_integration.StockIntegration.sync_asset_to_item",
            "sigma.sigma_erpnext_integrations.api.support_integration.SupportIntegration.sync_asset_maintenance",
        ],
        "on_update": [
            "sigma.sigma_erpnext_integrations.api.stock_integration.StockIntegration.sync_asset_to_item",
            "sigma.sigma_erpnext_integrations.api.support_integration.SupportIntegration.sync_asset_maintenance",
        ],
    },
    
    # Item ↔ Asset Sync (bidirectional)
    "Item": {
        "on_update": "sigma.sigma_erpnext_integrations.api.stock_integration.StockIntegration.sync_item_to_asset",
    },
    
    # Purchase Receipt ↔ Asset Creation
    "Purchase Receipt": {
        "on_submit": "sigma.sigma_erpnext_integrations.api.buying_integration.BuyingIntegration.create_asset_from_purchase_receipt",
    },
    
    # Maintenance Visit ↔ Asset Status Update
    "Maintenance Visit": {
        "on_submit": "sigma.sigma_erpnext_integrations.api.support_integration.SupportIntegration.update_asset_from_maintenance_visit",
        "on_update": "sigma.sigma_erpnext_integrations.api.support_integration.SupportIntegration.update_asset_from_maintenance_visit",
    },
    
    # Incident Report ↔ Maintenance Visit
    "Incident Report": {
        "after_insert": "sigma.sigma_erpnext_integrations.api.support_integration.SupportIntegration.create_maintenance_visit_from_incident",
    },
    
    # Visitor ↔ Contact (CRM)
    "Visitor": {
        "after_insert": "sigma.sigma_erpnext_integrations.api.crm_integration.CRMIntegration.sync_visitor_to_contact",
        "on_update": "sigma.sigma_erpnext_integrations.api.crm_integration.CRMIntegration.sync_visitor_to_contact",
    },
    
    # Case ↔ Ticket (Helpdesk)
    "Case Record": {
        "after_insert": [
            "sigma.sigma_erpnext_integrations.api.helpdesk_integration.HelpdeskIntegration.sync_case_to_ticket",
            "sigma.sigma_erpnext_integrations.api.projects_integration.ProjectsIntegration.sync_case_to_project",
        ],
        "on_update": [
            "sigma.sigma_erpnext_integrations.api.helpdesk_integration.HelpdeskIntegration.sync_case_to_ticket",
        ],
    },
}

# Scheduled Tasks - Batch Synchronization
# ========================================

scheduler_events = {
    # Hourly sync for critical data
    "hourly": [
        "sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_pending_assets",
        "sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_maintenance_schedules",
    ],
    
    # Daily sync for non-critical data
    "daily": [
        "sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_all_integrations",
        "sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.cleanup_old_logs",
    ],
}

# Fixtures - Export/Import Configuration
# =======================================

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["name", "in", [
            "Item-sigma_asset",
            "Item-sigma_asset_category",
            "Item-sigma_location",
            "Item-sigma_is_security_asset",
            "Asset-sigma_item_code",
            "Asset-sigma_maintenance_schedule",
            "Asset-sigma_purchase_request",
            "Asset-sigma_purchase_receipt",
            "Asset-sigma_disposal_order",
            "Maintenance Schedule-sigma_asset",
            "Maintenance Visit-sigma_asset",
            "Maintenance Visit-sigma_incident",
            "Purchase Receipt Item-sigma_is_security_asset",
            "Purchase Receipt Item-sigma_asset",
            "Visitor-sigma_contact",
            "Contact-sigma_visitor",
            "Case Record-sigma_ticket",
            "Case Record-sigma_project",
            "Incident Report-sigma_maintenance_visit",
        ]]]
    },
    {
        "dt": "DocType",
        "filters": [["module", "=", "Sigma ERPNext Integrations"]]
    },
]

# Installation Hooks
# ==================

after_install = "sigma.sigma_erpnext_integrations.install.after_install"
after_migrate = "sigma.sigma_erpnext_integrations.install.after_migrate"

# Uninstallation Hooks
# =====================

before_uninstall = "sigma.sigma_erpnext_integrations.install.before_uninstall"

