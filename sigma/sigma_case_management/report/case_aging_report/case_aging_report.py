# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate, now_datetime, get_datetime


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
			"fieldname": "date_reported",
			"label": _("Reported Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "days_open",
			"label": _("Days Open"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "sla_due_date",
			"label": _("SLA Due Date"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "sla_breach",
			"label": _("SLA Breach"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "days_overdue",
			"label": _("Days Overdue"),
			"fieldtype": "Int",
			"width": 100
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
			c.status,
			c.severity,
			c.date_reported,
			c.sla_due_date,
			c.assigned_case_manager
		FROM
			`tabCase` c
		WHERE
			c.docstatus < 2
			AND c.status NOT IN ('Closed', 'Rejected')
			{conditions}
		ORDER BY
			c.date_reported ASC
	""", filters, as_dict=1)
	
	# Calculate aging metrics
	today = getdate()
	now = now_datetime()
	
	for row in data:
		reported_date = getdate(row.get("date_reported"))
		row["days_open"] = date_diff(today, reported_date)
		
		# Check SLA breach
		sla_due = row.get("sla_due_date")
		if sla_due:
			sla_due_dt = get_datetime(sla_due)
			if now > sla_due_dt:
				row["sla_breach"] = "Yes"
				row["days_overdue"] = date_diff(now.date(), sla_due_dt.date())
			else:
				row["sla_breach"] = "No"
				row["days_overdue"] = 0
		else:
			row["sla_breach"] = "N/A"
			row["days_overdue"] = 0
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("c.date_reported >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("c.date_reported <= %(to_date)s")

	if filters.get("severity"):
		conditions.append("c.severity = %(severity)s")

	if filters.get("assigned_to"):
		conditions.append("c.assigned_case_manager = %(assigned_to)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# Aging buckets
	buckets = {
		"0-7 days": 0,
		"8-14 days": 0,
		"15-30 days": 0,
		"31-60 days": 0,
		"60+ days": 0
	}
	
	for row in data:
		days = row.get("days_open", 0)
		if days <= 7:
			buckets["0-7 days"] += 1
		elif days <= 14:
			buckets["8-14 days"] += 1
		elif days <= 30:
			buckets["15-30 days"] += 1
		elif days <= 60:
			buckets["31-60 days"] += 1
		else:
			buckets["60+ days"] += 1
	
	return {
		"data": {
			"labels": list(buckets.keys()),
			"datasets": [
				{
					"name": "Cases by Age",
					"values": list(buckets.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#4CAF50", "#8BC34A", "#FFC107", "#FF9800", "#F44336"]
	}

