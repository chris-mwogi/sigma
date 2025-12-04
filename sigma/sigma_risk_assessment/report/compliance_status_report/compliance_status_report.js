// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.query_reports["Compliance Status Report"] = {
	"filters": [
		{
			"fieldname": "requirement_type",
			"label": __("Requirement Type"),
			"fieldtype": "Select",
			"options": "\nRegulatory\nStatutory\nContractual\nInternal Policy\nIndustry Standard\nBest Practice"
		},
		{
			"fieldname": "regulatory_framework",
			"label": __("Regulatory Framework"),
			"fieldtype": "Select",
			"options": "\nISO 31000\nISO 9001\nISO 27001\nGDPR\nSOX\nHIPAA\nPCI DSS\nCOSO\nNIST\nOther"
		},
		{
			"fieldname": "compliance_owner",
			"label": __("Compliance Owner"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname": "compliance_status",
			"label": __("Compliance Status"),
			"fieldtype": "Select",
			"options": "\nNot Started\nIn Progress\nCompliant\nPartially Compliant\nNon-Compliant\nUnder Review"
		},
		{
			"fieldname": "priority",
			"label": __("Priority"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nCritical"
		},
		{
			"fieldname": "show_overdue_only",
			"label": __("Show Overdue Only"),
			"fieldtype": "Check"
		}
	]
};

