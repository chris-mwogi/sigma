# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate


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
			"fieldname": "case_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Case Category",
			"width": 150
		},
		{
			"fieldname": "severity",
			"label": _("Severity"),
			"fieldtype": "Link",
			"options": "Case Severity Matrix",
			"width": 100
		},
		{
			"fieldname": "date_reported",
			"label": _("Reported Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "actual_closure_date",
			"label": _("Closure Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "resolution_days",
			"label": _("Resolution Days"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "assigned_case_manager",
			"label": _("Assigned To"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			c.name as case_id,
			c.case_title,
			c.case_category,
			c.severity,
			c.date_reported,
			c.actual_closure_date,
			c.status,
			c.assigned_case_manager
		FROM
			`tabCase` c
		WHERE
			c.docstatus < 2
			AND c.status = 'Closed'
			{conditions}
		ORDER BY
			c.actual_closure_date DESC
	""", filters, as_dict=1)
	
	# Calculate resolution days
	for row in data:
		if row.get("date_reported") and row.get("actual_closure_date"):
			reported = getdate(row.get("date_reported"))
			closed = getdate(row.get("actual_closure_date"))
			row["resolution_days"] = date_diff(closed, reported)
		else:
			row["resolution_days"] = 0
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("c.actual_closure_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("c.actual_closure_date <= %(to_date)s")
	
	if filters.get("severity"):
		conditions.append("c.severity = %(severity)s")
	
	if filters.get("case_category"):
		conditions.append("c.case_category = %(case_category)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# Average resolution time by category
	category_days = {}
	
	for row in data:
		category = row.get("case_category") or "Unknown"
		days = row.get("resolution_days", 0)
		
		if category not in category_days:
			category_days[category] = []
		category_days[category].append(days)
	
	# Calculate averages
	avg_days = {cat: sum(days)/len(days) for cat, days in category_days.items()}
	
	return {
		"data": {
			"labels": list(avg_days.keys()),
			"datasets": [
				{
					"name": "Average Resolution Days",
					"values": list(avg_days.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#4CAF50"]
	}

