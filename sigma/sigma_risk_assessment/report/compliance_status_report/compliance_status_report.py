# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, date_diff


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	"""Return columns for the report"""
	return [
		{
			"fieldname": "name",
			"label": _("Requirement ID"),
			"fieldtype": "Link",
			"options": "Compliance Requirement",
			"width": 140
		},
		{
			"fieldname": "requirement_title",
			"label": _("Requirement Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "requirement_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "regulatory_framework",
			"label": _("Framework"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "compliance_owner",
			"label": _("Owner"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "compliance_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "current_compliance_level",
			"label": _("Compliance %"),
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"fieldname": "priority",
			"label": _("Priority"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "effective_date",
			"label": _("Effective Date"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "last_review_date",
			"label": _("Last Review"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "next_review_date",
			"label": _("Next Review"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "days_to_review",
			"label": _("Days to Review"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "target_compliance_date",
			"label": _("Target Date"),
			"fieldtype": "Date",
			"width": 110
		}
	]


def get_data(filters):
	"""Get data for the report"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			name,
			requirement_title,
			requirement_type,
			regulatory_framework,
			compliance_owner,
			compliance_status,
			current_compliance_level,
			priority,
			effective_date,
			last_review_date,
			next_review_date,
			target_compliance_date
		FROM
			`tabCompliance Requirement`
		WHERE
			1=1
			{conditions}
		ORDER BY
			compliance_status, priority DESC, next_review_date
	""", filters, as_dict=1)
	
	# Calculate days to review
	today = getdate()
	for row in data:
		if row.get("next_review_date"):
			row["days_to_review"] = date_diff(row["next_review_date"], today)
		else:
			row["days_to_review"] = None
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("requirement_type"):
		conditions.append("AND requirement_type = %(requirement_type)s")
	
	if filters.get("regulatory_framework"):
		conditions.append("AND regulatory_framework = %(regulatory_framework)s")
	
	if filters.get("compliance_owner"):
		conditions.append("AND compliance_owner = %(compliance_owner)s")
	
	if filters.get("compliance_status"):
		conditions.append("AND compliance_status = %(compliance_status)s")
	
	if filters.get("priority"):
		conditions.append("AND priority = %(priority)s")
	
	if filters.get("show_overdue_only"):
		conditions.append("AND next_review_date < CURDATE()")
	
	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for compliance status visualization"""
	# Count by status
	status_counts = {}
	for row in data:
		status = row.get("compliance_status")
		status_counts[status] = status_counts.get(status, 0) + 1
	
	chart = {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [
				{
					"name": "Compliance Requirements",
					"values": list(status_counts.values())
				}
			]
		},
		"type": "pie"
	}
	
	return chart

