# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, nowdate


def execute(filters=None):
	"""
	SLA Compliance Report
	Shows SLA compliance metrics for service contracts including:
	- Contract details
	- SLA targets
	- Actual performance
	- Compliance percentage
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "contract_name",
			"label": _("Contract"),
			"fieldtype": "Link",
			"options": "Service Contract",
			"width": 180
		},
		{
			"fieldname": "service_provider",
			"label": _("Service Provider"),
			"fieldtype": "Link",
			"options": "Service Provider",
			"width": 180
		},
		{
			"fieldname": "contract_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "start_date",
			"label": _("Start Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "end_date",
			"label": _("End Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "sla_response_time",
			"label": _("SLA Response Time (hrs)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "avg_response_time",
			"label": _("Avg Response Time (hrs)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "incidents_count",
			"label": _("Total Incidents"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "sla_met_count",
			"label": _("SLA Met"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "compliance_rate",
			"label": _("Compliance %"),
			"fieldtype": "Percent",
			"width": 120
		}
	]


def get_data(filters):
	"""Get report data"""
	# Check if Service Contract DocType exists
	if not frappe.db.exists("DocType", "Service Contract"):
		return []

	conditions = get_conditions(filters)

	# Get all service contracts
	query = f"""
		SELECT
			name as contract_name,
			service_provider,
			contract_status,
			start_date,
			end_date
		FROM `tabService Contract`
		WHERE 1=1
		{conditions}
		ORDER BY start_date DESC
	"""

	contracts = frappe.db.sql(query, filters or {}, as_dict=1)

	# Set default SLA response time (24 hours)
	for contract in contracts:
		contract.sla_response_time = 24.0
	
	# For each contract, calculate SLA compliance
	for contract in contracts:
		# Get incidents related to this contract's service provider
		incidents = frappe.db.sql("""
			SELECT 
				name,
				incident_date,
				response_time_hours
			FROM `tabGuard Incident`
			WHERE service_provider = %(provider)s
			AND incident_date BETWEEN %(start_date)s AND COALESCE(%(end_date)s, CURDATE())
		""", {
			"provider": contract.service_provider,
			"start_date": contract.start_date,
			"end_date": contract.end_date or nowdate()
		}, as_dict=1)
		
		contract.incidents_count = len(incidents)
		
		if contract.incidents_count > 0:
			# Calculate average response time
			total_response_time = sum([inc.response_time_hours or 0 for inc in incidents])
			contract.avg_response_time = total_response_time / contract.incidents_count
			
			# Count incidents that met SLA
			sla_target = contract.sla_response_time or 24  # Default 24 hours
			contract.sla_met_count = sum([
				1 for inc in incidents 
				if inc.response_time_hours and inc.response_time_hours <= sla_target
			])
			
			# Calculate compliance rate
			contract.compliance_rate = contract.sla_met_count / contract.incidents_count
		else:
			contract.avg_response_time = 0
			contract.sla_met_count = 0
			contract.compliance_rate = 1.0  # 100% if no incidents
	
	return contracts


def get_conditions(filters):
	"""Build SQL conditions from filters"""
	conditions = []

	if filters and filters.get("service_provider"):
		conditions.append("AND service_provider = %(service_provider)s")

	if filters and filters.get("contract_status"):
		conditions.append("AND contract_status = %(contract_status)s")

	if filters and filters.get("from_date"):
		conditions.append("AND start_date >= %(from_date)s")

	if filters and filters.get("to_date"):
		conditions.append("AND end_date <= %(to_date)s")

	return " ".join(conditions)

