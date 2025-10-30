"""
Stock Integration Module

Handles bidirectional synchronization between ERPNext Assets and Stock Items

REVISED STRATEGY (Item-First Approach):
- ERPNext Assets MUST have an item_code (Item is parent, Asset is child)
- Integration creates Fixed Asset Items from Assets
- Items are marked as is_fixed_asset=1, is_stock_item=0
- Bidirectional sync keeps Item and Asset in sync
"""

import frappe
from frappe import _
from frappe.utils import now, flt
from typing import Dict, Any, Optional
from .integration_api import SigmaIntegrationAPI, IntegrationError


class StockIntegration:
    """
    Manages Asset ↔ Item synchronization (Item-First Approach)

    Features:
    - Create Fixed Asset Item from Asset
    - Update Item when Asset changes
    - Sync Asset updates back to Item
    - Support Purchase Receipt → Item + Asset workflow

    Note: ERPNext Assets require an item_code. This integration creates
    Fixed Asset Items (is_fixed_asset=1, is_stock_item=0) to satisfy
    ERPNext's validation requirements.
    """
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_asset_to_item(asset_doc, method=None):
        """
        Create or update ERPNext Item from Sigma Asset
        
        Args:
            asset_doc: Asset document
            method: Hook method (on_insert, on_update, etc.)
        """
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("stock"):
            return
        
        # Check if Item already exists
        item_code = asset_doc.get("sigma_item_code")
        
        if item_code and frappe.db.exists("Item", item_code):
            # Update existing Item
            item = frappe.get_doc("Item", item_code)
            StockIntegration._update_item_from_asset(item, asset_doc)
            item.save(ignore_permissions=True)
            
            SigmaIntegrationAPI.log_integration(
                integration_type="Asset to Item Update",
                status="Success",
                source_doctype="Asset",
                source_name=asset_doc.name,
                target_doctype="Item",
                target_name=item_code
            )
        else:
            # Create new Item
            item = StockIntegration._create_item_from_asset(asset_doc)
            item.insert(ignore_permissions=True)
            
            # Update Asset with Item reference
            frappe.db.set_value("Asset", asset_doc.name, "sigma_item_code", item.name, update_modified=False)
            frappe.db.set_value("Asset", asset_doc.name, "sigma_last_stock_sync", now(), update_modified=False)
            
            SigmaIntegrationAPI.log_integration(
                integration_type="Asset to Item Creation",
                status="Success",
                source_doctype="Asset",
                source_name=asset_doc.name,
                target_doctype="Item",
                target_name=item.name
            )
        
        frappe.db.commit()
    
    @staticmethod
    def _create_item_from_asset(asset_doc):
        """
        Create Fixed Asset Item from Asset

        Creates an Item with:
        - is_fixed_asset = 1 (marks as Fixed Asset)
        - is_stock_item = 0 (not a stock item, as per ERPNext Fixed Asset requirements)
        - asset_category = from Asset

        This satisfies ERPNext's requirement that Assets must have an item_code.
        """
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": f"ASSET-{asset_doc.name}",
            "item_name": asset_doc.asset_name or asset_doc.name,
            "item_group": StockIntegration._get_item_group(asset_doc),
            "stock_uom": "Nos",
            "is_stock_item": 0,  # Fixed Assets are NOT stock items
            "is_fixed_asset": 1,  # Mark as Fixed Asset
            "asset_category": asset_doc.get("asset_category"),  # Link to Asset Category
            "disabled": 0,
            "description": asset_doc.get("description") or f"Fixed Asset: {asset_doc.asset_name}",

            # Custom fields for Sigma integration
            "sigma_asset": asset_doc.name,
            "sigma_asset_category": asset_doc.get("asset_category"),
            "sigma_location": asset_doc.get("location"),
            "sigma_is_security_asset": 1,

            # Standard fields
            "valuation_rate": flt(asset_doc.get("gross_purchase_amount", 0)),
            "standard_rate": flt(asset_doc.get("gross_purchase_amount", 0)),
        })

        return item
    
    @staticmethod
    def _update_item_from_asset(item, asset_doc):
        """Update existing Fixed Asset Item with Asset data"""
        item.item_name = asset_doc.asset_name or asset_doc.name
        item.description = asset_doc.get("description") or f"Fixed Asset: {asset_doc.asset_name}"
        item.sigma_location = asset_doc.get("location")
        item.sigma_asset_category = asset_doc.get("asset_category")

        # Update valuation if purchase amount changed
        if asset_doc.get("gross_purchase_amount"):
            item.valuation_rate = flt(asset_doc.gross_purchase_amount)
            item.standard_rate = flt(asset_doc.gross_purchase_amount)
    
    @staticmethod
    def _get_item_group(asset_doc) -> str:
        """
        Determine Item Group based on Asset Category

        Maps Asset Categories to ERPNext Item Groups.
        Creates "Fixed Assets" group if it doesn't exist.
        """
        category = asset_doc.get("asset_category")

        # Default mapping - all assets go to "Fixed Assets" group
        category_mapping = {
            "Security Equipment": "Fixed Assets",
            "Access Control": "Fixed Assets",
            "Surveillance": "Fixed Assets",
            "Communication": "Fixed Assets",
            "Vehicles": "Fixed Assets",
            "IT Equipment": "Fixed Assets",
            "Computers": "Fixed Assets",
            "Furniture and Fixtures": "Fixed Assets",
            "Office Equipment": "Fixed Assets",
        }

        item_group = category_mapping.get(category, "Fixed Assets")

        # Ensure Item Group exists
        if not frappe.db.exists("Item Group", item_group):
            # Create Fixed Assets item group
            try:
                ig = frappe.get_doc({
                    "doctype": "Item Group",
                    "item_group_name": item_group,
                    "parent_item_group": "All Item Groups",
                    "is_group": 0
                })
                ig.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as e:
                # If creation fails, use default "All Item Groups"
                frappe.log_error(f"Failed to create Item Group {item_group}: {str(e)}")
                return "All Item Groups"

        return item_group
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_item_to_asset(item_doc, method=None):
        """
        Sync changes from Item back to Asset
        
        Args:
            item_doc: Item document
            method: Hook method
        """
        if not item_doc.get("sigma_asset"):
            return
        
        if not frappe.db.exists("Asset", item_doc.sigma_asset):
            return
        
        # Update Asset with Item changes
        asset = frappe.get_doc("Asset", item_doc.sigma_asset)
        
        # Only sync specific fields to avoid conflicts
        if item_doc.get("description"):
            asset.description = item_doc.description
        
        asset.save(ignore_permissions=True)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Item to Asset Update",
            status="Success",
            source_doctype="Item",
            source_name=item_doc.name,
            target_doctype="Asset",
            target_name=asset.name
        )
    
    @staticmethod
    @frappe.whitelist()
    def create_stock_entry_for_asset(asset_name: str, warehouse: str, qty: float = 1.0):
        """
        Create Stock Entry to receive asset into warehouse

        Note: This is for Fixed Assets that need stock tracking.
        Most Fixed Assets don't need stock entries.

        Args:
            asset_name: Asset document name
            warehouse: Target warehouse
            qty: Quantity (default 1.0)
        """
        if not frappe.has_permission("Stock Entry", "create"):
            frappe.throw(_("Insufficient permissions"))

        asset = frappe.get_doc("Asset", asset_name)

        if not asset.get("sigma_item_code"):
            frappe.throw(_("Asset not synced to Stock. Please sync first."))

        # Get the item to verify it's a Fixed Asset
        item = frappe.get_doc("Item", asset.sigma_item_code)

        if not item.is_fixed_asset:
            frappe.throw(_("Item {0} is not a Fixed Asset").format(item.name))

        # Create Material Receipt
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": frappe.defaults.get_user_default("Company"),
            "posting_date": now(),
            "items": [{
                "item_code": asset.sigma_item_code,
                "qty": qty,
                "t_warehouse": warehouse,
                "basic_rate": flt(asset.get("gross_purchase_amount", 0)),
                "sigma_asset": asset.name
            }]
        })

        stock_entry.insert()
        stock_entry.submit()

        SigmaIntegrationAPI.log_integration(
            integration_type="Asset Stock Entry",
            status="Success",
            source_doctype="Asset",
            source_name=asset_name,
            target_doctype="Stock Entry",
            target_name=stock_entry.name
        )

        return stock_entry.name
    
    @staticmethod
    @frappe.whitelist()
    def get_asset_stock_balance(asset_name: str) -> Dict[str, Any]:
        """
        Get current stock balance for asset across all warehouses
        
        Returns dict with warehouse-wise stock levels
        """
        asset = frappe.get_doc("Asset", asset_name)
        
        if not asset.get("sigma_item_code"):
            return {"error": "Asset not synced to Stock"}
        
        # Get stock balance
        from erpnext.stock.utils import get_stock_balance
        
        warehouses = frappe.get_all("Warehouse", pluck="name")
        balance = {}
        
        for warehouse in warehouses:
            qty = get_stock_balance(asset.sigma_item_code, warehouse)
            if qty > 0:
                balance[warehouse] = qty
        
        return {
            "item_code": asset.sigma_item_code,
            "total_qty": sum(balance.values()),
            "warehouse_wise": balance
        }

