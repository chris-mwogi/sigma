# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, now_datetime


def execute(filters=None):
	"""
	Personnel Movement History Report
	Shows all personnel movements with filters for date range, personnel, and zone
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "timestamp",
			"label": _("Timestamp"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "human",
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
			"fieldname": "zone",
			"label": _("Zone"),
			"fieldtype": "Link",
			"options": "Zone Configuration",
			"width": 150
		},
		{
			"fieldname": "zone_name",
			"label": _("Zone Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "hazard_level",
			"label": _("Hazard Level"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "source_type",
			"label": _("Source"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "confidence",
			"label": _("Confidence %"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "clearance_level",
			"label": _("Clearance"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "location_event",
			"label": _("Event ID"),
			"fieldtype": "Link",
			"options": "Human Location Event",
			"width": 150
		}
	]


def get_data(filters):
	"""Get report data based on filters"""
	conditions = get_conditions(filters)
	
	query = """
		SELECT
			hle.timestamp,
			hle.human,
			hp.full_name,
			hp.person_type,
			hle.zone,
			zc.zone_name,
			zc.hazard_level,
			hle.source_type,
			hle.confidence,
			hp.clearance_level,
			hle.name as location_event
		FROM
			`tabHuman Location Event` hle
		LEFT JOIN
			`tabHuman Profile` hp ON hle.human = hp.name
		LEFT JOIN
			`tabZone Configuration` zc ON hle.zone = zc.name
		WHERE
			hle.docstatus < 2
			{conditions}
		ORDER BY
			hle.timestamp DESC
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, filters, as_dict=1)
	return data


def get_conditions(filters):
	"""Build WHERE conditions based on filters"""
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("AND hle.timestamp >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND hle.timestamp <= %(to_date)s")
	
	if filters.get("human"):
		conditions.append("AND hle.human = %(human)s")
	
	if filters.get("zone"):
		conditions.append("AND hle.zone = %(zone)s")
	
	if filters.get("person_type"):
		conditions.append("AND hp.person_type = %(person_type)s")
	
	if filters.get("source_type"):
		conditions.append("AND hle.source_type = %(source_type)s")
	
	return " ".join(conditions)

