# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Mobile Asset Scanner API - QR Code / Barcode scanning
"""

import frappe
from frappe import _
import json


@frappe.whitelist()
def scan_asset(code, code_type="qr"):
    """
    Scan asset by QR code or barcode
    
    Args:
        code: QR code or barcode value
        code_type: "qr" or "barcode" (default: "qr")
    
    Returns:
        Asset details if found
    """
    try:
        # Try to find asset by serial number or asset code
        asset = None
        
        # First try exact match on name
        if frappe.db.exists("Asset", code):
            asset = frappe.get_doc("Asset", code)
        # Then try serial number
        elif frappe.db.exists("Asset", {"serial_no": code}):
            asset_name = frappe.db.get_value("Asset", {"serial_no": code}, "name")
            asset = frappe.get_doc("Asset", asset_name)
        # Then try asset code (custom field)
        elif frappe.db.exists("Asset", {"asset_code": code}):
            asset_name = frappe.db.get_value("Asset", {"asset_code": code}, "name")
            asset = frappe.get_doc("Asset", asset_name)
        
        if not asset:
            return {
                "success": False,
                "error": _("Asset not found with code: {0}").format(code)
            }
        
        # Get location details
        location = None
        if asset.asset_location:
            location = frappe.get_doc("Asset Location", asset.asset_location)
        
        # Get category details
        category = None
        if asset.asset_category_sigma:
            category = frappe.get_doc("Asset Category Sigma", asset.asset_category_sigma)
        
        # Get recent maintenance history
        maintenance_history = frappe.get_all(
            "Asset Work Order",
            filters={
                "asset": asset.name,
                "workflow_state": "Completed",
                "docstatus": 1
            },
            fields=["name", "work_order_type", "actual_end_date", "completion_notes"],
            order_by="actual_end_date desc",
            limit=5
        )
        
        # Get active work orders
        active_work_orders = frappe.get_all(
            "Asset Work Order",
            filters={
                "asset": asset.name,
                "workflow_state": ["in", ["Scheduled", "Assigned", "In Progress"]],
                "docstatus": ["<", 2]
            },
            fields=["name", "work_order_type", "priority", "workflow_state", "assigned_to"],
            order_by="scheduled_start_date"
        )
        
        # Get health status
        health_data = {
            "health_score": asset.health_score,
            "health_status": asset.health_status,
            "last_health_update": asset.last_health_update
        }
        
        # Get monitored devices
        monitored_devices = frappe.get_all(
            "Monitored Device",
            filters={"asset": asset.name},
            fields=["name", "device_id", "device_type", "status"]
        )
        
        return {
            "success": True,
            "data": {
                "asset": {
                    "name": asset.name,
                    "asset_name": asset.asset_name,
                    "serial_no": asset.serial_no,
                    "asset_code": asset.asset_code if hasattr(asset, "asset_code") else None,
                    "lifecycle_status": asset.lifecycle_status,
                    "criticality_rating": asset.criticality_rating,
                    "purchase_date": asset.purchase_date,
                    "warranty_expiry_date": asset.warranty_expiry_date,
                    "total_operating_hours": asset.total_operating_hours,
                    "image": asset.image
                },
                "location": {
                    "name": location.name if location else None,
                    "location_name": location.location_name if location else None,
                    "gps_latitude": location.gps_latitude if location else None,
                    "gps_longitude": location.gps_longitude if location else None,
                    "address": location.address if location else None
                } if location else None,
                "category": {
                    "name": category.name if category else None,
                    "category_name": category.category_name if category else None,
                    "asset_type": category.asset_type if category else None
                } if category else None,
                "health": health_data,
                "maintenance_history": maintenance_history,
                "active_work_orders": active_work_orders,
                "monitored_devices": monitored_devices
            }
        }
    
    except Exception as e:
        frappe.log_error(f"Error scanning asset: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def generate_asset_qr(asset_name):
    """
    Generate QR code for an asset
    
    Args:
        asset_name: Asset ID
    
    Returns:
        QR code data URL
    """
    try:
        import qrcode
        import io
        import base64
        
        # Get asset
        asset = frappe.get_doc("Asset", asset_name)
        
        # Generate QR code with asset serial number or name
        qr_data = asset.serial_no or asset.name
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "success": True,
            "data": {
                "qr_code": f"data:image/png;base64,{img_str}",
                "qr_data": qr_data,
                "asset_name": asset.asset_name
            }
        }
    
    except Exception as e:
        frappe.log_error(f"Error generating QR code: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

