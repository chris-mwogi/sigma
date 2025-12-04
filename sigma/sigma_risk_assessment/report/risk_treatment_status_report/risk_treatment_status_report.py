# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


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
			"label": _("Treatment Plan ID"),
			"fieldtype": "Link",
			"options": "Risk Treatment Plan",
			"width": 140
		},
		{
			"fieldname": "plan_title",
			"label": _("Plan Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "linked_risk",
			"label": _("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register",
			"width": 120
		},
		{
			"fieldname": "treatment_strategy",
			"label": _("Strategy"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "plan_owner",
			"label": _("Plan Owner"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "progress_percentage",
			"label": _("Progress %"),
			"fieldtype": "Percent",
			"width": 90
		},
		{
			"fieldname": "start_date",
			"label": _("Start Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "target_completion_date",
			"label": _("Target Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "actual_completion_date",
			"label": _("Actual Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "estimated_budget",
			"label": _("Budget"),
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "actual_cost",
			"label": _("Actual Cost"),
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "budget_variance",
			"label": _("Variance"),
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "action_count",
			"label": _("Actions"),
			"fieldtype": "Int",
			"width": 80
		}
	]


def get_data(filters):
	"""Get data for the report"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			rtp.name,
			rtp.plan_title,
			rtp.linked_risk,
			rtp.treatment_strategy,
			rtp.plan_owner,
			rtp.plan_status as status,
			rtp.progress_percentage,
			rtp.start_date,
			rtp.target_completion_date,
			rtp.actual_completion_date,
			rtp.estimated_budget,
			rtp.actual_cost,
			rtp.budget_variance,
			(SELECT COUNT(*) FROM `tabRisk Treatment Action` WHERE parent = rtp.name) as action_count
		FROM
			`tabRisk Treatment Plan` rtp
		WHERE
			rtp.docstatus < 2
			{conditions}
		ORDER BY
			rtp.plan_status, rtp.target_completion_date
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("linked_risk"):
		conditions.append("AND rtp.linked_risk = %(linked_risk)s")
	
	if filters.get("treatment_strategy"):
		conditions.append("AND rtp.treatment_strategy = %(treatment_strategy)s")
	
	if filters.get("plan_owner"):
		conditions.append("AND rtp.plan_owner = %(plan_owner)s")
	
	if filters.get("status"):
		conditions.append("AND rtp.plan_status = %(status)s")
	
	if filters.get("from_date"):
		conditions.append("AND rtp.start_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND rtp.target_completion_date <= %(to_date)s")
	
	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for treatment status visualization"""
	# Count by status
	status_counts = {}
	for row in data:
		status = row.get("status")
		status_counts[status] = status_counts.get(status, 0) + 1
	
	chart = {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [
				{
					"name": "Treatment Plans",
					"values": list(status_counts.values())
				}
			]
		},
		"type": "pie"
	}
	
	return chart

