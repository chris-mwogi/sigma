// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Lone Worker Incidents Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Datetime",
			"default": frappe.datetime.add_days(frappe.datetime.now_datetime(), -30),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Datetime",
			"default": frappe.datetime.now_datetime(),
			"reqd": 1
		},
		{
			"fieldname": "human",
			"label": __("Personnel"),
			"fieldtype": "Link",
			"options": "Human Profile"
		},
		{
			"fieldname": "zone",
			"label": __("Zone"),
			"fieldtype": "Link",
			"options": "Zone Configuration"
		},
		{
			"fieldname": "severity",
			"label": __("Severity"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		},
		{
			"fieldname": "resolution_status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOpen\nAcknowledged\nResolved\nFalse Alarm"
		},
		{
			"fieldname": "alert_type",
			"label": __("Alert Type"),
			"fieldtype": "Select",
			"options": "\nLone Worker Timeout\nPanic Button\nNo Movement\nZone Breach\nMax Duration Exceeded\nMissed Check-In\nDevice Offline"
		}
	]
};

