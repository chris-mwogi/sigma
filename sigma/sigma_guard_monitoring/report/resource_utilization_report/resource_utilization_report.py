# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Resource Utilization Report
	Shows resource allocation and utilization rates by type and location
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "resource_type",
			"label": _("Resource Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "total_resources",
			"label": _("Total Resources"),
			"fieldtype": "Int",
			"width": 130
		},
		{
			"fieldname": "available",
			"label": _("Available"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "deployed",
			"label": _("Deployed"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "on_leave",
			"label": _("On Leave"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "inactive",
			"label": _("Inactive"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "utilization_rate",
			"label": _("Utilization Rate"),
			"fieldtype": "Percent",
			"width": 130
		}
	]


def get_data(filters):
	"""Get report data"""
	conditions = get_conditions(filters)

	# Get resource counts by type and status
	query = f"""
		SELECT
			resource_type,
			COUNT(*) as total_resources,
			SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) as available,
			SUM(CASE WHEN status = 'Deployed' THEN 1 ELSE 0 END) as deployed,
			SUM(CASE WHEN status = 'On Leave' THEN 1 ELSE 0 END) as on_leave,
			SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive
		FROM `tabSecurity Resource`
		WHERE 1=1
		{conditions}
		GROUP BY resource_type
		ORDER BY resource_type
	"""

	data = frappe.db.sql(query, filters or {}, as_dict=1)
	
	# Calculate utilization rate for each type
	for row in data:
		if row.total_resources > 0:
			# Utilization = (Deployed + On Leave) / Total
			utilized = (row.deployed or 0) + (row.on_leave or 0)
			row.utilization_rate = utilized / row.total_resources
		else:
			row.utilization_rate = 0
	
	return data


def get_conditions(filters):
	"""Build SQL conditions from filters"""
	conditions = []

	if filters and filters.get("resource_type"):
		conditions.append("AND resource_type = %(resource_type)s")

	if filters and filters.get("status"):
		conditions.append("AND status = %(status)s")

	return " ".join(conditions)

