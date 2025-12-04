# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "case_id",
			"label": _("Case ID"),
			"fieldtype": "Link",
			"options": "Case",
			"width": 150
		},
		{
			"fieldname": "case_title",
			"label": _("Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "severity",
			"label": _("Severity"),
			"fieldtype": "Link",
			"options": "Case Severity Matrix",
			"width": 100
		},
		{
			"fieldname": "case_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Case Category",
			"width": 150
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "date_reported",
			"label": _("Reported Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "sla_due_date",
			"label": _("SLA Due Date"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "assigned_case_manager",
			"label": _("Assigned To"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "confidentiality_level",
			"label": _("Confidentiality"),
			"fieldtype": "Data",
			"width": 120
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			c.name as case_id,
			c.case_title,
			c.status,
			c.severity,
			c.case_category,
			c.risk_score,
			c.date_reported,
			c.sla_due_date,
			c.assigned_case_manager,
			c.confidentiality_level
		FROM
			`tabCase` c
		WHERE
			c.docstatus < 2
			{conditions}
		ORDER BY
			c.risk_score DESC, c.date_reported DESC
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("c.date_reported >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("c.date_reported <= %(to_date)s")

	if filters.get("status"):
		conditions.append("c.status = %(status)s")

	if filters.get("severity"):
		conditions.append("c.severity = %(severity)s")

	if filters.get("case_category"):
		conditions.append("c.case_category = %(case_category)s")

	if filters.get("assigned_to"):
		conditions.append("c.assigned_case_manager = %(assigned_to)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# Status distribution
	status_counts = {}
	severity_counts = {}
	category_counts = {}
	
	for row in data:
		status = row.get("status") or "Unknown"
		severity = row.get("severity") or "Unknown"
		category = row.get("case_category") or "Unknown"
		
		status_counts[status] = status_counts.get(status, 0) + 1
		severity_counts[severity] = severity_counts.get(severity, 0) + 1
		category_counts[category] = category_counts.get(category, 0) + 1
	
	return {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [
				{
					"name": "Cases by Status",
					"values": list(status_counts.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#4CAF50", "#FFC107", "#F44336", "#2196F3", "#9E9E9E"]
	}

