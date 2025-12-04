# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import time_diff_in_seconds, now_datetime


def execute(filters=None):
	"""
	Lone Worker Incidents Report
	Shows all lone worker alerts with resolution tracking (ISO 45001 compliance)
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
			"label": _("Alert ID"),
			"fieldtype": "Link",
			"options": "Lone Worker Alert",
			"width": 150
		},
		{
			"fieldname": "alert_timestamp",
			"label": _("Alert Time"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "human",
			"label": _("Personnel"),
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
			"fieldname": "alert_type",
			"label": _("Alert Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "zone",
			"label": _("Zone"),
			"fieldtype": "Link",
			"options": "Zone Configuration",
			"width": 150
		},
		{
			"fieldname": "severity",
			"label": _("Severity"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "resolution_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "responder",
			"label": _("Responder"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "response_time_minutes",
			"label": _("Response Time (min)"),
			"fieldtype": "Float",
			"width": 130
		},
		{
			"fieldname": "resolution_time",
			"label": _("Resolved At"),
			"fieldtype": "Datetime",
			"width": 150
		}
	]


def get_data(filters):
	"""Get report data based on filters"""
	conditions = get_conditions(filters)
	
	query = """
		SELECT
			lwa.name,
			lwa.raised_at as alert_timestamp,
			lwa.human,
			hp.full_name,
			lwa.alert_type,
			lwa.zone,
			lwa.severity,
			lwa.resolution_status,
			lwa.responder,
			lwa.response_time,
			lwa.resolution_notes as resolution_time
		FROM
			`tabLone Worker Alert` lwa
		LEFT JOIN
			`tabHuman Profile` hp ON lwa.human = hp.name
		WHERE
			lwa.docstatus < 2
			{conditions}
		ORDER BY
			lwa.raised_at DESC
	""".format(conditions=conditions)

	data = frappe.db.sql(query, filters, as_dict=1)

	# Calculate response time in minutes from duration field
	for row in data:
		if row.response_time:
			# response_time is in seconds (Duration field)
			row["response_time_minutes"] = round(row.response_time / 60, 2)
		else:
			row["response_time_minutes"] = None

	return data


def get_conditions(filters):
	"""Build WHERE conditions based on filters"""
	conditions = []

	if filters.get("from_date"):
		conditions.append("AND lwa.raised_at >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND lwa.raised_at <= %(to_date)s")

	if filters.get("human"):
		conditions.append("AND lwa.human = %(human)s")

	if filters.get("zone"):
		conditions.append("AND lwa.zone = %(zone)s")

	if filters.get("severity"):
		conditions.append("AND lwa.severity = %(severity)s")

	if filters.get("resolution_status"):
		conditions.append("AND lwa.resolution_status = %(resolution_status)s")

	if filters.get("alert_type"):
		conditions.append("AND lwa.alert_type = %(alert_type)s")

	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for alert severity distribution"""
	severity_counts = {}
	for row in data:
		severity = row.get("severity", "Unknown")
		severity_counts[severity] = severity_counts.get(severity, 0) + 1
	
	return {
		"data": {
			"labels": list(severity_counts.keys()),
			"datasets": [{"name": "Alerts", "values": list(severity_counts.values())}]
		},
		"type": "donut",
		"colors": ["#F44336", "#FF9800", "#FFC107", "#4CAF50"]
	}


def get_summary(data):
	"""Generate summary statistics"""
	total_alerts = len(data)
	open_alerts = len([d for d in data if d["resolution_status"] == "Open"])
	resolved_alerts = len([d for d in data if d["resolution_status"] == "Resolved"])
	critical_alerts = len([d for d in data if d["severity"] == "Critical"])
	
	avg_response_time = 0
	response_times = [d["response_time_minutes"] for d in data if d.get("response_time_minutes")]
	if response_times:
		avg_response_time = round(sum(response_times) / len(response_times), 2)
	
	return [
		{"label": _("Total Alerts"), "value": total_alerts, "indicator": "Blue"},
		{"label": _("Open Alerts"), "value": open_alerts, "indicator": "Red"},
		{"label": _("Resolved Alerts"), "value": resolved_alerts, "indicator": "Green"},
		{"label": _("Critical Alerts"), "value": critical_alerts, "indicator": "Red"},
		{"label": _("Avg Response Time (min)"), "value": avg_response_time, "indicator": "Orange"}
	]

