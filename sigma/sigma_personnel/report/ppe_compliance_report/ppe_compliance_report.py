# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, date_diff, now_datetime


def execute(filters=None):
	"""
	PPE Compliance Report
	Shows PPE certification status and compliance rates (ISO 45001 compliance)
	"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "name",
			"label": _("Personnel ID"),
			"fieldtype": "Link",
			"options": "Human Profile",
			"width": 150
		},
		{
			"fieldname": "full_name",
			"label": _("Full Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "person_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 150
		},
		{
			"fieldname": "clearance_level",
			"label": _("Clearance"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "ppe_required",
			"label": _("PPE Required"),
			"fieldtype": "Check",
			"width": 100
		},
		{
			"fieldname": "ppe_certified_date",
			"label": _("Certified Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "days_since_certification",
			"label": _("Days Since Cert"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "compliance_status",
			"label": _("Compliance Status"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Float",
			"width": 100
		}
	]


def get_data(filters):
	"""Get report data based on filters"""
	conditions = get_conditions(filters)
	
	query = """
		SELECT
			hp.name,
			hp.full_name,
			hp.person_type,
			hp.department,
			hp.clearance_level,
			hp.ppe_required,
			hp.ppe_certified_date,
			hp.risk_score,
			hp.status
		FROM
			`tabHuman Profile` hp
		WHERE
			hp.docstatus = 1
			{conditions}
		ORDER BY
			hp.full_name
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, filters, as_dict=1)
	
	# Calculate compliance status
	today = getdate()
	for row in data:
		if not row.ppe_required:
			row["compliance_status"] = "Not Required"
			row["days_since_certification"] = None
		elif not row.ppe_certified_date:
			row["compliance_status"] = "Not Certified"
			row["days_since_certification"] = None
		else:
			days_since = date_diff(today, row.ppe_certified_date)
			row["days_since_certification"] = days_since
			
			if days_since > 365:
				row["compliance_status"] = "Expired"
			elif days_since > 335:  # 30 days before expiry
				row["compliance_status"] = "Expiring Soon"
			else:
				row["compliance_status"] = "Compliant"
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions based on filters"""
	conditions = []
	
	if filters.get("person_type"):
		conditions.append("AND hp.person_type = %(person_type)s")
	
	if filters.get("department"):
		conditions.append("AND hp.department = %(department)s")
	
	if filters.get("clearance_level"):
		conditions.append("AND hp.clearance_level = %(clearance_level)s")
	
	if filters.get("compliance_status"):
		# This will be filtered in post-processing
		pass
	
	if filters.get("status"):
		conditions.append("AND hp.status = %(status)s")
	
	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for compliance status distribution"""
	status_counts = {}
	for row in data:
		status = row.get("compliance_status", "Unknown")
		status_counts[status] = status_counts.get(status, 0) + 1
	
	return {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [{"name": "Personnel", "values": list(status_counts.values())}]
		},
		"type": "pie",
		"colors": ["#4CAF50", "#FFC107", "#F44336", "#9E9E9E"]
	}


def get_summary(data):
	"""Generate summary statistics"""
	total_personnel = len(data)
	ppe_required = len([d for d in data if d["ppe_required"]])
	compliant = len([d for d in data if d["compliance_status"] == "Compliant"])
	expired = len([d for d in data if d["compliance_status"] == "Expired"])
	expiring_soon = len([d for d in data if d["compliance_status"] == "Expiring Soon"])
	not_certified = len([d for d in data if d["compliance_status"] == "Not Certified"])
	
	compliance_rate = 0
	if ppe_required > 0:
		compliance_rate = round((compliant / ppe_required) * 100, 2)
	
	return [
		{"label": _("Total Personnel"), "value": total_personnel, "indicator": "Blue"},
		{"label": _("PPE Required"), "value": ppe_required, "indicator": "Orange"},
		{"label": _("Compliant"), "value": compliant, "indicator": "Green"},
		{"label": _("Expired"), "value": expired, "indicator": "Red"},
		{"label": _("Expiring Soon"), "value": expiring_soon, "indicator": "Orange"},
		{"label": _("Not Certified"), "value": not_certified, "indicator": "Red"},
		{"label": _("Compliance Rate %"), "value": compliance_rate, "indicator": "Green"}
	]

