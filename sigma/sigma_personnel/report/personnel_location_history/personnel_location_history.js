// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Personnel Location History"] = {
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
			"fieldname": "human",
			"label": __("Personnel"),
			"fieldtype": "Link",
			"options": "Human Profile"
		},
		{
			"fieldname": "event_type",
			"label": __("Event Type"),
			"fieldtype": "Select",
			"options": "\nZone Entry\nZone Exit\nLocation Update\nCheck-in\nCheck-out"
		}
	]
};

