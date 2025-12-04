# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Mobile API for Work Orders
"""

import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime, get_datetime
import json


@frappe.whitelist()
def get_my_work_orders(status=None, limit=20):
    """
    Get work orders assigned to current user (mobile-optimized)
    
    Args:
        status: Filter by workflow_state (optional)
        limit: Number of records to return (default: 20)
    
    Returns:
        List of work orders with essential fields only
    """
    user = frappe.session.user
    
    filters = {
        "assigned_to": user,
        "docstatus": ["<", 2]
    }
    
    if status:
        filters["workflow_state"] = status
    
    work_orders = frappe.get_all(
        "Asset Work Order",
        filters=filters,
        fields=[
            "name",
            "asset",
            "asset_name",
            "asset_location",
            "work_order_type",
            "priority",
            "workflow_state",
            "scheduled_start_date",
            "scheduled_end_date",
            "estimated_duration_hours",
            "work_description",
            "is_emergency"
        ],
        order_by="FIELD(priority, 'Emergency', 'Critical', 'High', 'Medium', 'Low'), scheduled_start_date",
        limit_page_length=limit
    )
    
    # Add additional computed fields
    for wo in work_orders:
        # Get asset location details
        if wo.asset_location:
            location = frappe.db.get_value("Asset Location", wo.asset_location, 
                                          ["location_name", "gps_latitude", "gps_longitude"], as_dict=True)
            wo["location_name"] = location.location_name if location else None
            wo["gps_latitude"] = location.gps_latitude if location else None
            wo["gps_longitude"] = location.gps_longitude if location else None
        
        # Strip HTML from description
        if wo.work_description:
            wo["work_description"] = frappe.utils.strip_html_tags(wo.work_description)[:200]
    
    return {
        "success": True,
        "data": work_orders,
        "count": len(work_orders)
    }


@frappe.whitelist()
def get_work_order_details(work_order_name):
    """
    Get detailed work order information (mobile-optimized)
    
    Args:
        work_order_name: Work order ID
    
    Returns:
        Work order details with related information
    """
    try:
        wo = frappe.get_doc("Asset Work Order", work_order_name)
        
        # Check permission
        if wo.assigned_to != frappe.session.user and not frappe.has_permission("Asset Work Order", "read", wo):
            frappe.throw(_("You don't have permission to view this work order"))
        
        # Get asset details
        asset = frappe.get_doc("Asset", wo.asset) if wo.asset else None
        
        # Get location details with GPS
        location = None
        if wo.asset_location:
            location = frappe.get_doc("Asset Location", wo.asset_location)
        
        # Get checklist items
        checklist = []
        if hasattr(wo, "checklist_items"):
            for item in wo.checklist_items:
                checklist.append({
                    "task": item.task,
                    "is_completed": item.is_completed,
                    "completed_by": item.completed_by,
                    "completed_at": item.completed_at
                })
        
        # Get spare parts
        spare_parts = []
        if hasattr(wo, "spare_parts"):
            for part in wo.spare_parts:
                spare_parts.append({
                    "item_code": part.item_code,
                    "item_name": part.item_name,
                    "quantity": part.quantity,
                    "uom": part.uom
                })
        
        return {
            "success": True,
            "data": {
                "work_order": {
                    "name": wo.name,
                    "asset": wo.asset,
                    "asset_name": wo.asset_name,
                    "work_order_type": wo.work_order_type,
                    "priority": wo.priority,
                    "workflow_state": wo.workflow_state,
                    "work_description": wo.work_description,
                    "scheduled_start_date": wo.scheduled_start_date,
                    "scheduled_end_date": wo.scheduled_end_date,
                    "actual_start_date": wo.actual_start_date,
                    "actual_end_date": wo.actual_end_date,
                    "estimated_duration_hours": wo.estimated_duration_hours,
                    "actual_duration_hours": wo.actual_duration_hours,
                    "required_skills": wo.required_skills,
                    "required_tools": wo.required_tools,
                    "safety_requirements": wo.safety_requirements,
                    "is_emergency": wo.is_emergency
                },
                "asset": {
                    "name": asset.name if asset else None,
                    "asset_name": asset.asset_name if asset else None,
                    "serial_no": asset.serial_no if asset else None,
                    "health_score": asset.health_score if asset else None,
                    "health_status": asset.health_status if asset else None
                } if asset else None,
                "location": {
                    "name": location.name if location else None,
                    "location_name": location.location_name if location else None,
                    "gps_latitude": location.gps_latitude if location else None,
                    "gps_longitude": location.gps_longitude if location else None,
                    "address": location.address if location else None
                } if location else None,
                "checklist": checklist,
                "spare_parts": spare_parts
            }
        }
    
    except Exception as e:
        frappe.log_error(f"Error fetching work order details: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def start_work_order_mobile(work_order_name):
    """
    Start a work order from mobile app

    Args:
        work_order_name: Work order ID

    Returns:
        Success status and updated work order
    """
    try:
        wo = frappe.get_doc("Asset Work Order", work_order_name)

        # Check permission
        if wo.assigned_to != frappe.session.user:
            frappe.throw(_("You are not assigned to this work order"))

        if wo.workflow_state not in ["Scheduled", "Assigned"]:
            frappe.throw(_("Work order must be in Scheduled or Assigned state to start"))

        wo.workflow_state = "In Progress"
        wo.actual_start_date = now_datetime()
        wo.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Work order started successfully"),
            "data": {
                "name": wo.name,
                "workflow_state": wo.workflow_state,
                "actual_start_date": wo.actual_start_date
            }
        }

    except Exception as e:
        frappe.log_error(f"Error starting work order: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def complete_work_order_mobile(work_order_name, completion_notes=None, actual_cost=None):
    """
    Complete a work order from mobile app

    Args:
        work_order_name: Work order ID
        completion_notes: Notes about completion (optional)
        actual_cost: Actual cost incurred (optional)

    Returns:
        Success status and updated work order
    """
    try:
        wo = frappe.get_doc("Asset Work Order", work_order_name)

        # Check permission
        if wo.assigned_to != frappe.session.user:
            frappe.throw(_("You are not assigned to this work order"))

        if wo.workflow_state != "In Progress":
            frappe.throw(_("Work order must be in progress to complete"))

        wo.workflow_state = "Completed"
        wo.actual_end_date = now_datetime()

        if completion_notes:
            wo.completion_notes = completion_notes

        if actual_cost:
            wo.actual_cost = actual_cost

        wo.save(ignore_permissions=True)
        wo.submit()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Work order completed successfully"),
            "data": {
                "name": wo.name,
                "workflow_state": wo.workflow_state,
                "actual_end_date": wo.actual_end_date
            }
        }

    except Exception as e:
        frappe.log_error(f"Error completing work order: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def update_checklist_item(work_order_name, task, is_completed):
    """
    Update checklist item status from mobile app

    Args:
        work_order_name: Work order ID
        task: Task description
        is_completed: 1 or 0

    Returns:
        Success status
    """
    try:
        wo = frappe.get_doc("Asset Work Order", work_order_name)

        # Check permission
        if wo.assigned_to != frappe.session.user:
            frappe.throw(_("You are not assigned to this work order"))

        # Find and update checklist item
        updated = False
        if hasattr(wo, "checklist_items"):
            for item in wo.checklist_items:
                if item.task == task:
                    item.is_completed = int(is_completed)
                    if int(is_completed):
                        item.completed_by = frappe.session.user
                        item.completed_at = now_datetime()
                    updated = True
                    break

        if not updated:
            frappe.throw(_("Checklist item not found"))

        wo.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Checklist item updated successfully")
        }

    except Exception as e:
        frappe.log_error(f"Error updating checklist item: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

