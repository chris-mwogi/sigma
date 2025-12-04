// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Lone Worker Monitoring"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nActive\nAcknowledged\nResolved\nEscalated"
		},
		{
			"fieldname": "hazard_level",
			"label": __("Hazard Level"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		}
	]
};

