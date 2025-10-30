"""
Selling/Disposal Integration Module

Handles integration between Sigma Asset Management and ERPNext Selling module
for asset disposal workflows
"""

import frappe
from frappe import _
from frappe.utils import now, flt
from typing import Dict, Any
from .integration_api import SigmaIntegrationAPI


class SellingIntegration:
    """Manages Asset Disposal ↔ Sales Order/Delivery synchronization"""
    
    @staticmethod
    @frappe.whitelist()
    def create_disposal_request(asset_name: str, disposal_reason: str, 
                                estimated_value: float = 0) -> str:
        """Create Sales Order for asset disposal"""
        if not frappe.has_permission("Sales Order", "create"):
            frappe.throw(_("Insufficient permissions"))
        
        asset = frappe.get_doc("Asset", asset_name)
        
        # Create Sales Order for disposal
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": "Asset Disposal",
            "company": frappe.defaults.get_user_default("Company"),
            "transaction_date": now(),
            "delivery_date": now(),
            "sigma_asset": asset.name,
            "sigma_disposal_reason": disposal_reason,
            "items": [{
                "item_code": asset.get("sigma_item_code"),
                "item_name": asset.asset_name,
                "qty": 1,
                "rate": flt(estimated_value),
                "sigma_asset": asset.name
            }]
        })
        
        so.insert()
        
        # Update asset status
        frappe.db.set_value("Asset", asset_name, "status", "Disposed")
        frappe.db.set_value("Asset", asset_name, "sigma_disposal_order", so.name)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Asset Disposal Request",
            status="Success",
            source_doctype="Asset",
            source_name=asset_name,
            target_doctype="Sales Order",
            target_name=so.name
        )
        
        return so.name

