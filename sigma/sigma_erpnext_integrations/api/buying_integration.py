"""
Buying/Acquisition Integration Module

Handles integration between Sigma Asset Management and ERPNext Buying module
for asset procurement and acquisition workflows
"""

import frappe
from frappe import _
from frappe.utils import now, flt
from typing import Dict, Any, Optional
from .integration_api import SigmaIntegrationAPI, IntegrationError


class BuyingIntegration:
    """
    Manages Asset Procurement ↔ Purchase Order/Receipt synchronization
    
    Features:
    - Create Purchase Request for new assets
    - Convert Purchase Receipt to Asset
    - Track procurement status
    - Link suppliers to assets
    """
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def create_asset_from_purchase_receipt(pr_doc, method=None):
        """
        Automatically create Asset from Purchase Receipt
        
        Args:
            pr_doc: Purchase Receipt document
            method: Hook method (on_submit)
        """
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("buying"):
            return
        
        # Only process if Purchase Receipt is submitted
        if pr_doc.docstatus != 1:
            return
        
        for item in pr_doc.items:
            # Check if item is marked as security asset
            if item.get("sigma_is_security_asset") or item.get("is_fixed_asset"):
                BuyingIntegration._create_asset_from_pr_item(pr_doc, item)
    
    @staticmethod
    def _create_asset_from_pr_item(pr_doc, item):
        """Create Asset from Purchase Receipt item"""
        
        # Check if asset already exists
        if frappe.db.exists("Asset", {"sigma_purchase_receipt": pr_doc.name, 
                                     "sigma_pr_item": item.name}):
            return
        
        asset = frappe.get_doc({
            "doctype": "Asset",
            "asset_name": item.item_name,
            "asset_category": item.get("sigma_asset_category") or "Security Equipment",
            "item_code": item.item_code,
            "company": pr_doc.company,
            "purchase_date": pr_doc.posting_date,
            "purchase_amount": flt(item.amount),
            "supplier": pr_doc.supplier,
            "location": item.get("sigma_location"),
            "status": "Operational",
            
            # Link back to Purchase Receipt
            "sigma_purchase_receipt": pr_doc.name,
            "sigma_pr_item": item.name,
            "sigma_item_code": item.item_code,
            
            # Additional details
            "description": item.description,
            "warranty_expiry_date": item.get("warranty_expiry_date"),
        })
        
        asset.insert(ignore_permissions=True)
        
        # Update Purchase Receipt item with asset reference
        frappe.db.set_value("Purchase Receipt Item", item.name, 
                          "sigma_asset", asset.name, update_modified=False)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Purchase Receipt to Asset",
            status="Success",
            source_doctype="Purchase Receipt",
            source_name=pr_doc.name,
            target_doctype="Asset",
            target_name=asset.name,
            details={"item_code": item.item_code, "amount": item.amount}
        )
        
        frappe.db.commit()
    
    @staticmethod
    @frappe.whitelist()
    def create_purchase_request(asset_name: str, supplier: str = None, 
                               expected_delivery_date: str = None) -> str:
        """
        Create Purchase Request for asset procurement
        
        Args:
            asset_name: Asset document name (can be draft)
            supplier: Preferred supplier
            expected_delivery_date: Expected delivery date
        
        Returns:
            Purchase Request name
        """
        if not frappe.has_permission("Material Request", "create"):
            frappe.throw(_("Insufficient permissions"))
        
        asset = frappe.get_doc("Asset", asset_name)
        
        if not asset.get("sigma_item_code"):
            frappe.throw(_("Asset not synced to Stock. Please sync first."))
        
        # Create Material Request (Purchase Request)
        mr = frappe.get_doc({
            "doctype": "Material Request",
            "material_request_type": "Purchase",
            "company": frappe.defaults.get_user_default("Company"),
            "transaction_date": now(),
            "schedule_date": expected_delivery_date or now(),
            "sigma_asset": asset.name,
            "items": [{
                "item_code": asset.sigma_item_code,
                "item_name": asset.asset_name,
                "qty": 1,
                "schedule_date": expected_delivery_date or now(),
                "warehouse": frappe.db.get_value("Warehouse", {"is_group": 0}, "name"),
                "sigma_asset": asset.name,
                "description": asset.get("description")
            }]
        })
        
        if supplier:
            mr.items[0].supplier = supplier
        
        mr.insert()
        
        # Update asset with purchase request reference
        frappe.db.set_value("Asset", asset_name, "sigma_purchase_request", mr.name)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Asset to Purchase Request",
            status="Success",
            source_doctype="Asset",
            source_name=asset_name,
            target_doctype="Material Request",
            target_name=mr.name
        )
        
        return mr.name
    
    @staticmethod
    @frappe.whitelist()
    def get_asset_procurement_status(asset_name: str) -> Dict[str, Any]:
        """
        Get procurement status for an asset
        
        Returns dict with procurement workflow status
        """
        asset = frappe.get_doc("Asset", asset_name)
        
        status = {
            "asset": asset.name,
            "purchase_request": asset.get("sigma_purchase_request"),
            "purchase_order": None,
            "purchase_receipt": asset.get("sigma_purchase_receipt"),
            "status": "Not Started"
        }
        
        # Check Purchase Request
        if asset.get("sigma_purchase_request"):
            mr = frappe.get_doc("Material Request", asset.sigma_purchase_request)
            status["purchase_request_status"] = mr.status
            status["status"] = "Purchase Requested"
            
            # Check if Purchase Order created
            po_list = frappe.get_all(
                "Purchase Order Item",
                filters={"material_request": mr.name},
                fields=["parent"],
                limit=1
            )
            
            if po_list:
                status["purchase_order"] = po_list[0].parent
                po = frappe.get_doc("Purchase Order", po_list[0].parent)
                status["purchase_order_status"] = po.status
                status["status"] = "Purchase Ordered"
        
        # Check Purchase Receipt
        if asset.get("sigma_purchase_receipt"):
            pr = frappe.get_doc("Purchase Receipt", asset.sigma_purchase_receipt)
            status["purchase_receipt_status"] = pr.status
            status["status"] = "Received"
        
        return status

