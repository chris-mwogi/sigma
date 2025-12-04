# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	
	return columns, data, None, chart, summary


def get_columns():
	return [
		{
			"fieldname": "investigation_id",
			"label": _("Investigation ID"),
			"fieldtype": "Link",
			"options": "Case Investigation",
			"width": 150
		},
		{
			"fieldname": "investigation_title",
			"label": _("Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "linked_case",
			"label": _("Linked Case"),
			"fieldtype": "Link",
			"options": "Case",
			"width": 150
		},
		{
			"fieldname": "investigation_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "start_date",
			"label": _("Start Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "target_completion_date",
			"label": _("Target Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "actual_completion_date",
			"label": _("Actual Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "planned_days",
			"label": _("Planned Days"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "actual_days",
			"label": _("Actual Days"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "variance",
			"label": _("Variance"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "sla_status",
			"label": _("SLA Status"),
			"fieldtype": "Data",
			"width": 120
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			ci.name as investigation_id,
			ci.investigation_title,
			ci.linked_case,
			ci.investigation_type,
			ci.status,
			ci.start_date,
			ci.target_completion_date,
			ci.actual_completion_date,
			ci.lead_investigator
		FROM
			`tabCase Investigation` ci
		WHERE
			ci.docstatus < 2
			{conditions}
		ORDER BY
			ci.start_date DESC
	""", filters, as_dict=1)
	
	# Calculate SLA metrics
	for row in data:
		start = row.get("start_date")
		target = row.get("target_completion_date")
		actual = row.get("actual_completion_date")
		
		if start and target:
			row["planned_days"] = date_diff(getdate(target), getdate(start))
		else:
			row["planned_days"] = 0
		
		if start and actual:
			row["actual_days"] = date_diff(getdate(actual), getdate(start))
			row["variance"] = row["actual_days"] - row["planned_days"]
			
			if row["variance"] <= 0:
				row["sla_status"] = "On Time"
			else:
				row["sla_status"] = "Delayed"
		else:
			row["actual_days"] = 0
			row["variance"] = 0
			if row.get("status") == "Completed":
				row["sla_status"] = "Unknown"
			else:
				row["sla_status"] = "In Progress"
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("ci.start_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("ci.start_date <= %(to_date)s")
	
	if filters.get("investigation_type"):
		conditions.append("ci.investigation_type = %(investigation_type)s")
	
	if filters.get("status"):
		conditions.append("ci.status = %(status)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
	if not data:
		return None
	
	# SLA status distribution
	sla_counts = {"On Time": 0, "Delayed": 0, "In Progress": 0, "Unknown": 0}
	
	for row in data:
		status = row.get("sla_status", "Unknown")
		sla_counts[status] = sla_counts.get(status, 0) + 1
	
	return {
		"data": {
			"labels": list(sla_counts.keys()),
			"datasets": [
				{
					"name": "Investigation SLA Status",
					"values": list(sla_counts.values())
				}
			]
		},
		"type": "pie",
		"colors": ["#4CAF50", "#F44336", "#FFC107", "#9E9E9E"]
	}


def get_summary(data):
	if not data:
		return []
	
	completed = [d for d in data if d.get("status") == "Completed" and d.get("actual_days")]
	on_time = [d for d in completed if d.get("sla_status") == "On Time"]
	
	total_completed = len(completed)
	total_on_time = len(on_time)
	
	adherence_rate = (total_on_time / total_completed * 100) if total_completed > 0 else 0
	
	return [
		{
			"value": total_completed,
			"indicator": "Blue",
			"label": "Total Completed",
			"datatype": "Int"
		},
		{
			"value": total_on_time,
			"indicator": "Green",
			"label": "Completed On Time",
			"datatype": "Int"
		},
		{
			"value": adherence_rate,
			"indicator": "Green" if adherence_rate >= 80 else "Red",
			"label": "SLA Adherence Rate (%)",
			"datatype": "Percent"
		}
	]

