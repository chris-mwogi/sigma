# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days


def execute(filters=None):
	"""
	Dangerous Goods Tracking Report
	Tracks all vehicles carrying dangerous goods for OSHA compliance
	OSHA 29 CFR 1910.1200 - Hazard Communication
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
			"fieldname": "dangerous_goods_class",
			"label": _("DG Class"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "cargo_type",
			"label": _("Cargo Type"),
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
			"fieldname": "owner_name",
			"label": _("Owner Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "driver_license_number",
			"label": _("Driver License"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "driver_license_expiry",
			"label": _("License Expiry"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "last_check_in",
			"label": _("Last Check-In"),
			"fieldtype": "Datetime",
			"width": 150
		}
	]


def get_data(filters):
	"""Get dangerous goods tracking data"""
	
	# Get all vehicles carrying dangerous goods
	vehicles = frappe.db.sql("""
		SELECT 
			v.license_plate,
			v.vehicle_type,
			v.dangerous_goods_class,
			v.cargo_type,
			v.owner_type,
			v.owner_name,
			v.driver_name,
			v.driver_license_number,
			v.driver_license_expiry,
			v.risk_score,
			v.status,
			(SELECT MAX(check_in_time) 
			 FROM `tabVehicle Checkin Checkout` 
			 WHERE license_plate = v.license_plate) as last_check_in
		FROM `tabVehicle` v
		WHERE v.dangerous_goods_flag = 1
		AND v.status != 'Inactive'
		ORDER BY v.risk_score DESC, v.license_plate
	""", as_dict=1)
	
	data = []
	for vehicle in vehicles:
		data.append({
			"license_plate": vehicle.license_plate,
			"vehicle_type": vehicle.vehicle_type,
			"dangerous_goods_class": vehicle.dangerous_goods_class,
			"cargo_type": vehicle.cargo_type,
			"owner_type": vehicle.owner_type,
			"owner_name": vehicle.owner_name,
			"driver_name": vehicle.driver_name,
			"driver_license_number": vehicle.driver_license_number,
			"driver_license_expiry": vehicle.driver_license_expiry,
			"risk_score": vehicle.risk_score or 0,
			"status": vehicle.status,
			"last_check_in": vehicle.last_check_in
		})
	
	return data


def get_chart_data(data):
	"""Generate chart for dangerous goods class distribution"""
	if not data:
		return None
	
	# Count by DG class
	dg_counts = {}
	for row in data:
		dg_class = row.get("dangerous_goods_class", "Unknown")
		# Simplify class name for chart
		if dg_class:
			class_num = dg_class.split(" - ")[0] if " - " in dg_class else dg_class
			dg_counts[class_num] = dg_counts.get(class_num, 0) + 1
	
	return {
		"data": {
			"labels": list(dg_counts.keys()),
			"datasets": [
				{
					"name": "Vehicles",
					"values": list(dg_counts.values())
				}
			]
		},
		"type": "pie",
		"colors": ["#ff5858", "#ffa00a", "#ffdd57", "#98d85b", "#5e64ff", "#743ee2", "#ff66c4", "#00d4ff", "#7575ff"]
	}

