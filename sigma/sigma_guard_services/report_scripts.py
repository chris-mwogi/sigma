# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_months
from datetime import datetime, timedelta


# ============================================================================
# PROVIDER PERFORMANCE REPORT
# ============================================================================

def get_provider_performance_report_data():
	"""
	Generate provider performance report data.
	"""
	from frappe.query_builder import Query
	from frappe.query_builder.functions import Count, Sum, Avg
	
	# Get all active contracts
	contracts = frappe.get_all(
		"Contract",
		filters={"status": "Active"},
		fields=["name", "supplier", "location"],
		limit_page_length=None
	)
	
	report_data = []
	
	for contract in contracts:
		supplier = contract["supplier"]
		
		# Get compliance records
		compliance_records = frappe.get_all(
			"SLA Compliance Record",
			filters={"service_contract": contract["name"]},
			fields=["compliance_status", "compliance_score"],
			limit_page_length=None
		)
		
		compliance_rate = 0
		avg_score = 0
		if compliance_records:
			compliant = sum(1 for r in compliance_records if r["compliance_status"] == "Compliant")
			compliance_rate = (compliant / len(compliance_records)) * 100
			avg_score = sum(r["compliance_score"] for r in compliance_records) / len(compliance_records)
		
		# Get surcharges
		surcharges = frappe.get_all(
			"Surcharge Record",
			filters={"service_contract": contract["name"], "docstatus": 1},
			fields=["surcharge_amount"],
			limit_page_length=None
		)
		total_surcharges = sum(s["surcharge_amount"] for s in surcharges)
		
		# Get patrol completion rate
		patrol_schedules = frappe.get_all(
			"Patrol Schedule",
			filters={"location": contract["location"]},
			fields=["status"],
			limit_page_length=None
		)
		
		patrol_completion = 0
		if patrol_schedules:
			completed = sum(1 for p in patrol_schedules if p["status"] == "Completed")
			patrol_completion = (completed / len(patrol_schedules)) * 100
		
		report_data.append({
			"supplier": supplier,
			"contract": contract["name"],
			"location": contract["location"],
			"compliance_rate": round(compliance_rate, 2),
			"avg_compliance_score": round(avg_score, 2),
			"total_surcharges": total_surcharges,
			"patrol_completion_rate": round(patrol_completion, 2),
			"compliance_records": len(compliance_records),
			"surcharge_count": len(surcharges)
		})
	
	return report_data


# ============================================================================
# SLA COMPLIANCE TRENDS REPORT
# ============================================================================

def get_sla_compliance_trends_report_data():
	"""
	Generate SLA compliance trends report data.
	"""
	end_date = getdate()
	start_date = end_date - timedelta(days=30)
	
	compliance_records = frappe.get_all(
		"SLA Compliance Record",
		filters={
			"compliance_date": [">=", start_date],
			"compliance_date": ["<=", end_date]
		},
		fields=["compliance_date", "compliance_status", "compliance_score", "service_contract"],
		order_by="compliance_date asc",
		limit_page_length=None
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
				"scores": []
			}
		
		daily_data[date_str]["total"] += 1
		if record["compliance_status"] == "Compliant":
			daily_data[date_str]["compliant"] += 1
		else:
			daily_data[date_str]["non_compliant"] += 1
		daily_data[date_str]["scores"].append(record["compliance_score"])
	
	# Calculate averages
	report_data = []
	for date_str in sorted(daily_data.keys()):
		data = daily_data[date_str]
		avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
		compliance_rate = (data["compliant"] / data["total"] * 100) if data["total"] > 0 else 0
		
		report_data.append({
			"date": data["date"],
			"total_records": data["total"],
			"compliant": data["compliant"],
			"non_compliant": data["non_compliant"],
			"compliance_rate": round(compliance_rate, 2),
			"avg_compliance_score": round(avg_score, 2)
		})
	
	return report_data


# ============================================================================
# FINANCIAL IMPACT REPORT
# ============================================================================

def get_financial_impact_report_data():
	"""
	Generate financial impact report data.
	"""
	# Get surcharge records
	surcharges = frappe.get_all(
		"Surcharge Record",
		filters={"docstatus": 1},
		fields=["name", "service_contract", "surcharge_amount", "surcharge_date", "surcharge_method"],
		order_by="surcharge_date desc",
		limit_page_length=None
	)
	
	# Get debit notes
	debit_notes = frappe.get_all(
		"Debit Note",
		filters={"docstatus": 1},
		fields=["name", "supplier", "total", "posting_date"],
		order_by="posting_date desc",
		limit_page_length=None
	)
	
	# Get compliance notices
	compliance_notices = frappe.get_all(
		"Compliance Notice",
		filters={"docstatus": 1},
		fields=["name", "supplier", "surcharge_applicable"],
		limit_page_length=None
	)
	
	# Calculate summary
	total_surcharges = sum(s["surcharge_amount"] for s in surcharges)
	total_debit_notes = sum(d["total"] for d in debit_notes)
	
	# Group surcharges by method
	surcharge_by_method = {}
	for surcharge in surcharges:
		method = surcharge["surcharge_method"]
		if method not in surcharge_by_method:
			surcharge_by_method[method] = {"count": 0, "amount": 0}
		surcharge_by_method[method]["count"] += 1
		surcharge_by_method[method]["amount"] += surcharge["surcharge_amount"]
	
	# Group by supplier
	surcharge_by_supplier = {}
	for surcharge in surcharges:
		contract = frappe.get_doc("Contract", surcharge["service_contract"])
		supplier = contract.supplier
		if supplier not in surcharge_by_supplier:
			surcharge_by_supplier[supplier] = 0
		surcharge_by_supplier[supplier] += surcharge["surcharge_amount"]
	
	report_data = {
		"summary": {
			"total_surcharges": total_surcharges,
			"total_debit_notes": total_debit_notes,
			"total_financial_impact": total_surcharges + total_debit_notes,
			"total_compliance_notices": len(compliance_notices),
			"notices_with_surcharge": sum(1 for n in compliance_notices if n["surcharge_applicable"]),
			"avg_surcharge": total_surcharges / len(surcharges) if surcharges else 0
		},
		"surcharge_by_method": surcharge_by_method,
		"surcharge_by_supplier": surcharge_by_supplier,
		"recent_surcharges": surcharges[:10],
		"recent_debit_notes": debit_notes[:10]
	}
	
	return report_data


# ============================================================================
# PATROL SUMMARY REPORT
# ============================================================================

def get_patrol_summary_report_data():
	"""Generate patrol summary report data for patrols and discrepancies."""

	# Get patrol schedules
	patrol_schedules = frappe.get_all(
		"Patrol Schedule",
		fields=["name", "status", "patrol_date", "location"],
		order_by="patrol_date desc",
		limit_page_length=None,
	)

	# Get patrol verification records
	verification_records = frappe.get_all(
		"Patrol Verification Record",
		filters={"docstatus": 1},
		fields=["name", "patrol_schedule", "discrepancies_found", "verification_time"],
		order_by="verification_time desc",
		limit_page_length=None,
	)

	# Get discrepancy reports
	discrepancy_reports = frappe.get_all(
		"Discrepancy Report",
		filters={"docstatus": 1},
		fields=["name", "severity", "status", "patrol_verification"],
		limit_page_length=None,
	)

	# Calculate metrics
	total_schedules = len(patrol_schedules)
	completed_schedules = sum(1 for p in patrol_schedules if p["status"] == "Completed")
	in_progress_schedules = sum(1 for p in patrol_schedules if p["status"] == "In Progress")
	scheduled_schedules = sum(1 for p in patrol_schedules if p["status"] == "Scheduled")

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

	report_data = {
		"summary": {
			"total_patrol_schedules": total_schedules,
			"completed_schedules": completed_schedules,
			"in_progress_schedules": in_progress_schedules,
			"scheduled_schedules": scheduled_schedules,
			"completion_rate": round((
				completed_schedules / total_schedules * 100
			) if total_schedules > 0 else 0, 2),
			"total_verifications": total_verifications,
			"verifications_with_discrepancies": verifications_with_discrepancies,
			"discrepancy_rate": round((
				verifications_with_discrepancies / total_verifications * 100
			) if total_verifications > 0 else 0, 2),
			"total_discrepancies": len(discrepancy_reports),
		},
		"discrepancies_by_severity": discrepancies_by_severity,
		"discrepancies_by_status": discrepancies_by_status,
		"recent_schedules": patrol_schedules[:10],
		"recent_verifications": verification_records[:10],
	}

	return report_data


	# =========================================================================
	# PATROL TIMING COMPLIANCE REPORT
	# =========================================================================


def get_patrol_timing_report_data(from_date=None, to_date=None, grace_minutes=5):
	"""Generate patrol timing compliance data.

	Compares scheduled checkpoint times from Patrol Schedule Item against
	actual verification times from Patrol Verification Record and classifies
	each checkpoint as Early, On Time, Late, or Skipped.

	Args:
		from_date (str | date | None): Start date (inclusive). Defaults to 7 days ago.
		to_date (str | date | None): End date (inclusive). Defaults to today.
		grace_minutes (int): Minutes window around scheduled time considered "On Time".

	Returns:
		Dict with summary counts/percentages and per-route breakdown.
	"""

	# Resolve date range
	if to_date:
		to_date = getdate(to_date)
	else:
		to_date = getdate()

	if from_date:
		from_date = getdate(from_date)
	else:
		from_date = to_date - timedelta(days=7)

	try:
		grace_minutes = int(grace_minutes or 0)
	except Exception:
		grace_minutes = 0

	# Base dataset: one row per scheduled checkpoint
	rows = frappe.db.sql(
		"""
		SELECT
			psi.parent AS patrol_schedule,
			psi.checkpoint,
			psi.sequence,
			ps.location,
			ps.patrol_officer,
			ps.patrol_date,
			psi.scheduled_time,
			MIN(pvr.verification_time) AS first_verification_time
		FROM `tabPatrol Schedule` ps
		JOIN `tabPatrol Schedule Item` psi
			ON psi.parent = ps.name
		LEFT JOIN `tabPatrol Verification Record` pvr
			ON pvr.patrol_schedule = ps.name
			AND pvr.checkpoint = psi.checkpoint
			AND pvr.patrol_date = ps.patrol_date
		WHERE ps.patrol_date BETWEEN %s AND %s
		GROUP BY
			psi.parent,
			psi.checkpoint,
			psi.sequence,
			ps.location,
			ps.patrol_officer,
			ps.patrol_date,
			psi.scheduled_time
		ORDER BY
			ps.patrol_date,
			psi.parent,
			psi.sequence
		""",
		[from_date, to_date],
		as_dict=True,
	)

	status_counts = {"On Time": 0, "Early": 0, "Late": 0, "Skipped": 0}
	route_stats = {}
	details = []

	def _parse_time(value):
		if not value:
			return None
		if isinstance(value, datetime):
			return value
		# Frappe may give strings for Time/Datetime fields
		try:
			# Try full datetime first
			return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
		except Exception:
			# Fallback to just time (we'll combine with date separately)
			return datetime.strptime(str(value), "%H:%M:%S")

	for row in rows:
		patrol_date = row.patrol_date
		scheduled_time = row.scheduled_time
		first_verification = row.first_verification_time

		# Build scheduled datetime if possible
		scheduled_dt = None
		if scheduled_time:
			try:
				# scheduled_time is usually a time string; combine with patrol_date
				if isinstance(scheduled_time, datetime):
					scheduled_dt = scheduled_time
				else:
					st = datetime.strptime(str(scheduled_time), "%H:%M:%S").time()
					scheduled_dt = datetime.combine(patrol_date, st)
			except Exception:
				scheduled_dt = None

		verification_dt = _parse_time(first_verification) if first_verification else None

		# Classification
		if not verification_dt:
			classification = "Skipped"
		elif not scheduled_dt:
			# No scheduled time defined, treat as on time for scoring purposes
			classification = "On Time"
		else:
			delta_minutes = (verification_dt - scheduled_dt).total_seconds() / 60.0
			if abs(delta_minutes) <= grace_minutes:
				classification = "On Time"
			elif delta_minutes < -grace_minutes:
				classification = "Early"
			else:
				classification = "Late"

		status_counts[classification] += 1

		# Per-route aggregation
		route_key = row.patrol_schedule
		if route_key not in route_stats:
			route_stats[route_key] = {
				"patrol_schedule": row.patrol_schedule,
				"location": row.location,
				"patrol_officer": row.patrol_officer,
				"total": 0,
				"on_time": 0,
				"early": 0,
				"late": 0,
				"skipped": 0,
			}

		route_stats[route_key]["total"] += 1
		if classification == "On Time":
			route_stats[route_key]["on_time"] += 1
		elif classification == "Early":
			route_stats[route_key]["early"] += 1
		elif classification == "Late":
			route_stats[route_key]["late"] += 1
		elif classification == "Skipped":
			route_stats[route_key]["skipped"] += 1

		details.append(
			{
				"patrol_schedule": row.patrol_schedule,
				"checkpoint": row.checkpoint,
				"sequence": row.sequence,
				"location": row.location,
				"patrol_officer": row.patrol_officer,
				"patrol_date": row.patrol_date,
				"scheduled_time": row.scheduled_time,
				"first_verification_time": row.first_verification_time,
				"classification": classification,
			}
		)

	def _pct(part, whole):
		return round((part / whole * 100.0), 1) if whole else 0

	_total = sum(status_counts.values())
	summary = {
		"total_checkpoints": _total,
		"on_time": status_counts["On Time"],
		"early": status_counts["Early"],
		"late": status_counts["Late"],
		"skipped": status_counts["Skipped"],
		"on_time_pct": _pct(status_counts["On Time"], _total),
		"early_pct": _pct(status_counts["Early"], _total),
		"late_pct": _pct(status_counts["Late"], _total),
		"skipped_pct": _pct(status_counts["Skipped"], _total),
	}

	# Convert route_stats dict to sorted list (most issues first)
	by_route = sorted(
		route_stats.values(),
		key=lambda r: (r["late"] + r["skipped"]),
		reverse=True,
	)

	return {
		"parameters": {
			"from_date": str(from_date),
			"to_date": str(to_date),
			"grace_minutes": grace_minutes,
		},
		"summary": summary,
		"by_route": by_route,
		"details": details,
	}


# ============================================================================
# RESOURCE DEPLOYMENT REPORT
# ============================================================================

def get_resource_deployment_report_data():
	"""
	Generate resource deployment report data.
	"""
	# Get resource deployments
	deployments = frappe.get_all(
		"Resource Deployment",
		filters={"docstatus": 1},
		fields=["name", "status", "deployment_date", "location"],
		order_by="deployment_date desc",
		limit_page_length=None
	)
	
	# Get security resources
	resources = frappe.get_all(
		"Security Resource",
		fields=["name", "resource_type", "status"],
		limit_page_length=None
	)
	
	# Group resources by type
	resources_by_type = {}
	for resource in resources:
		res_type = resource["resource_type"]
		if res_type not in resources_by_type:
			resources_by_type[res_type] = {"total": 0, "active": 0, "inactive": 0}
		resources_by_type[res_type]["total"] += 1
		if resource["status"] == "Active":
			resources_by_type[res_type]["active"] += 1
		else:
			resources_by_type[res_type]["inactive"] += 1
	
	# Calculate deployment metrics
	total_deployments = len(deployments)
	active_deployments = sum(1 for d in deployments if d["status"] == "Active")
	
	report_data = {
		"summary": {
			"total_deployments": total_deployments,
			"active_deployments": active_deployments,
			"deployment_rate": round((active_deployments / total_deployments * 100) if total_deployments > 0 else 0, 2),
			"total_resources": len(resources)
		},
		"resources_by_type": resources_by_type,
		"recent_deployments": deployments[:10]
	}
	
	return report_data


# ============================================================================
# VISITOR MANAGEMENT REPORT
# ============================================================================

def get_visitor_management_report_data():
	"""
	Generate visitor management report data.
	"""
	# Get visitor-guard assignments
	assignments = frappe.get_all(
		"Visitor Guard Assignment",
		filters={"docstatus": 1},
		fields=["name", "status", "assignment_time"],
		order_by="assignment_time desc",
		limit_page_length=None
	)
	
	# Get evacuation records
	evacuations = frappe.get_all(
		"Emergency Evacuation Tracking",
		filters={"docstatus": 1},
		fields=["name", "status", "total_visitors", "total_evacuated", "evacuation_date"],
		order_by="evacuation_date desc",
		limit_page_length=None
	)
	
	# Calculate metrics
	total_assignments = len(assignments)
	checked_out = sum(1 for a in assignments if a["status"] == "Checked Out")
	active_assignments = sum(1 for a in assignments if a["status"] in ["Assigned", "Escorting"])
	
	total_evacuations = len(evacuations)
	completed_evacuations = sum(1 for e in evacuations if e["status"] == "Completed")
	
	total_visitors_evacuated = sum(e["total_evacuated"] for e in evacuations)
	total_visitors_in_evacuations = sum(e["total_visitors"] for e in evacuations)
	
	report_data = {
		"summary": {
			"total_assignments": total_assignments,
			"active_assignments": active_assignments,
			"checked_out": checked_out,
			"total_evacuations": total_evacuations,
			"completed_evacuations": completed_evacuations,
			"evacuation_completion_rate": round((completed_evacuations / total_evacuations * 100) if total_evacuations > 0 else 0, 2),
			"total_visitors_evacuated": total_visitors_evacuated,
			"total_visitors_in_evacuations": total_visitors_in_evacuations,
			"evacuation_success_rate": round((total_visitors_evacuated / total_visitors_in_evacuations * 100) if total_visitors_in_evacuations > 0 else 0, 2)
		},
		"recent_assignments": assignments[:10],
		"recent_evacuations": evacuations[:10]
	}
	
	return report_data

