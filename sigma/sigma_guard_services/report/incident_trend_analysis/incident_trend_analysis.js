// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Incident Trend Analysis"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": "Daily\nWeekly\nMonthly\nQuarterly\nYearly",
			"default": "Monthly"
		},
		{
			"fieldname": "incident_type",
			"label": __("Incident Type"),
			"fieldtype": "Select",
			"options": "\nSecurity Breach\nTheft\nVandalism\nUnauthorized Access\nFire\nMedical Emergency\nEquipment Failure\nOther"
		},
		{
			"fieldname": "location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Location"
		},
		{
			"fieldname": "zone",
			"label": __("Zone"),
			"fieldtype": "Link",
			"options": "Zone Configuration",
			"get_query": function() {
				var location = frappe.query_report.get_filter_value('location');
				if (location) {
					return {
						filters: {
							'location': location,
							'is_active': 1
						}
					};
				}
				return {
					filters: {
						'is_active': 1
					}
				};
			}
		},
		{
			"fieldname": "group_by_zone",
			"label": __("Group by Zone"),
			"fieldtype": "Check",
			"default": 0
		}
	],
	
	onload: function(report) {
		// Clear zone when location changes
		report.page.fields_dict.location.$input.on('change', function() {
			frappe.query_report.set_filter_value('zone', '');
		});
	}
};

