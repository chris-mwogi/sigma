"""
Hook wrapper functions for Stock Integration

These functions are called by Frappe's hook system and delegate to the
StockIntegration class methods.

Frappe's hook system expects module-level functions, not class methods.
These wrappers provide the correct interface while keeping the main
integration logic organized in the StockIntegration class.
"""

import frappe
from sigma.sigma_erpnext_integrations.api.stock_integration import StockIntegration


def sync_asset_to_item(doc, method=None):
	"""
	Hook: Called when Asset is inserted or updated
	Syncs Asset data to Fixed Asset Item
	
	Args:
		doc: Asset document
		method: Hook method name (after_insert, on_update, etc.)
	"""
	StockIntegration.sync_asset_to_item(doc, method)


def sync_item_to_asset(doc, method=None):
	"""
	Hook: Called when Item is updated
	Syncs Fixed Asset Item data back to Asset
	
	Args:
		doc: Item document
		method: Hook method name (on_update, etc.)
	"""
	StockIntegration.sync_item_to_asset(doc, method)

