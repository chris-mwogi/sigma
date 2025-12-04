// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["KRI Dashboard Report"] = {
	"filters": [
		{
			"fieldname": "kri_category",
			"label": __("KRI Category"),
			"fieldtype": "Select",
			"options": "\nFinancial\nOperational\nCompliance\nStrategic\nReputational\nTechnology"
		},
		{
			"fieldname": "linked_risk",
			"label": __("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register"
		},
		{
			"fieldname": "kri_owner",
			"label": __("KRI Owner"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname": "current_status",
			"label": __("Current Status"),
			"fieldtype": "Select",
			"options": "\nNormal\nWarning\nCritical"
		},
		{
			"fieldname": "trend",
			"label": __("Trend"),
			"fieldtype": "Select",
			"options": "\nImproving\nStable\nDeteriorating"
		}
	]
};

