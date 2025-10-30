"""
Hook wrapper functions for Projects Integration

These wrapper functions are required because Frappe's hook system
expects module-level functions, not class methods.
"""

import frappe
from sigma.sigma_erpnext_integrations.api.projects_integration import ProjectsIntegration


def sync_case_to_project(doc, method=None):
	"""
	Hook: Called when Case Record is inserted or updated
	
	Args:
		doc: Case Record document
		method: Hook method (after_insert, on_update, etc.)
	"""
	ProjectsIntegration.sync_case_to_project(doc, method)

