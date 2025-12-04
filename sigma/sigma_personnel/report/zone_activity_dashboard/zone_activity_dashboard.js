// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Zone Activity Dashboard"] = {
	"filters": [
		{
			"fieldname": "zone_type",
			"label": __("Zone Type"),
			"fieldtype": "Select",
			"options": "\nRestricted\nHazardous\nSecure\nGeneral\nEmergency Assembly"
		}
	]
};

