# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Parking Utilization Report
	Shows parking space occupancy and utilization rates
	"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	
	return columns, data, None, chart


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "parking_space",
			"label": _("Parking Space"),
			"fieldtype": "Link",
			"options": "Parking Space",
			"width": 150
		},
		{
			"fieldname": "location",
			"label": _("Location"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "space_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "current_vehicle",
			"label": _("Current Vehicle"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "vehicle_type",
			"label": _("Vehicle Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "check_in_time",
			"label": _("Occupied Since"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "utilization_today",
			"label": _("Utilization Today (%)"),
			"fieldtype": "Percent",
			"width": 150
		}
	]


def get_data(filters):
	"""Get parking utilization data"""
	
	# Get all parking spaces with current occupancy
	spaces = frappe.db.sql("""
		SELECT 
			ps.name as parking_space,
			ps.location,
			ps.space_type,
			ps.status,
			vcc.license_plate as current_vehicle,
			v.vehicle_type,
			vcc.check_in_time
		FROM `tabParking Space` ps
		LEFT JOIN `tabVehicle Checkin Checkout` vcc 
			ON ps.name = vcc.parking_space 
			AND vcc.check_out_time IS NULL
			AND vcc.docstatus < 2
		LEFT JOIN `tabVehicle` v ON vcc.license_plate = v.license_plate
		WHERE ps.status != 'Inactive'
		ORDER BY ps.location, ps.name
	""", as_dict=1)
	
	data = []
	for space in spaces:
		# Calculate utilization (simplified - would need historical data for accurate calculation)
		# For now, occupied = 100%, vacant = 0%
		utilization = 100 if space.current_vehicle else 0
		
		data.append({
			"parking_space": space.parking_space,
			"location": space.location,
			"space_type": space.space_type,
			"status": space.status,
			"current_vehicle": space.current_vehicle,
			"vehicle_type": space.vehicle_type,
			"check_in_time": space.check_in_time,
			"utilization_today": utilization
		})
	
	return data


def get_chart_data(data):
	"""Generate chart for parking occupancy"""
	if not data:
		return None
	
	# Count occupied vs vacant
	occupied = sum(1 for row in data if row.get("current_vehicle"))
	vacant = len(data) - occupied
	
	return {
		"data": {
			"labels": ["Occupied", "Vacant"],
			"datasets": [
				{
					"name": "Parking Spaces",
					"values": [occupied, vacant]
				}
			]
		},
		"type": "pie",
		"colors": ["#ff5858", "#98d85b"]
	}

