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
			"fieldname": "case_category",
			"label": _("Case Category"),
			"fieldtype": "Link",
			"options": "Case Category",
			"width": 150
		},
		{
			"fieldname": "total_cases",
			"label": _("Total Cases"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "investigations_completed",
			"label": _("Investigations Completed"),
			"fieldtype": "Int",
			"width": 150
		},
		{
			"fieldname": "common_findings",
			"label": _("Common Findings"),
			"fieldtype": "Long Text",
			"width": 300
		},
		{
			"fieldname": "recommendations",
			"label": _("Key Recommendations"),
			"fieldtype": "Long Text",
			"width": 300
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	# Get case counts by category
	case_data = frappe.db.sql(f"""
		SELECT
			c.case_category,
			COUNT(c.name) as total_cases
		FROM
			`tabCase` c
		WHERE
			c.docstatus < 2
			{conditions}
		GROUP BY
			c.case_category
		ORDER BY
			total_cases DESC
	""", filters, as_dict=1)
	
	# For each category, get investigation findings
	for row in case_data:
		category = row.get("case_category")
		
		# Count completed investigations
		inv_count = frappe.db.count("Case Investigation", {
			"linked_case": ["in", frappe.get_all("Case", 
				filters={"case_category": category, "docstatus": ["<", 2]}, 
				pluck="name")],
			"status": "Completed",
			"docstatus": ["<", 2]
		})
		row["investigations_completed"] = inv_count
		
		# Get common findings (sample from recent investigations)
		findings = frappe.db.sql("""
			SELECT ci.findings
			FROM `tabCase Investigation` ci
			INNER JOIN `tabCase` c ON ci.linked_case = c.name
			WHERE c.case_category = %s
				AND ci.status = 'Completed'
				AND ci.docstatus < 2
				AND ci.findings IS NOT NULL
				AND ci.findings != ''
			ORDER BY ci.actual_completion_date DESC
			LIMIT 3
		""", (category,), as_dict=1)
		
		if findings:
			row["common_findings"] = "\n\n".join([f"• {f.get('findings', '')[:200]}..." 
				for f in findings if f.get('findings')])
		else:
			row["common_findings"] = "No findings recorded"
		
		# Get recommendations
		recommendations = frappe.db.sql("""
			SELECT ci.recommendations
			FROM `tabCase Investigation` ci
			INNER JOIN `tabCase` c ON ci.linked_case = c.name
			WHERE c.case_category = %s
				AND ci.status = 'Completed'
				AND ci.docstatus < 2
				AND ci.recommendations IS NOT NULL
				AND ci.recommendations != ''
			ORDER BY ci.actual_completion_date DESC
			LIMIT 3
		""", (category,), as_dict=1)
		
		if recommendations:
			row["recommendations"] = "\n\n".join([f"• {r.get('recommendations', '')[:200]}..." 
				for r in recommendations if r.get('recommendations')])
		else:
			row["recommendations"] = "No recommendations recorded"
	
	return case_data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("c.reported_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("c.reported_date <= %(to_date)s")
	
	if filters.get("case_category"):
		conditions.append("c.case_category = %(case_category)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# Cases by category
	labels = [row.get("case_category", "Unknown") for row in data]
	values = [row.get("total_cases", 0) for row in data]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Cases by Category",
					"values": values
				}
			]
		},
		"type": "bar",
		"colors": ["#2196F3"]
	}

