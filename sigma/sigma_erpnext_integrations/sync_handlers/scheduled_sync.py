"""
Scheduled Synchronization Handlers

Handles batch synchronization tasks that run on schedule
"""

import frappe
from frappe.utils import now, add_days
from typing import List


def sync_pending_assets():
    """
    Sync assets that haven't been synced to Stock yet
    Runs hourly
    """
    if not frappe.db.exists("DocType", "Asset"):
        return
    
    # Get assets without Item sync
    assets = frappe.get_all(
        "Asset",
        filters={
            "sigma_item_code": ["is", "not set"],
            "status": ["!=", "Disposed"]
        },
        limit=50  # Process 50 at a time
    )
    
    from sigma.sigma_erpnext_integrations.api.stock_integration import StockIntegration
    
    for asset_name in assets:
        try:
            asset = frappe.get_doc("Asset", asset_name.name)
            StockIntegration.sync_asset_to_item(asset)
        except Exception as e:
            frappe.log_error(f"Error syncing asset {asset_name.name}: {str(e)}")
    
    frappe.db.commit()


def sync_maintenance_schedules():
    """
    Sync maintenance schedules for assets that require maintenance
    Runs hourly
    """
    if not frappe.db.exists("DocType", "Asset"):
        return
    
    # Get assets that require maintenance but don't have schedule
    assets = frappe.get_all(
        "Asset",
        filters={
            "requires_maintenance": 1,
            "sigma_maintenance_schedule": ["is", "not set"],
            "status": ["!=", "Disposed"]
        },
        limit=50
    )
    
    from sigma.sigma_erpnext_integrations.api.support_integration import SupportIntegration
    
    for asset_name in assets:
        try:
            asset = frappe.get_doc("Asset", asset_name.name)
            SupportIntegration.sync_asset_maintenance(asset)
        except Exception as e:
            frappe.log_error(f"Error syncing maintenance for {asset_name.name}: {str(e)}")
    
    frappe.db.commit()


def sync_all_integrations():
    """
    Full synchronization of all integrations
    Runs daily
    """
    from sigma.sigma_erpnext_integrations.api.integration_api import SigmaIntegrationAPI
    
    settings = SigmaIntegrationAPI.get_integration_settings()
    
    if not settings.get("auto_sync"):
        return
    
    # Sync assets
    sync_pending_assets()
    sync_maintenance_schedules()
    
    # Update last sync time
    if frappe.db.exists("DocType", "Sigma Integration Settings"):
        frappe.db.set_value("Sigma Integration Settings", None, {
            "last_sync": now(),
            "sync_status": "Completed"
        })
    
    frappe.db.commit()


def cleanup_old_logs():
    """
    Clean up old integration logs (older than 90 days)
    Runs daily
    """
    if not frappe.db.exists("DocType", "Integration Log"):
        return
    
    # Delete logs older than 90 days
    cutoff_date = add_days(now(), -90)
    
    old_logs = frappe.get_all(
        "Integration Log",
        filters={
            "timestamp": ["<", cutoff_date]
        },
        pluck="name"
    )
    
    for log_name in old_logs:
        try:
            frappe.delete_doc("Integration Log", log_name, force=True)
        except Exception as e:
            frappe.log_error(f"Error deleting log {log_name}: {str(e)}")
    
    frappe.db.commit()
    
    if old_logs:
        frappe.logger().info(f"Cleaned up {len(old_logs)} old integration logs")

