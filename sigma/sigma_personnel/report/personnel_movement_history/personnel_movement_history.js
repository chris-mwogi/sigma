// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Personnel Movement History"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Datetime",
			"default": frappe.datetime.add_days(frappe.datetime.now_datetime(), -7),
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
			"fieldname": "person_type",
			"label": __("Person Type"),
			"fieldtype": "Select",
			"options": "\nEmployee\nContractor\nVisitor\nVendor"
		},
		{
			"fieldname": "source_type",
			"label": __("Source Type"),
			"fieldtype": "Select",
			"options": "\nRFID\nBLE\nGPS\nCCTV\nManual\nLoRa\nWiFi"
		}
	]
};

