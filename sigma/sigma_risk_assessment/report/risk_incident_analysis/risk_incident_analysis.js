// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["Risk Incident Analysis"] = {
	"filters": [
		{
			"fieldname": "incident_type",
			"label": __("Incident Type"),
			"fieldtype": "Select",
			"options": "\nRisk Event\nControl Failure\nCompliance Breach\nSecurity Incident\nOperational Failure\nFinancial Loss\nOther"
		},
		{
			"fieldname": "incident_category",
			"label": __("Incident Category"),
			"fieldtype": "Link",
			"options": "Risk Category"
		},
		{
			"fieldname": "incident_status",
			"label": __("Incident Status"),
			"fieldtype": "Select",
			"options": "\nReported\nUnder Investigation\nContained\nResolved\nClosed"
		},
		{
			"fieldname": "impact_level",
			"label": __("Impact Level"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		},
		{
			"fieldname": "linked_risk",
			"label": __("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register"
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

