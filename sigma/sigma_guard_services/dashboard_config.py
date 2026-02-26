# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Dashboard configurations for Sigma Guard Monitoring module.
These configurations define the dashboard layouts and components.
"""

# Provider Performance Scorecard Configuration
PROVIDER_PERFORMANCE_SCORECARD = {
	"name": "Provider Performance Scorecard",
	"module": "Sigma Guard Monitoring",
	"charts": [
		{
			"chart_name": "Provider Compliance Rate",
			"chart_type": "Bar",
			"doctype": "Contract",
			"x_field": "supplier",
			"y_field": "compliance_rate",
			"title": "Provider Compliance Rate (%)"
		},
		{
			"chart_name": "Provider Surcharges",
			"chart_type": "Bar",
			"doctype": "Surcharge Record",
			"x_field": "supplier",
			"y_field": "surcharge_amount",
			"title": "Total Surcharges by Provider"
		},
		{
			"chart_name": "Patrol Completion Rate",
			"chart_type": "Bar",
			"doctype": "Patrol Schedule",
			"x_field": "supplier",
			"y_field": "completion_rate",
			"title": "Patrol Completion Rate by Provider (%)"
		}
	],
	"cards": [
		{
			"label": "Total Active Providers",
			"indicator": "total_providers",
			"color": "blue"
		},
		{
			"label": "Average Compliance Rate",
			"indicator": "avg_compliance_rate",
			"color": "green"
		},
		{
			"label": "Total Surcharges",
			"indicator": "total_surcharges",
			"color": "red"
		}
	]
}

# SLA Compliance Trends Configuration
SLA_COMPLIANCE_TRENDS = {
	"name": "SLA Compliance Trends",
	"module": "Sigma Guard Monitoring",
	"charts": [
		{
			"chart_name": "Compliance Trend",
			"chart_type": "Line",
			"doctype": "SLA Compliance Record",
			"x_field": "compliance_date",
			"y_field": "compliance_score",
			"title": "SLA Compliance Score Trend (30 Days)"
		},
		{
			"chart_name": "Compliance Status Distribution",
			"chart_type": "Pie",
			"doctype": "SLA Compliance Record",
			"x_field": "compliance_status",
			"y_field": "count",
			"title": "Compliance Status Distribution"
		},
		{
			"chart_name": "Daily Compliance Rate",
			"chart_type": "Bar",
			"doctype": "SLA Compliance Record",
			"x_field": "compliance_date",
			"y_field": "compliance_rate",
			"title": "Daily Compliance Rate (%)"
		}
	],
	"cards": [
		{
			"label": "Current Compliance Rate",
			"indicator": "current_compliance_rate",
			"color": "green"
		},
		{
			"label": "Average Compliance Score",
			"indicator": "avg_compliance_score",
			"color": "blue"
		},
		{
			"label": "Compliance Notices",
			"indicator": "total_notices",
			"color": "orange"
		}
	]
}

# Financial Impact Report Configuration
FINANCIAL_IMPACT_REPORT = {
	"name": "Financial Impact Report",
	"module": "Sigma Guard Monitoring",
	"charts": [
		{
			"chart_name": "Surcharges Over Time",
			"chart_type": "Line",
			"doctype": "Surcharge Record",
			"x_field": "surcharge_date",
			"y_field": "surcharge_amount",
			"title": "Surcharges Over Time"
		},
		{
			"chart_name": "Surcharge by Method",
			"chart_type": "Pie",
			"doctype": "Surcharge Record",
			"x_field": "surcharge_method",
			"y_field": "surcharge_amount",
			"title": "Surcharges by Calculation Method"
		},
		{
			"chart_name": "Debit Notes",
			"chart_type": "Bar",
			"doctype": "Debit Note",
			"x_field": "supplier",
			"y_field": "total",
			"title": "Debit Notes by Supplier"
		}
	],
	"cards": [
		{
			"label": "Total Surcharges",
			"indicator": "total_surcharges",
			"color": "red"
		},
		{
			"label": "Total Debit Notes",
			"indicator": "total_debit_notes",
			"color": "orange"
		},
		{
			"label": "Total Financial Impact",
			"indicator": "total_financial_impact",
			"color": "red"
		}
	]
}

# Patrol Summary Report Configuration
PATROL_SUMMARY_REPORT = {
	"name": "Patrol Summary Report",
	"module": "Sigma Guard Monitoring",
	"charts": [
		{
			"chart_name": "Patrol Completion Status",
			"chart_type": "Pie",
			"doctype": "Patrol Schedule",
			"x_field": "status",
			"y_field": "count",
			"title": "Patrol Schedule Status Distribution"
		},
		{
			"chart_name": "Discrepancies by Severity",
			"chart_type": "Bar",
			"doctype": "Discrepancy Report",
			"x_field": "severity",
			"y_field": "count",
			"title": "Discrepancies by Severity"
		},
		{
			"chart_name": "Verification Discrepancy Rate",
			"chart_type": "Line",
			"doctype": "Patrol Verification Record",
			"x_field": "verification_date",
			"y_field": "discrepancy_rate",
			"title": "Verification Discrepancy Rate Over Time"
		}
	],
	"cards": [
		{
			"label": "Total Patrol Schedules",
			"indicator": "total_schedules",
			"color": "blue"
		},
		{
			"label": "Completion Rate",
			"indicator": "completion_rate",
			"color": "green"
		},
		{
			"label": "Total Discrepancies",
			"indicator": "total_discrepancies",
			"color": "red"
		}
	]
}

# Main Dashboard Configuration
MAIN_DASHBOARD = {
	"name": "Sigma Guard Monitoring Dashboard",
	"module": "Sigma Guard Monitoring",
	"sections": [
		{
			"title": "Key Performance Indicators",
			"cards": [
				{
					"label": "Active Deployments",
					"indicator": "active_deployments",
					"color": "blue"
				},
				{
					"label": "Compliance Rate",
					"indicator": "compliance_rate",
					"color": "green"
				},
				{
					"label": "Patrol Completion",
					"indicator": "patrol_completion",
					"color": "blue"
				},
				{
					"label": "Active Visitors",
					"indicator": "active_visitors",
					"color": "purple"
				}
			]
		},
		{
			"title": "Resource Management",
			"charts": [
				{
					"chart_name": "Resource Deployment by Type",
					"chart_type": "Pie"
				},
				{
					"chart_name": "Resource Availability",
					"chart_type": "Bar"
				}
			]
		},
		{
			"title": "Compliance & SLA",
			"charts": [
				{
					"chart_name": "Compliance Trend",
					"chart_type": "Line"
				},
				{
					"chart_name": "Compliance Status",
					"chart_type": "Pie"
				}
			]
		},
		{
			"title": "Patrol & Verification",
			"charts": [
				{
					"chart_name": "Patrol Completion Status",
					"chart_type": "Pie"
				},
				{
					"chart_name": "Discrepancies by Severity",
					"chart_type": "Bar"
				}
			]
		},
		{
			"title": "Financial Metrics",
			"charts": [
				{
					"chart_name": "Surcharges Over Time",
					"chart_type": "Line"
				},
				{
					"chart_name": "Surcharge by Method",
					"chart_type": "Pie"
				}
			]
		}
	]
}

