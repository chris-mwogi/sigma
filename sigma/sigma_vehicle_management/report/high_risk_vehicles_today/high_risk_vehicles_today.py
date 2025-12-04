# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, getdate


def execute(filters=None):
	"""
	High-Risk Vehicles Today Report
	Shows vehicles with high risk scores that checked in today
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
			"fieldname": "license_plate",
			"label": _("License Plate"),
			"fieldtype": "Link",
			"options": "Vehicle",
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
			"fieldname": "is_blacklisted",
			"label": _("Blacklisted"),
			"fieldtype": "Check",
			"width": 100
		},
		{
			"fieldname": "dangerous_goods",
			"label": _("Dangerous Goods"),
			"fieldtype": "Check",
			"width": 120
		},
		{
			"fieldname": "dangerous_goods_class",
			"label": _("DG Class"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "cargo_type",
			"label": _("Cargo Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "check_in_time",
			"label": _("Check-In Time"),
			"fieldtype": "Datetime",
			"width": 150
		}
	]


def get_data(filters):
	"""Get high-risk vehicles data"""
	
	# Default to today if no date filter
	from_date = filters.get("from_date") or today()
	to_date = filters.get("to_date") or today()
	
	# Get vehicles with high risk that checked in today
	vehicles = frappe.db.sql("""
		SELECT DISTINCT
			v.license_plate,
			v.vehicle_type,
			v.make,
			v.model,
			v.owner_type,
			v.driver_name,
			v.risk_score,
			v.risk_band,
			v.is_blacklisted,
			v.dangerous_goods_flag,
			v.dangerous_goods_class,
			v.cargo_type,
			vcc.check_in_time
		FROM `tabVehicle` v
		LEFT JOIN `tabVehicle Checkin Checkout` vcc ON v.license_plate = vcc.license_plate
		WHERE (v.risk_band = 'High' OR v.risk_score >= 60 OR v.is_blacklisted = 1 OR v.dangerous_goods_flag = 1)
		AND DATE(vcc.check_in_time) BETWEEN %s AND %s
		AND vcc.docstatus < 2
		ORDER BY v.risk_score DESC, vcc.check_in_time DESC
	""", (from_date, to_date), as_dict=1)
	
	data = []
	for vehicle in vehicles:
		data.append({
			"license_plate": vehicle.license_plate,
			"vehicle_type": vehicle.vehicle_type,
			"make_model": f"{vehicle.make or ''} {vehicle.model or ''}".strip(),
			"owner_type": vehicle.owner_type,
			"driver_name": vehicle.driver_name,
			"risk_score": vehicle.risk_score or 0,
			"risk_band": vehicle.risk_band or "Low",
			"is_blacklisted": vehicle.is_blacklisted,
			"dangerous_goods": vehicle.dangerous_goods_flag,
			"dangerous_goods_class": vehicle.dangerous_goods_class,
			"cargo_type": vehicle.cargo_type,
			"check_in_time": vehicle.check_in_time
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
					"name": "Vehicles",
					"values": list(risk_counts.values())
				}
			]
		},
		"type": "bar",
		"colors": ["#ff5858", "#ffa00a", "#98d85b"]
	}

