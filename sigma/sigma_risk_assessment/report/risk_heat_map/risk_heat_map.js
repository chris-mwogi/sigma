// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["Risk Heat Map"] = {
	"filters": [
		{
			"fieldname": "risk_type",
			"label": __("Risk Type"),
			"fieldtype": "Select",
			"options": "Residual\nInherent",
			"default": "Residual",
			"reqd": 1
		},
		{
			"fieldname": "risk_category",
			"label": __("Risk Category"),
			"fieldtype": "Link",
			"options": "Risk Category"
		},
		{
			"fieldname": "assessment_type",
			"label": __("Assessment Type"),
			"fieldtype": "Select",
			"options": "\nInitial\nPeriodic\nIncident-Triggered\nAd-hoc"
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

