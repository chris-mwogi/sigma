# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_hours


def execute(filters=None):
	"""
	Live Visitors Onsite Report
	Shows all visitors currently checked in (not checked out)
	ISO 27001 A.11.1.2 - Physical access control
	"""
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "visitor",
			"label": _("Visitor ID"),
			"fieldtype": "Link",
			"options": "Visitor",
			"width": 120
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
			"fieldname": "location",
			"label": _("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"width": 120
		},
		{
			"fieldname": "check_in_time",
			"label": _("Check-In Time"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "duration_hours",
			"label": _("Duration (Hours)"),
			"fieldtype": "Float",
			"width": 120
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
			"fieldname": "badge_number",
			"label": _("Badge #"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "host_employee",
			"label": _("Host"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "purpose",
			"label": _("Purpose"),
			"fieldtype": "Data",
			"width": 200
		}
	]


def get_data(filters):
	"""Get live visitors data"""
	
	# Get all checked-in visitors (no check-out time)
	checkins = frappe.db.sql("""
		SELECT 
			vcc.visitor,
			vcc.location,
			vcc.check_in_time,
			vcc.badge_number,
			v.first_name,
			v.last_name,
			v.company_name,
			vr.visitor_type,
			vr.purpose_of_visit,
			vr.host_employee,
			vr.risk_score,
			vr.risk_band
		FROM `tabVisitor Checkin Checkout` vcc
		LEFT JOIN `tabVisitor` v ON vcc.visitor = v.name
		LEFT JOIN `tabVisitor Registration` vr ON vr.visitor = vcc.visitor
		WHERE vcc.check_out_time IS NULL
		AND vcc.docstatus < 2
		ORDER BY vcc.check_in_time DESC
	""", as_dict=1)
	
	data = []
	current_time = now_datetime()
	
	for checkin in checkins:
		# Calculate duration
		duration = time_diff_in_hours(current_time, checkin.check_in_time)
		
		data.append({
			"visitor": checkin.visitor,
			"visitor_name": f"{checkin.first_name or ''} {checkin.last_name or ''}".strip(),
			"company_name": checkin.company_name,
			"visitor_type": checkin.visitor_type,
			"location": checkin.location,
			"check_in_time": checkin.check_in_time,
			"duration_hours": round(duration, 2),
			"risk_score": checkin.risk_score or 0,
			"risk_band": checkin.risk_band or "Low",
			"badge_number": checkin.badge_number,
			"host_employee": checkin.host_employee,
			"purpose": checkin.purpose_of_visit
		})
	
	return data

