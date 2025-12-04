# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Zone Occupancy Report
	Shows current and historical zone occupancy with capacity analysis
	"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "zone",
			"label": _("Zone ID"),
			"fieldtype": "Link",
			"options": "Zone Configuration",
			"width": 150
		},
		{
			"fieldname": "zone_name",
			"label": _("Zone Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "zone_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "hazard_level",
			"label": _("Hazard Level"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "current_occupancy",
			"label": _("Current Occupancy"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "max_occupancy",
			"label": _("Max Capacity"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "occupancy_percentage",
			"label": _("Occupancy %"),
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "clearance_required",
			"label": _("Clearance Required"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "lone_worker_alert_minutes",
			"label": _("Lone Worker Alert (min)"),
			"fieldtype": "Int",
			"width": 150
		}
	]


def get_data(filters):
	"""Get report data based on filters"""
	# Get all active zones
	zones = frappe.get_all("Zone Configuration",
		filters={"is_active": 1},
		fields=["name", "zone_name", "zone_type", "hazard_level", "max_occupancy", 
		        "clearance_level_required", "lone_worker_alert_minutes"]
	)
	
	data = []
	for zone in zones:
		# Count current occupancy
		current_occupancy = frappe.db.count("Zone Presence", {
			"zone": zone.name,
			"status": "Active"
		})
		
		# Calculate occupancy percentage
		occupancy_percentage = 0
		if zone.max_occupancy and zone.max_occupancy > 0:
			occupancy_percentage = (current_occupancy / zone.max_occupancy) * 100
		
		# Determine status
		status = "Normal"
		if occupancy_percentage >= 100:
			status = "At Capacity"
		elif occupancy_percentage >= 80:
			status = "Near Capacity"
		elif current_occupancy == 1 and zone.lone_worker_alert_minutes:
			status = "Lone Worker"
		elif current_occupancy == 0:
			status = "Empty"
		
		data.append({
			"zone": zone.name,
			"zone_name": zone.zone_name,
			"zone_type": zone.zone_type,
			"hazard_level": zone.hazard_level,
			"current_occupancy": current_occupancy,
			"max_occupancy": zone.max_occupancy or 0,
			"occupancy_percentage": occupancy_percentage,
			"status": status,
			"clearance_required": zone.clearance_level_required,
			"lone_worker_alert_minutes": zone.lone_worker_alert_minutes or 0
		})
	
	return data


def get_chart_data(data):
	"""Generate chart data for zone occupancy visualization"""
	labels = [d["zone_name"] for d in data]
	current = [d["current_occupancy"] for d in data]
	max_capacity = [d["max_occupancy"] for d in data]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Current Occupancy",
					"values": current
				},
				{
					"name": "Max Capacity",
					"values": max_capacity
				}
			]
		},
		"type": "bar",
		"colors": ["#4CAF50", "#FF9800"]
	}

