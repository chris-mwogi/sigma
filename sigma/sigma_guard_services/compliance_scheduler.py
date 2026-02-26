# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Automated compliance checking scheduler for SLA monitoring.

Runs daily at 6 AM to:
1. Query all active service contracts
2. Get required resources from contract
3. Check deployed resources for the day
4. Generate SLA Compliance Records
5. Create Compliance Notices for non-compliance
"""

import frappe
from datetime import datetime, timedelta


def run_daily_compliance_check():
	"""
	Main scheduler function - runs daily compliance check.
	Called by Frappe scheduler at configured time (6 AM).
	"""
	frappe.logger().info("Starting daily compliance check...")
	
	try:
		# Get all active contracts
		contracts = frappe.get_all(
			"Contract",
			filters={"status": "Active"},
			fields=["name", "party_name", "contract_value"]
		)
		
		frappe.logger().info(f"Found {len(contracts)} active contracts")
		
		today = datetime.now().date()
		compliance_records_created = 0
		
		for contract in contracts:
			try:
				# Create compliance record for this contract
				compliance_record = create_compliance_record(contract, today)
				if compliance_record:
					compliance_records_created += 1
					frappe.logger().info(f"Created compliance record: {compliance_record}")
			except Exception as e:
				frappe.logger().error(f"Error processing contract {contract['name']}: {str(e)}")
				continue
		
		frappe.logger().info(f"Daily compliance check completed. Created {compliance_records_created} records")
		
	except Exception as e:
		frappe.logger().error(f"Daily compliance check failed: {str(e)}")
		raise


def create_compliance_record(contract, compliance_date):
	"""
	Create a compliance record for a specific contract and date.
	
	Args:
		contract: Contract document dict
		compliance_date: Date to check compliance for
	
	Returns:
		Name of created compliance record or None
	"""
	contract_doc = frappe.get_doc("Contract", contract["name"])
	
	# Get required resources from contract
	required_resources = get_required_resources(contract_doc)
	if not required_resources:
		return None
	
	# Get deployed resources for the date
	deployed_resources = get_deployed_resources(contract_doc, compliance_date)
	
	# Calculate shortfalls
	shortfalls = calculate_shortfalls(required_resources, deployed_resources)
	
	# Determine compliance status
	if not shortfalls:
		compliance_status = "Compliant"
	elif len(shortfalls) < len(required_resources):
		compliance_status = "Partial"
	else:
		compliance_status = "Non-Compliant"
	
	# Create compliance record
	compliance_record = frappe.new_doc("SLA Compliance Record")
	compliance_record.service_contract = contract["name"]
	compliance_record.compliance_date = compliance_date
	compliance_record.compliance_status = compliance_status
	
	# Add required resources
	for req in required_resources:
		compliance_record.append("required_resources", {
			"resource_type": req["resource_type"],
			"required_count": req["required_count"],
			"shift_start": req.get("shift_start"),
			"shift_end": req.get("shift_end")
		})
	
	# Add deployed resources
	for dep in deployed_resources:
		compliance_record.append("deployed_resources", {
			"resource": dep["resource"],
			"resource_type": dep["resource_type"],
			"check_in_time": dep.get("check_in_time"),
			"check_out_time": dep.get("check_out_time"),
			"status": dep.get("status", "Deployed")
		})
	
	# Add shortfalls
	for shortfall in shortfalls:
		compliance_record.append("shortfall_details", {
			"resource_type": shortfall["resource_type"],
			"required_count": shortfall["required_count"],
			"deployed_count": shortfall["deployed_count"],
			"severity": shortfall.get("severity", "Medium")
		})
	
	compliance_record.insert(ignore_permissions=True)
	compliance_record.submit()
	
	return compliance_record.name


def get_required_resources(contract_doc):
	"""
	Get required resources from contract.
	
	Looks for custom field or linked resource requirements.
	"""
	# This would typically come from contract custom fields or linked documents
	# For now, return empty list - to be populated based on contract structure
	return []


def get_deployed_resources(contract_doc, compliance_date):
	"""
	Get deployed resources for a specific contract and date.
	
	Queries Resource Deployment records for the date.
	"""
	deployments = frappe.get_all(
		"Resource Deployment",
		filters={
			"service_contract": contract_doc.name,
			"deployment_date": compliance_date,
			"docstatus": 1  # Only submitted deployments
		},
		fields=["name"]
	)
	
	deployed_resources = []
	for deployment in deployments:
		deployment_doc = frappe.get_doc("Resource Deployment", deployment["name"])
		for item in deployment_doc.resources_table:
			if item.resource:
				resource_doc = frappe.get_doc("Security Resource", item.resource)
				deployed_resources.append({
					"resource": item.resource,
					"resource_type": resource_doc.resource_type,
					"check_in_time": item.check_in_time,
					"check_out_time": item.check_out_time,
					"status": item.status or "Deployed"
				})
	
	return deployed_resources


def calculate_shortfalls(required_resources, deployed_resources):
	"""
	Calculate resource shortfalls by comparing required vs deployed.
	
	Returns list of shortfall records.
	"""
	shortfalls = []
	
	# Group deployed resources by type
	deployed_by_type = {}
	for dep in deployed_resources:
		resource_type = dep["resource_type"]
		deployed_by_type[resource_type] = deployed_by_type.get(resource_type, 0) + 1
	
	# Check each required resource type
	for req in required_resources:
		resource_type = req["resource_type"]
		required_count = req["required_count"]
		deployed_count = deployed_by_type.get(resource_type, 0)
		
		if deployed_count < required_count:
			shortfalls.append({
				"resource_type": resource_type,
				"required_count": required_count,
				"deployed_count": deployed_count,
				"severity": calculate_severity(required_count, deployed_count)
			})
	
	return shortfalls


def calculate_severity(required_count, deployed_count):
	"""Calculate severity based on shortfall percentage"""
	if required_count == 0:
		return "Low"
	
	shortfall_percentage = ((required_count - deployed_count) / required_count) * 100
	
	if shortfall_percentage >= 75:
		return "Critical"
	elif shortfall_percentage >= 50:
		return "High"
	elif shortfall_percentage >= 25:
		return "Medium"
	else:
		return "Low"

