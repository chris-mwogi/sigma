"""
Hook wrapper functions for Helpdesk Integration

These wrapper functions are required because Frappe's hook system
expects module-level functions, not class methods.
"""

import frappe
from sigma.sigma_erpnext_integrations.api.helpdesk_integration import HelpdeskIntegration


def sync_case_to_ticket(doc, method=None):
	"""
	Hook: Called when Case Record is inserted or updated
	
	Args:
		doc: Case Record document
		method: Hook method (after_insert, on_update, etc.)
	"""
	HelpdeskIntegration.sync_case_to_ticket(doc, method)

