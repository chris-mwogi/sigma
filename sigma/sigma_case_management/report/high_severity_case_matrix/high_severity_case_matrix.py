# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _


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
			"fieldname": "severity",
			"label": _("Severity"),
			"fieldtype": "Link",
			"options": "Case Severity Matrix",
			"width": 100
		},
		{
			"fieldname": "severity_score",
			"label": _("Severity Score"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "case_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Case Category",
			"width": 150
		},
		{
			"fieldname": "risk_weight",
			"label": _("Risk Weight"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "date_reported",
			"label": _("Reported Date"),
			"fieldtype": "Date",
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
			c.severity,
			sm.severity_score,
			c.case_category,
			cc.risk_weight,
			c.risk_score,
			c.status,
			c.date_reported,
			c.assigned_case_manager
		FROM
			`tabCase` c
		LEFT JOIN
			`tabCase Severity Matrix` sm ON c.severity = sm.name
		LEFT JOIN
			`tabCase Category` cc ON c.case_category = cc.name
		WHERE
			c.docstatus < 2
			AND c.severity IN ('Critical', 'High')
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

	if filters.get("case_category"):
		conditions.append("c.case_category = %(case_category)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# Risk score distribution
	category_risk = {}
	
	for row in data:
		category = row.get("case_category") or "Unknown"
		risk_score = row.get("risk_score", 0)
		
		if category not in category_risk:
			category_risk[category] = []
		category_risk[category].append(risk_score)
	
	# Calculate average risk per category
	avg_risk = {cat: sum(scores)/len(scores) for cat, scores in category_risk.items()}
	
	return {
		"data": {
			"labels": list(avg_risk.keys()),
			"datasets": [
				{
					"name": "Average Risk Score by Category",
					"values": list(avg_risk.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#F44336"]
	}

