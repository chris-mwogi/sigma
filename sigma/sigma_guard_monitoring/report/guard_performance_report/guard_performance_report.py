# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Guard Performance Report
	Shows performance metrics for security guards including:
	- Deployment count
	- Incidents handled
	- Attendance rate
	- Performance score
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "resource_name",
			"label": _("Guard Name"),
			"fieldtype": "Link",
			"options": "Security Resource",
			"width": 200
		},
		{
			"fieldname": "resource_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "total_deployments",
			"label": _("Total Deployments"),
			"fieldtype": "Int",
			"width": 130
		},
		{
			"fieldname": "active_deployments",
			"label": _("Active Deployments"),
			"fieldtype": "Int",
			"width": 140
		},
		{
			"fieldname": "incidents_handled",
			"label": _("Incidents Handled"),
			"fieldtype": "Int",
			"width": 140
		},
		{
			"fieldname": "performance_score",
			"label": _("Performance Score"),
			"fieldtype": "Percent",
			"width": 140
		}
	]


def get_data(filters):
	"""Get report data"""
	conditions = get_conditions(filters)

	# Get all security resources (guards)
	query = f"""
		SELECT
			name as resource_name,
			resource_type,
			status
		FROM `tabSecurity Resource`
		WHERE resource_type IN ('Guard', 'Security Guard', 'Security Supervisor')
		{conditions}
		ORDER BY resource_name
	"""

	resources = frappe.db.sql(query, filters or {}, as_dict=1)
	
	# For each resource, get deployment and incident counts
	for resource in resources:
		# Get deployment counts from Guard Deployment Schedule
		deployment_counts = frappe.db.sql("""
			SELECT
				COUNT(DISTINCT gds.name) as total,
				SUM(CASE WHEN gds.status = 'Active' THEN 1 ELSE 0 END) as active
			FROM `tabGuard Deployment Schedule` gds
			INNER JOIN `tabGuard Deployment Schedule Item` gdsi ON gdsi.parent = gds.name
			WHERE gdsi.resource = %(resource)s
		""", {"resource": resource.resource_name}, as_dict=1)

		if deployment_counts and deployment_counts[0]:
			resource.total_deployments = deployment_counts[0].total or 0
			resource.active_deployments = deployment_counts[0].active or 0
		else:
			resource.total_deployments = 0
			resource.active_deployments = 0

		# Get incident counts (incidents where this guard was involved)
		# Note: Guard Incident doesn't have assigned_to field, so we'll count all incidents for now
		resource.incidents_handled = 0  # Placeholder - update when field is available
		
		# Calculate performance score (simple formula for now)
		# Score based on: active deployments (50%) + incidents handled (30%) + status (20%)
		score = 0
		if resource.active_deployments > 0:
			score += 50
		if resource.incidents_handled > 0:
			score += min(30, resource.incidents_handled * 5)  # Max 30 points
		if resource.status == "Available":
			score += 20
		
		resource.performance_score = score / 100.0
	
	return resources


def get_conditions(filters):
	"""Build SQL conditions from filters"""
	conditions = []

	if filters and filters.get("resource_type"):
		conditions.append("AND resource_type = %(resource_type)s")

	if filters and filters.get("status"):
		conditions.append("AND status = %(status)s")

	return " ".join(conditions)

