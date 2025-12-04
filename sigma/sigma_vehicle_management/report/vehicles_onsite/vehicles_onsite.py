# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_hours


def execute(filters=None):
	"""
	Vehicles Onsite Report
	Shows all vehicles currently on premises (checked in, not checked out)
	ISO 27001 A.11.1.2 - Physical access control
	"""
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "license_plate",
			"label": _("License Plate"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "vehicle_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "make_model",
			"label": _("Make/Model"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "owner_type",
			"label": _("Owner Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver"),
			"fieldtype": "Data",
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
			"fieldname": "parking_space",
			"label": _("Parking Space"),
			"fieldtype": "Data",
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
			"fieldname": "dangerous_goods",
			"label": _("Dangerous Goods"),
			"fieldtype": "Check",
			"width": 120
		},
		{
			"fieldname": "cargo_type",
			"label": _("Cargo Type"),
			"fieldtype": "Data",
			"width": 150
		}
	]


def get_data(filters):
	"""Get vehicles onsite data"""
	
	# Get all checked-in vehicles (no check-out time)
	checkins = frappe.db.sql("""
		SELECT 
			vcc.license_plate,
			vcc.check_in_time,
			vcc.parking_space,
			v.vehicle_type,
			v.make,
			v.model,
			v.owner_type,
			v.driver_name,
			v.risk_score,
			v.risk_band,
			v.dangerous_goods_flag,
			v.cargo_type
		FROM `tabVehicle Checkin Checkout` vcc
		LEFT JOIN `tabVehicle` v ON vcc.license_plate = v.license_plate
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
			"license_plate": checkin.license_plate,
			"vehicle_type": checkin.vehicle_type,
			"make_model": f"{checkin.make or ''} {checkin.model or ''}".strip(),
			"owner_type": checkin.owner_type,
			"driver_name": checkin.driver_name,
			"check_in_time": checkin.check_in_time,
			"duration_hours": round(duration, 2),
			"parking_space": checkin.parking_space,
			"risk_score": checkin.risk_score or 0,
			"risk_band": checkin.risk_band or "Low",
			"dangerous_goods": checkin.dangerous_goods_flag,
			"cargo_type": checkin.cargo_type
		})
	
	return data

