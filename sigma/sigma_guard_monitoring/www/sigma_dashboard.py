# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url


def get_context(context):
	"""
	Get context for the Sigma Guard Monitoring Dashboard page.
	
	This function is called when accessing /sigma-dashboard route.
	It prepares the context for rendering the dashboard HTML template.
	"""
	
	# Check if user has permission to access dashboard
	if not frappe.has_permission("Security Resource", "read"):
		frappe.throw("You do not have permission to access this dashboard", frappe.PermissionError)
	
	# Prepare context
	context = {
		"title": "Sigma Guard Monitoring Dashboard",
		"page_title": "Sigma Guard Monitoring Dashboard",
		"no_cache": 1,
		"csrf_token": frappe.sessions.get_csrf_token(),
	}
	
	return context

