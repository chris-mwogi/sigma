# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_months, now_datetime
from datetime import datetime, timedelta
from . import report_scripts


# ============================================================================
# PROVIDER PERFORMANCE SCORECARD DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_provider_performance_data(filters=None):
	"""
	Get provider performance metrics for scorecard.
	
	Returns:
		Dictionary with provider performance metrics
	"""
	if filters is None:
		filters = {}
	
	from frappe.query_builder import Query
	from frappe.query_builder.functions import Count, Sum, Avg
	
	# Get all active contracts
	contracts = frappe.get_all(
		"Contract",
		filters={"status": "Active"},
		fields=["name", "supplier", "location"]
	)
	
	provider_metrics = {}
	
	for contract in contracts:
		supplier = contract["supplier"]
		
		if supplier not in provider_metrics:
			provider_metrics[supplier] = {
				"supplier": supplier,
				"total_contracts": 0,
				"active_contracts": 0,
				"compliance_rate": 0,
				"avg_compliance_score": 0,
				"total_surcharges": 0,
				"resource_deployment_rate": 0,
				"patrol_completion_rate": 0
			}
		
		provider_metrics[supplier]["total_contracts"] += 1
		provider_metrics[supplier]["active_contracts"] += 1
		
		# Get compliance records for this contract
		compliance_records = frappe.get_all(
			"SLA Compliance Record",
			filters={"service_contract": contract["name"]},
			fields=["compliance_status", "compliance_score"]
		)
		
		if compliance_records:
			compliant = sum(1 for r in compliance_records if r["compliance_status"] == "Compliant")
			provider_metrics[supplier]["compliance_rate"] = (compliant / len(compliance_records)) * 100
			provider_metrics[supplier]["avg_compliance_score"] = sum(r["compliance_score"] for r in compliance_records) / len(compliance_records)
		
		# Get surcharges for this contract
		surcharges = frappe.get_all(
			"Surcharge Record",
			filters={"service_contract": contract["name"], "docstatus": 1},
			fields=["surcharge_amount"]
		)
		provider_metrics[supplier]["total_surcharges"] = sum(s["surcharge_amount"] for s in surcharges)
		
		# Get patrol completion rate
		patrol_schedules = frappe.get_all(
			"Patrol Schedule",
			filters={"location": contract["location"]},
			fields=["status"]
		)
		
		if patrol_schedules:
			completed = sum(1 for p in patrol_schedules if p["status"] == "Completed")
			provider_metrics[supplier]["patrol_completion_rate"] = (completed / len(patrol_schedules)) * 100
	
	return {
		"status": "success",
		"data": list(provider_metrics.values())
	}


# ============================================================================
# SLA COMPLIANCE TRENDS DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_sla_compliance_trends(filters=None):
	"""
	Get SLA compliance trends over time.
	
	Returns:
		Dictionary with compliance trend data
	"""
	if filters is None:
		filters = {}
	
	# Get date range (default: last 30 days)
	end_date = getdate()
	start_date = end_date - timedelta(days=30)
	
	# Query compliance records grouped by date
	compliance_records = frappe.get_all(
		"SLA Compliance Record",
		filters={
			"compliance_date": [">=", start_date],
			"compliance_date": ["<=", end_date]
		},
		fields=["compliance_date", "compliance_status", "compliance_score"],
		order_by="compliance_date asc"
	)
	
	# Group by date
	daily_data = {}
	for record in compliance_records:
		date_str = str(record["compliance_date"])
		if date_str not in daily_data:
			daily_data[date_str] = {
				"date": date_str,
				"total": 0,
				"compliant": 0,
				"non_compliant": 0,
				"avg_score": 0,
				"scores": []
			}
		
		daily_data[date_str]["total"] += 1
		if record["compliance_status"] == "Compliant":
			daily_data[date_str]["compliant"] += 1
		else:
			daily_data[date_str]["non_compliant"] += 1
		daily_data[date_str]["scores"].append(record["compliance_score"])
	
	# Calculate averages
	for date_str in daily_data:
		scores = daily_data[date_str]["scores"]
		daily_data[date_str]["avg_score"] = sum(scores) / len(scores) if scores else 0
		del daily_data[date_str]["scores"]
	
	return {
		"status": "success",
		"data": list(daily_data.values())
	}


# ============================================================================
# FINANCIAL IMPACT DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_financial_impact_data(filters=None):
	"""
	Get financial impact metrics including surcharges and penalties.
	
	Returns:
		Dictionary with financial metrics
	"""
	if filters is None:
		filters = {}
	
	# Get surcharge records
	surcharges = frappe.get_all(
		"Surcharge Record",
		filters={"docstatus": 1},
		fields=["name", "service_contract", "surcharge_amount", "surcharge_date", "surcharge_method"]
	)
	
	# Get debit notes
	debit_notes = frappe.get_all(
		"Debit Note",
		filters={"docstatus": 1},
		fields=["name", "total", "posting_date"]
	)
	
	# Calculate metrics
	total_surcharges = sum(s["surcharge_amount"] for s in surcharges)
	total_debit_notes = sum(d["total"] for d in debit_notes)
	
	# Group surcharges by method
	surcharge_by_method = {}
	for surcharge in surcharges:
		method = surcharge["surcharge_method"]
		if method not in surcharge_by_method:
			surcharge_by_method[method] = 0
		surcharge_by_method[method] += surcharge["surcharge_amount"]
	
	# Get compliance notices (potential financial impact)
	compliance_notices = frappe.get_all(
		"Compliance Notice",
		filters={"docstatus": 1},
		fields=["name", "surcharge_applicable"]
	)
	
	notices_with_surcharge = sum(1 for n in compliance_notices if n["surcharge_applicable"])
	
	return {
		"status": "success",
		"data": {
			"total_surcharges": total_surcharges,
			"total_debit_notes": total_debit_notes,
			"total_compliance_notices": len(compliance_notices),
			"notices_with_surcharge": notices_with_surcharge,
			"surcharge_by_method": surcharge_by_method,
			"avg_surcharge": total_surcharges / len(surcharges) if surcharges else 0,
			"total_financial_impact": total_surcharges + total_debit_notes
		}
	}


# ============================================================================
# PATROL SUMMARY DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_patrol_summary_data(filters=None):
	"""Get patrol verification summary and discrepancy data.

	Returns a dictionary with high-level patrol metrics and discrepancy breakdowns.
	"""
	if filters is None:
		filters = {}

	# Get patrol schedules
	patrol_schedules = frappe.get_all(
		"Patrol Schedule",
		fields=["name", "status", "patrol_date"],
	)

	# Get patrol verification records
	verification_records = frappe.get_all(
		"Patrol Verification Record",
		filters={"docstatus": 1},
		fields=["name", "patrol_schedule", "discrepancies_found"],
	)

	# Get discrepancy reports
	discrepancy_reports = frappe.get_all(
		"Discrepancy Report",
		filters={"docstatus": 1},
		fields=["name", "severity", "status"],
	)

	# Calculate metrics
	total_schedules = len(patrol_schedules)
	completed_schedules = sum(1 for p in patrol_schedules if p["status"] == "Completed")
	in_progress_schedules = sum(1 for p in patrol_schedules if p["status"] == "In Progress")

	total_verifications = len(verification_records)
	verifications_with_discrepancies = sum(1 for v in verification_records if v["discrepancies_found"])

	# Group discrepancies by severity
	discrepancies_by_severity = {}
	for report in discrepancy_reports:
		severity = report["severity"]
		if severity not in discrepancies_by_severity:
			discrepancies_by_severity[severity] = 0
		discrepancies_by_severity[severity] += 1

	# Group discrepancies by status
	discrepancies_by_status = {}
	for report in discrepancy_reports:
		status = report["status"]
		if status not in discrepancies_by_status:
			discrepancies_by_status[status] = 0
		discrepancies_by_status[status] += 1

	return {
		"status": "success",
		"data": {
			"total_patrol_schedules": total_schedules,
			"completed_schedules": completed_schedules,
			"in_progress_schedules": in_progress_schedules,
			"completion_rate": (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0,
			"total_verifications": total_verifications,
			"verifications_with_discrepancies": verifications_with_discrepancies,
			"discrepancy_rate": (verifications_with_discrepancies / total_verifications * 100) if total_verifications > 0 else 0,
			"total_discrepancies": len(discrepancy_reports),
			"discrepancies_by_severity": discrepancies_by_severity,
			"discrepancies_by_status": discrepancies_by_status,
		},
	}


# ============================================================================
# PATROL TIMING COMPLIANCE DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_patrol_timing_data(filters=None):
	"""Get patrol timing compliance metrics for guard monitoring dashboard.

	Optional filters (all optional):
		from_date (str | date): start date (inclusive)
		to_date (str | date): end date (inclusive)
		grace_minutes (int): minutes window treated as "On Time"
	"""
	if filters is None:
		filters = {}

	data = report_scripts.get_patrol_timing_report_data(
		from_date=filters.get("from_date"),
		to_date=filters.get("to_date"),
		grace_minutes=filters.get("grace_minutes"),
	)

	return {
		"status": "success",
		"data": data,
	}


# ============================================================================
# RESOURCE DEPLOYMENT DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_resource_deployment_data(filters=None):
	"""
	Get resource deployment metrics.
	
	Returns:
		Dictionary with deployment metrics
	"""
	if filters is None:
		filters = {}
	
	# Get resource deployments
	deployments = frappe.get_all(
		"Resource Deployment",
		filters={"docstatus": 1},
		fields=["name", "status", "deployment_date"]
	)
	
	# Get security resources
	resources = frappe.get_all(
		"Security Resource",
		fields=["name", "resource_type", "status"]
	)
	
	# Group resources by type
	resources_by_type = {}
	for resource in resources:
		res_type = resource["resource_type"]
		if res_type not in resources_by_type:
			resources_by_type[res_type] = {"total": 0, "active": 0}
		resources_by_type[res_type]["total"] += 1
		if resource["status"] == "Active":
			resources_by_type[res_type]["active"] += 1
	
	# Calculate deployment metrics
	total_deployments = len(deployments)
	active_deployments = sum(1 for d in deployments if d["status"] == "Active")
	
	return {
		"status": "success",
		"data": {
			"total_deployments": total_deployments,
			"active_deployments": active_deployments,
			"deployment_rate": (active_deployments / total_deployments * 100) if total_deployments > 0 else 0,
			"resources_by_type": resources_by_type
		}
	}


# ============================================================================
# VISITOR MANAGEMENT DATA SOURCES
# ============================================================================

@frappe.whitelist()
def get_visitor_management_data(filters=None):
	"""
	Get visitor management metrics.
	
	Returns:
		Dictionary with visitor metrics
	"""
	if filters is None:
		filters = {}
	
	# Get visitor-guard assignments
	assignments = frappe.get_all(
		"Visitor Guard Assignment",
		filters={"docstatus": 1},
		fields=["name", "status"]
	)
	
	# Get evacuation records
	evacuations = frappe.get_all(
		"Emergency Evacuation Tracking",
		filters={"docstatus": 1},
		fields=["name", "status", "total_visitors", "total_evacuated"]
	)
	
	# Calculate metrics
	total_assignments = len(assignments)
	checked_out = sum(1 for a in assignments if a["status"] == "Checked Out")
	active_assignments = sum(1 for a in assignments if a["status"] in ["Assigned", "Escorting"])
	
	total_evacuations = len(evacuations)
	completed_evacuations = sum(1 for e in evacuations if e["status"] == "Completed")
	
	total_visitors_evacuated = sum(e["total_evacuated"] for e in evacuations)
	total_visitors_in_evacuations = sum(e["total_visitors"] for e in evacuations)
	
	return {
		"status": "success",
		"data": {
			"total_assignments": total_assignments,
			"active_assignments": active_assignments,
			"checked_out": checked_out,
			"total_evacuations": total_evacuations,
			"completed_evacuations": completed_evacuations,
			"evacuation_completion_rate": (completed_evacuations / total_evacuations * 100) if total_evacuations > 0 else 0,
			"total_visitors_evacuated": total_visitors_evacuated,
			"total_visitors_in_evacuations": total_visitors_in_evacuations,
			"evacuation_success_rate": (total_visitors_evacuated / total_visitors_in_evacuations * 100) if total_visitors_in_evacuations > 0 else 0
		}
	}

