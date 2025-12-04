# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""Asset Health Dashboard - Shows real-time health status of all monitored assets."""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	
	return columns, data, None, chart, summary


def get_columns():
	"""Define report columns."""
	return [
		{
			"fieldname": "asset_name",
			"label": _("Asset"),
			"fieldtype": "Link",
			"options": "Asset",
			"width": 200
		},
		{
			"fieldname": "asset_category_sigma",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Asset Category Sigma",
			"width": 150
		},
		{
			"fieldname": "criticality_rating",
			"label": _("Criticality"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "health_status",
			"label": _("Health Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "condition_index",
			"label": _("Condition"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "risk_classification",
			"label": _("Risk Level"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "monitored_device",
			"label": _("Monitored Device"),
			"fieldtype": "Link",
			"options": "Monitored Device",
			"width": 150
		},
		{
			"fieldname": "last_telemetry_update",
			"label": _("Last Telemetry"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "alert_count",
			"label": _("Open Alerts"),
			"fieldtype": "Int",
			"width": 100
		}
	]


def get_data(filters):
	"""Get asset health data with monitoring information."""
	conditions = []
	
	if filters and filters.get("criticality_rating"):
		conditions.append(f"a.criticality_rating = '{filters.get('criticality_rating')}'")
	
	if filters and filters.get("health_status"):
		conditions.append(f"a.health_status = '{filters.get('health_status')}'")
	
	where_clause = " AND " + " AND ".join(conditions) if conditions else ""
	
	query = f"""
		SELECT
			a.name as asset_name,
			a.asset_category_sigma,
			a.criticality_rating,
			a.health_status,
			a.condition_index,
			a.risk_score,
			a.risk_classification,
			a.monitored_device,
			a.last_telemetry_update,
			(SELECT COUNT(*) FROM `tabMonitoring Alert` 
			 WHERE asset = a.name AND workflow_state IN ('Open', 'Acknowledged')) as alert_count
		FROM `tabAsset` a
		WHERE a.docstatus < 2
		  AND a.asset_category_sigma IS NOT NULL
		  {where_clause}
		ORDER BY a.risk_score DESC, a.criticality_rating DESC
	"""
	
	return frappe.db.sql(query, as_dict=1)


def get_chart_data(data):
	"""Generate chart data for health status distribution."""
	health_counts = {}
	for row in data:
		status = row.get("health_status") or "Unknown"
		health_counts[status] = health_counts.get(status, 0) + 1
	
	return {
		"data": {
			"labels": list(health_counts.keys()),
			"datasets": [
				{
					"name": "Asset Count",
					"values": list(health_counts.values())
				}
			]
		},
		"type": "donut",
		"colors": ["#28a745", "#ffc107", "#dc3545", "#6c757d", "#17a2b8"]
	}


def get_summary(data):
	"""Generate summary statistics."""
	total_assets = len(data)
	critical_assets = len([d for d in data if d.get("criticality_rating") == "Critical"])
	unhealthy_assets = len([d for d in data if d.get("health_status") in ["Warning", "Critical", "Failed"]])
	high_risk_assets = len([d for d in data if d.get("risk_classification") in ["High Risk", "Very High Risk"]])
	assets_with_alerts = len([d for d in data if d.get("alert_count", 0) > 0])
	
	return [
		{
			"value": total_assets,
			"label": "Total Assets",
			"datatype": "Int",
			"indicator": "Blue"
		},
		{
			"value": critical_assets,
			"label": "Critical Assets",
			"datatype": "Int",
			"indicator": "Red"
		},
		{
			"value": unhealthy_assets,
			"label": "Unhealthy Assets",
			"datatype": "Int",
			"indicator": "Orange"
		},
		{
			"value": high_risk_assets,
			"label": "High Risk Assets",
			"datatype": "Int",
			"indicator": "Red"
		},
		{
			"value": assets_with_alerts,
			"label": "Assets with Alerts",
			"datatype": "Int",
			"indicator": "Orange"
		}
	]

