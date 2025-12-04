// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["Risk Register Report"] = {
	"filters": [
		{
			"fieldname": "risk_category",
			"label": __("Risk Category"),
			"fieldtype": "Link",
			"options": "Risk Category"
		},
		{
			"fieldname": "risk_owner",
			"label": __("Risk Owner"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nActive\nUnder Review\nMitigated\nAccepted\nClosed"
		},
		{
			"fieldname": "current_risk_rating",
			"label": __("Current Risk Rating"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	]
};

