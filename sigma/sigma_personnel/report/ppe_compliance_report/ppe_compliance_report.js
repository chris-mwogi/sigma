// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["PPE Compliance Report"] = {
	"filters": [
		{
			"fieldname": "person_type",
			"label": __("Person Type"),
			"fieldtype": "Select",
			"options": "\nEmployee\nContractor\nVisitor\nVendor"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "clearance_level",
			"label": __("Clearance Level"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nActive\nInactive\nSuspended"
		}
	]
};

