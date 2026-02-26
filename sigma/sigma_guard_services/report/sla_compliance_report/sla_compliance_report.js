// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.query_reports["SLA Compliance Report"] = {
	"filters": [
		{
			"fieldname": "service_provider",
			"label": __("Service Provider"),
			"fieldtype": "Link",
			"options": "Service Provider"
		},
		{
			"fieldname": "contract_status",
			"label": __("Contract Status"),
			"fieldtype": "Select",
			"options": "\nActive\nExpired\nPending\nCancelled"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
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

