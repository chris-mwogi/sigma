// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["Risk Treatment Status Report"] = {
	"filters": [
		{
			"fieldname": "linked_risk",
			"label": __("Linked Risk"),
			"fieldtype": "Link",
			"options": "Risk Register"
		},
		{
			"fieldname": "treatment_strategy",
			"label": __("Treatment Strategy"),
			"fieldtype": "Select",
			"options": "\nAvoid\nReduce\nTransfer\nAccept"
		},
		{
			"fieldname": "plan_owner",
			"label": __("Plan Owner"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nPlanned\nIn Progress\nOn Hold\nCompleted\nCancelled"
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

