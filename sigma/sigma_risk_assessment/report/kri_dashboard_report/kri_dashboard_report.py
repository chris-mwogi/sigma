# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	"""Return columns for the report"""
	return [
		{
			"fieldname": "name",
			"label": _("KRI ID"),
			"fieldtype": "Link",
			"options": "Key Risk Indicator",
			"width": 120
		},
		{
			"fieldname": "kri_name",
			"label": _("KRI Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "kri_category",
			"label": _("Category"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "linked_risk",
			"label": _("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register",
			"width": 120
		},
		{
			"fieldname": "kri_owner",
			"label": _("KRI Owner"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"fieldname": "current_value",
			"label": _("Current Value"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "target_value",
			"label": _("Target Value"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "unit_of_measurement",
			"label": _("Unit"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "current_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 90
		},
		{
			"fieldname": "trend",
			"label": _("Trend"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "threshold_green",
			"label": _("Green"),
			"fieldtype": "Float",
			"width": 80
		},
		{
			"fieldname": "threshold_yellow",
			"label": _("Yellow"),
			"fieldtype": "Float",
			"width": 80
		},
		{
			"fieldname": "threshold_red",
			"label": _("Red"),
			"fieldtype": "Float",
			"width": 80
		},
		{
			"fieldname": "last_reading_date",
			"label": _("Last Reading"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "measurement_frequency",
			"label": _("Frequency"),
			"fieldtype": "Data",
			"width": 100
		}
	]


def get_data(filters):
	"""Get data for the report"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			name,
			kri_name,
			kri_category,
			linked_risk,
			kri_owner,
			current_value,
			target_value,
			unit_of_measurement,
			current_status,
			trend,
			threshold_green,
			threshold_yellow,
			threshold_red,
			last_reading_date,
			measurement_frequency
		FROM
			`tabKey Risk Indicator`
		WHERE
			status = 'Active'
			{conditions}
		ORDER BY
			CASE current_status
				WHEN 'Critical' THEN 1
				WHEN 'Warning' THEN 2
				WHEN 'Normal' THEN 3
				ELSE 4
			END,
			kri_category
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("kri_category"):
		conditions.append("AND kri_category = %(kri_category)s")
	
	if filters.get("linked_risk"):
		conditions.append("AND linked_risk = %(linked_risk)s")
	
	if filters.get("kri_owner"):
		conditions.append("AND kri_owner = %(kri_owner)s")
	
	if filters.get("current_status"):
		conditions.append("AND current_status = %(current_status)s")
	
	if filters.get("trend"):
		conditions.append("AND trend = %(trend)s")
	
	return " ".join(conditions)


def get_chart_data(data):
	"""Generate chart data for KRI status visualization"""
	# Count by status
	status_counts = {"Normal": 0, "Warning": 0, "Critical": 0}
	for row in data:
		status = row.get("current_status")
		if status in status_counts:
			status_counts[status] += 1
	
	chart = {
		"data": {
			"labels": ["Normal", "Warning", "Critical"],
			"datasets": [
				{
					"name": "KRI Status Distribution",
					"values": [
						status_counts["Normal"],
						status_counts["Warning"],
						status_counts["Critical"]
					]
				}
			]
		},
		"type": "bar",
		"colors": ["#28a745", "#ffc107", "#dc3545"]
	}
	
	return chart

