# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	"""Return columns for the report"""
	return [
		{
			"fieldname": "name",
			"label": _("Incident ID"),
			"fieldtype": "Link",
			"options": "Risk Incident",
			"width": 120
		},
		{
			"fieldname": "incident_title",
			"label": _("Incident Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "incident_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "incident_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Risk Category",
			"width": 120
		},
		{
			"fieldname": "incident_date",
			"label": _("Incident Date"),
			"fieldtype": "Datetime",
			"width": 140
		},
		{
			"fieldname": "reported_by",
			"label": _("Reported By"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "incident_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "impact_level",
			"label": _("Impact Level"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "financial_impact",
			"label": _("Financial Impact"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "linked_risk",
			"label": _("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register",
			"width": 120
		},
		{
			"fieldname": "linked_control",
			"label": _("Linked Control"),
			"fieldtype": "Link",
			"options": "Risk Control",
			"width": 120
		},
		{
			"fieldname": "investigation_status",
			"label": _("Investigation"),
			"fieldtype": "Data",
			"width": 110
		},
		{
			"fieldname": "investigation_owner",
			"label": _("Investigator"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "closure_date",
			"label": _("Closure Date"),
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
			incident_title,
			incident_type,
			incident_category,
			incident_date,
			reported_by,
			incident_status,
			impact_level,
			financial_impact,
			linked_risk,
			linked_control,
			investigation_status,
			investigation_owner,
			closure_date
		FROM
			`tabRisk Incident`
		WHERE
			docstatus < 2
			{conditions}
		ORDER BY
			incident_date DESC
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("incident_type"):
		conditions.append("AND incident_type = %(incident_type)s")
	
	if filters.get("incident_category"):
		conditions.append("AND incident_category = %(incident_category)s")
	
	if filters.get("incident_status"):
		conditions.append("AND incident_status = %(incident_status)s")
	
	if filters.get("impact_level"):
		conditions.append("AND impact_level = %(impact_level)s")
	
	if filters.get("linked_risk"):
		conditions.append("AND linked_risk = %(linked_risk)s")
	
	if filters.get("from_date"):
		conditions.append("AND DATE(incident_date) >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND DATE(incident_date) <= %(to_date)s")
	
	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for incident analysis"""
	# Count by type
	type_counts = {}
	for row in data:
		incident_type = row.get("incident_type")
		type_counts[incident_type] = type_counts.get(incident_type, 0) + 1
	
	chart = {
		"data": {
			"labels": list(type_counts.keys()),
			"datasets": [
				{
					"name": "Incidents by Type",
					"values": list(type_counts.values())
				}
			]
		},
		"type": "bar"
	}
	
	return chart


def get_summary(data):
	"""Generate summary statistics"""
	total_incidents = len(data)
	total_financial_impact = sum(flt(row.get("financial_impact", 0)) for row in data)
	
	# Count by status
	status_counts = {}
	for row in data:
		status = row.get("incident_status")
		status_counts[status] = status_counts.get(status, 0) + 1
	
	# Count by impact level
	impact_counts = {}
	for row in data:
		impact = row.get("impact_level")
		impact_counts[impact] = impact_counts.get(impact, 0) + 1
	
	summary = [
		{
			"label": _("Total Incidents"),
			"value": total_incidents,
			"indicator": "blue"
		},
		{
			"label": _("Total Financial Impact"),
			"value": frappe.format_value(total_financial_impact, {"fieldtype": "Currency"}),
			"indicator": "red"
		},
		{
			"label": _("Critical Impact"),
			"value": impact_counts.get("Critical", 0),
			"indicator": "red"
		},
		{
			"label": _("High Impact"),
			"value": impact_counts.get("High", 0),
			"indicator": "orange"
		},
		{
			"label": _("Closed"),
			"value": status_counts.get("Closed", 0),
			"indicator": "green"
		}
	]
	
	return summary

