// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Resource Utilization Report"] = {
	"filters": [
		{
			"fieldname": "resource_type",
			"label": __("Resource Type"),
			"fieldtype": "Select",
			"options": "\nGuard\nSecurity Guard\nSecurity Supervisor\nVehicle\nEquipment"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nAvailable\nDeployed\nOn Leave\nInactive"
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
		}
	],
	
	onload: function(report) {
		// Clear zone when location changes
		report.page.fields_dict.location.$input.on('change', function() {
			frappe.query_report.set_filter_value('zone', '');
		});
	}
};

