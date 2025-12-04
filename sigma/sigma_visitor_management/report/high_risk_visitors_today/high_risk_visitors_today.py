# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, getdate


def execute(filters=None):
	"""
	High-Risk Visitors Today Report
	Shows visitors with high risk scores expected or checked in today
	ISO 31000 - Risk Management
	"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	
	return columns, data, None, chart


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "name",
			"label": _("Registration ID"),
			"fieldtype": "Link",
			"options": "Visitor Registration",
			"width": 150
		},
		{
			"fieldname": "visitor_name",
			"label": _("Visitor Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "company_name",
			"label": _("Company"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "visitor_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "risk_band",
			"label": _("Risk Band"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "on_watchlist",
			"label": _("Watchlist"),
			"fieldtype": "Check",
			"width": 80
		},
		{
			"fieldname": "access_level",
			"label": _("Access Level"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "nda_required",
			"label": _("NDA Required"),
			"fieldtype": "Check",
			"width": 100
		},
		{
			"fieldname": "safety_induction_required",
			"label": _("Safety Induction"),
			"fieldtype": "Check",
			"width": 120
		},
		{
			"fieldname": "expected_arrival_date",
			"label": _("Expected Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "purpose_of_visit",
			"label": _("Purpose"),
			"fieldtype": "Data",
			"width": 200
		}
	]


def get_data(filters):
	"""Get high-risk visitors data"""
	
	# Default to today if no date filter
	from_date = filters.get("from_date") or today()
	to_date = filters.get("to_date") or today()
	
	# Get visitor registrations with high risk
	registrations = frappe.db.sql("""
		SELECT 
			vr.name,
			vr.visitor,
			vr.visitor_type,
			vr.expected_arrival_date,
			vr.purpose_of_visit,
			vr.risk_score,
			vr.risk_band,
			vr.on_watchlist,
			vr.access_level,
			vr.nda_required,
			vr.safety_induction_required,
			v.first_name,
			v.last_name,
			v.company_name
		FROM `tabVisitor Registration` vr
		LEFT JOIN `tabVisitor` v ON vr.visitor = v.name
		WHERE vr.expected_arrival_date BETWEEN %s AND %s
		AND (vr.risk_band = 'High' OR vr.risk_score >= 60 OR vr.on_watchlist = 1)
		AND vr.docstatus < 2
		ORDER BY vr.risk_score DESC, vr.expected_arrival_date
	""", (from_date, to_date), as_dict=1)
	
	data = []
	for reg in registrations:
		data.append({
			"name": reg.name,
			"visitor_name": f"{reg.first_name or ''} {reg.last_name or ''}".strip(),
			"company_name": reg.company_name,
			"visitor_type": reg.visitor_type,
			"risk_score": reg.risk_score or 0,
			"risk_band": reg.risk_band or "Low",
			"on_watchlist": reg.on_watchlist,
			"access_level": reg.access_level,
			"nda_required": reg.nda_required,
			"safety_induction_required": reg.safety_induction_required,
			"expected_arrival_date": reg.expected_arrival_date,
			"purpose_of_visit": reg.purpose_of_visit
		})
	
	return data


def get_chart_data(data):
	"""Generate chart for risk distribution"""
	if not data:
		return None
	
	# Count by risk band
	risk_counts = {"High": 0, "Medium": 0, "Low": 0}
	for row in data:
		risk_band = row.get("risk_band", "Low")
		risk_counts[risk_band] = risk_counts.get(risk_band, 0) + 1
	
	return {
		"data": {
			"labels": list(risk_counts.keys()),
			"datasets": [
				{
					"name": "Visitors",
					"values": list(risk_counts.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#ff5858", "#ffa00a", "#98d85b"]
	}

