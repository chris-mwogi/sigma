# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Return columns for the report"""
	return [
		{
			"fieldname": "name",
			"label": _("Risk ID"),
			"fieldtype": "Link",
			"options": "Risk Register",
			"width": 120
		},
		{
			"fieldname": "risk_title",
			"label": _("Risk Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "risk_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Risk Category",
			"width": 120
		},
		{
			"fieldname": "risk_owner",
			"label": _("Risk Owner"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "current_risk_rating",
			"label": _("Current Risk Rating"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "date_identified",
			"label": _("Date Identified"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "last_assessment_date",
			"label": _("Last Assessment"),
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
			"fieldname": "assessment_count",
			"label": _("Assessments"),
			"fieldtype": "Int",
			"width": 90
		},
		{
			"fieldname": "treatment_count",
			"label": _("Treatments"),
			"fieldtype": "Int",
			"width": 90
		},
		{
			"fieldname": "incident_count",
			"label": _("Incidents"),
			"fieldtype": "Int",
			"width": 90
		}
	]


def get_data(filters):
	"""Get data for the report"""
	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			rr.name,
			rr.risk_title,
			rr.risk_category,
			rr.risk_owner,
			rr.department,
			rr.status,
			(SELECT residual_risk_rating
			 FROM `tabRisk Assessment`
			 WHERE linked_risk = rr.name AND docstatus = 1
			 ORDER BY assessment_date DESC
			 LIMIT 1) as current_risk_rating,
			rr.date_identified,
			(SELECT assessment_date
			 FROM `tabRisk Assessment`
			 WHERE linked_risk = rr.name AND docstatus = 1
			 ORDER BY assessment_date DESC
			 LIMIT 1) as last_assessment_date,
			rr.next_review_date,
			(SELECT COUNT(*) FROM `tabRisk Assessment` WHERE linked_risk = rr.name AND docstatus < 2) as assessment_count,
			(SELECT COUNT(*) FROM `tabRisk Treatment Plan` WHERE linked_risk = rr.name AND docstatus < 2) as treatment_count,
			(SELECT COUNT(*) FROM `tabRisk Incident` WHERE linked_risk = rr.name AND docstatus < 2) as incident_count
		FROM
			`tabRisk Register` rr
		WHERE
			rr.docstatus < 2
			{conditions}
		ORDER BY
			rr.date_identified DESC
	""", filters, as_dict=1)

	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("risk_category"):
		conditions.append("AND rr.risk_category = %(risk_category)s")
	
	if filters.get("risk_owner"):
		conditions.append("AND rr.risk_owner = %(risk_owner)s")
	
	if filters.get("department"):
		conditions.append("AND rr.department = %(department)s")
	
	if filters.get("status"):
		conditions.append("AND rr.status = %(status)s")
	
	if filters.get("current_risk_rating"):
		conditions.append("AND rr.current_risk_rating = %(current_risk_rating)s")
	
	if filters.get("from_date"):
		conditions.append("AND rr.date_identified >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND rr.date_identified <= %(to_date)s")
	
	return " ".join(conditions)

