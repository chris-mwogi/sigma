"""
Hook wrapper functions for Support Integration

These functions are called by Frappe's hook system and delegate to the
SupportIntegration class methods.
"""

import frappe
from sigma.sigma_erpnext_integrations.api.support_integration import SupportIntegration


def sync_asset_maintenance(doc, method=None):
	"""
	Hook: Called when Asset is inserted or updated
	Creates/updates Maintenance Schedule for assets requiring maintenance
	
	Args:
		doc: Asset document
		method: Hook method name (after_insert, on_update, etc.)
	"""
	SupportIntegration.sync_asset_maintenance(doc, method)


def update_asset_from_maintenance_visit(doc, method=None):
	"""
	Hook: Called when Maintenance Visit is submitted or updated
	Updates Asset status and maintenance history
	
	Args:
		doc: Maintenance Visit document
		method: Hook method name (on_submit, on_update, etc.)
	"""
	SupportIntegration.update_asset_from_maintenance_visit(doc, method)


def create_maintenance_visit_from_incident(doc, method=None):
	"""
	Hook: Called when Incident Report is inserted
	Creates Maintenance Visit for incidents requiring maintenance
	
	Args:
		doc: Incident Report document
		method: Hook method name (after_insert, etc.)
	"""
	SupportIntegration.create_maintenance_visit_from_incident(doc, method)

