# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Incident Trend Analysis Report
	Shows incident trends over time by type, location, zone, and severity
	"""
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart


def get_columns(filters):
	"""Define report columns"""
	columns = [
		{
			"fieldname": "period",
			"label": _("Period"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "incident_type",
			"label": _("Incident Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "location",
			"label": _("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"width": 180
		}
	]

	# Add zone column if zone filtering is available
	if filters and (filters.get("zone") or filters.get("group_by_zone")):
		columns.append({
			"fieldname": "zone",
			"label": _("Zone"),
			"fieldtype": "Link",
			"options": "Zone Configuration",
			"width": 150
		})

	columns.extend([
		{
			"fieldname": "severity",
			"label": _("Severity"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "incident_count",
			"label": _("Incident Count"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "avg_response_time",
			"label": _("Avg Response Time (hrs)"),
			"fieldtype": "Float",
			"width": 160
		},
		{
			"fieldname": "resolved_count",
			"label": _("Resolved"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "resolution_rate",
			"label": _("Resolution Rate"),
			"fieldtype": "Percent",
			"width": 130
		}
	])

	return columns


def get_data(filters):
	"""Get report data"""
	conditions = get_conditions(filters)
	group_by = get_group_by(filters)

	# Determine if zone should be included
	include_zone = filters and (filters.get("zone") or filters.get("group_by_zone"))
	zone_select = ", zone" if include_zone else ""
	zone_group = ", zone" if include_zone else ""

	# Get incident trends
	query = f"""
		SELECT
			{get_period_expression(filters)} as period,
			category as incident_type,
			location{zone_select},
			'Medium' as severity,
			COUNT(*) as incident_count,
			0 as avg_response_time,
			SUM(CASE WHEN incident_status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
		FROM `tabGuard Incident`
		WHERE 1=1
		{conditions}
		GROUP BY {group_by}{zone_group}
		ORDER BY period DESC, incident_count DESC
	"""

	data = frappe.db.sql(query, filters or {}, as_dict=1)

	# Calculate resolution rate
	for row in data:
		if row.incident_count > 0:
			row.resolution_rate = (row.resolved_count or 0) / row.incident_count
		else:
			row.resolution_rate = 0

	return data


def get_period_expression(filters):
	"""Get SQL expression for period grouping"""
	period = filters.get("period", "Monthly") if filters else "Monthly"

	if period == "Daily":
		return "DATE(reported_on)"
	elif period == "Weekly":
		return "DATE_FORMAT(reported_on, '%%Y-W%%u')"
	elif period == "Monthly":
		return "DATE_FORMAT(reported_on, '%%Y-%%m')"
	elif period == "Quarterly":
		return "CONCAT(YEAR(reported_on), '-Q', QUARTER(reported_on))"
	elif period == "Yearly":
		return "YEAR(reported_on)"
	else:
		return "DATE_FORMAT(reported_on, '%%Y-%%m')"


def get_group_by(filters):
	"""Get GROUP BY clause"""
	period_expr = get_period_expression(filters)
	return f"{period_expr}, category, location"


def get_conditions(filters):
	"""Build SQL conditions from filters"""
	conditions = []

	if filters and filters.get("from_date"):
		conditions.append("AND DATE(reported_on) >= %(from_date)s")

	if filters and filters.get("to_date"):
		conditions.append("AND DATE(reported_on) <= %(to_date)s")

	if filters and filters.get("incident_type"):
		conditions.append("AND category = %(incident_type)s")

	if filters and filters.get("location"):
		conditions.append("AND location = %(location)s")

	if filters and filters.get("zone"):
		conditions.append("AND zone = %(zone)s")

	return " ".join(conditions)


def get_chart_data(data, filters):
	"""Generate chart data for visualization"""
	if not data:
		return None
	
	# Group data by period for chart
	periods = []
	incident_counts = []
	
	period_data = {}
	for row in data:
		period = row.period
		if period not in period_data:
			period_data[period] = 0
		period_data[period] += row.incident_count
	
	# Sort by period
	for period in sorted(period_data.keys()):
		periods.append(str(period))
		incident_counts.append(period_data[period])
	
	return {
		"data": {
			"labels": periods,
			"datasets": [
				{
					"name": "Incident Count",
					"values": incident_counts
				}
			]
		},
		"type": "line",
		"colors": ["#ff6384"]
	}

