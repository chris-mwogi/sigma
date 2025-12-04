# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Offline Sync API for Mobile App
"""

import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime
import json


@frappe.whitelist()
def sync_offline_data(data):
    """
    Sync offline data from mobile app to server
    
    Args:
        data: JSON string containing offline changes
    
    Returns:
        Sync results with success/failure for each item
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        results = {
            "success": True,
            "synced": [],
            "failed": [],
            "timestamp": now_datetime()
        }
        
        # Process work order updates
        if "work_orders" in data:
            for wo_data in data["work_orders"]:
                try:
                    wo = frappe.get_doc("Asset Work Order", wo_data["name"])
                    
                    # Check permission
                    if wo.assigned_to != frappe.session.user:
                        results["failed"].append({
                            "type": "work_order",
                            "name": wo_data["name"],
                            "error": "Permission denied"
                        })
                        continue
                    
                    # Update fields
                    if "workflow_state" in wo_data:
                        wo.workflow_state = wo_data["workflow_state"]
                    
                    if "actual_start_date" in wo_data:
                        wo.actual_start_date = wo_data["actual_start_date"]
                    
                    if "actual_end_date" in wo_data:
                        wo.actual_end_date = wo_data["actual_end_date"]
                    
                    if "completion_notes" in wo_data:
                        wo.completion_notes = wo_data["completion_notes"]
                    
                    if "actual_cost" in wo_data:
                        wo.actual_cost = wo_data["actual_cost"]
                    
                    # Update checklist items
                    if "checklist_items" in wo_data and hasattr(wo, "checklist_items"):
                        for item_data in wo_data["checklist_items"]:
                            for item in wo.checklist_items:
                                if item.task == item_data["task"]:
                                    item.is_completed = item_data["is_completed"]
                                    if item_data["is_completed"]:
                                        item.completed_by = frappe.session.user
                                        item.completed_at = item_data.get("completed_at", now_datetime())
                    
                    wo.save(ignore_permissions=True)
                    
                    # Submit if completed
                    if wo.workflow_state == "Completed" and wo.docstatus == 0:
                        wo.submit()
                    
                    results["synced"].append({
                        "type": "work_order",
                        "name": wo.name,
                        "status": "success"
                    })
                
                except Exception as e:
                    frappe.log_error(f"Error syncing work order {wo_data.get('name')}: {str(e)}")
                    results["failed"].append({
                        "type": "work_order",
                        "name": wo_data.get("name"),
                        "error": str(e)
                    })
        
        # Process asset updates
        if "assets" in data:
            for asset_data in data["assets"]:
                try:
                    asset = frappe.get_doc("Asset", asset_data["name"])
                    
                    # Update fields
                    if "asset_location" in asset_data:
                        asset.asset_location = asset_data["asset_location"]
                    
                    if "notes" in asset_data:
                        asset.notes = asset_data["notes"]
                    
                    asset.save(ignore_permissions=True)
                    
                    results["synced"].append({
                        "type": "asset",
                        "name": asset.name,
                        "status": "success"
                    })
                
                except Exception as e:
                    frappe.log_error(f"Error syncing asset {asset_data.get('name')}: {str(e)}")
                    results["failed"].append({
                        "type": "asset",
                        "name": asset_data.get("name"),
                        "error": str(e)
                    })
        
        frappe.db.commit()
        
        if results["failed"]:
            results["success"] = False
        
        return results
    
    except Exception as e:
        frappe.log_error(f"Error in offline sync: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_offline_data_package(user=None):
    """
    Get data package for offline use
    
    Args:
        user: User email (defaults to current user)
    
    Returns:
        Package containing work orders, assets, and reference data
    """
    try:
        if not user:
            user = frappe.session.user
        
        # Get assigned work orders
        work_orders = frappe.get_all(
            "Asset Work Order",
            filters={
                "assigned_to": user,
                "workflow_state": ["in", ["Scheduled", "Assigned", "In Progress"]],
                "docstatus": ["<", 2]
            },
            fields=["*"],
            limit=50
        )
        
        # Get related assets
        asset_names = [wo["asset"] for wo in work_orders if wo.get("asset")]
        assets = []
        if asset_names:
            assets = frappe.get_all(
                "Asset",
                filters={"name": ["in", asset_names]},
                fields=["*"]
            )
        
        # Get reference data
        locations = frappe.get_all("Asset Location", fields=["*"], limit=100)
        categories = frappe.get_all("Asset Category Sigma", fields=["*"], limit=50)
        
        return {
            "success": True,
            "data": {
                "work_orders": work_orders,
                "assets": assets,
                "locations": locations,
                "categories": categories,
                "timestamp": now_datetime(),
                "user": user
            }
        }
    
    except Exception as e:
        frappe.log_error(f"Error creating offline data package: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

