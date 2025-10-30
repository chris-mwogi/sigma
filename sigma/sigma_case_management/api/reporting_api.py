"""
Reporting API - Case analytics and reporting
"""
import frappe
from frappe.utils import now, today
from datetime import datetime, timedelta


@frappe.whitelist()
def get_investigator_workload(investigator=None):
    """
    Get investigator workload
    
    Args:
        investigator: Investigator user (optional, defaults to current user)
    
    Returns:
        Workload information
    """
    try:
        if not investigator:
            investigator = frappe.session.user
        
        # Get active cases
        active_cases = frappe.db.count(
            "Case Assignment",
            filters={
                "investigator": investigator,
                "status": "Active"
            }
        )
        
        # Get completed cases this month
        month_start = datetime.now().replace(day=1)
        completed_cases = frappe.db.count(
            "Case Assignment",
            filters={
                "investigator": investigator,
                "status": "Completed",
                "modified": [">", month_start.isoformat()]
            }
        )
        
        return {
            "investigator": investigator,
            "active_cases": active_cases,
            "completed_this_month": completed_cases,
            "workload_percentage": (active_cases / 20) * 100  # Max 20 cases
        }
    except Exception as e:
        frappe.log_error(f"Failed to get investigator workload: {str(e)}")
        frappe.throw(f"Failed to get investigator workload: {str(e)}")


@frappe.whitelist()
def get_case_timeline(case_name):
    """
    Get case timeline with all activities
    
    Args:
        case_name: Case name
    
    Returns:
        Timeline of activities
    """
    try:
        activities = frappe.db.get_list(
            "Case Activity Log",
            filters={"case": case_name},
            fields=["name", "activity_type", "activity_date", "performed_by", 
                   "activity_description", "old_value", "new_value"],
            order_by="activity_date asc"
        )
        
        return {
            "case": case_name,
            "total_activities": len(activities),
            "timeline": activities
        }
    except Exception as e:
        frappe.log_error(f"Failed to get case timeline: {str(e)}")
        frappe.throw(f"Failed to get case timeline: {str(e)}")


@frappe.whitelist()
def get_cases_by_status(status=None):
    """
    Get cases grouped by status
    
    Args:
        status: Filter by specific status (optional)
    
    Returns:
        Cases by status
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        
        cases = frappe.db.get_list(
            "Case",
            filters=filters,
            fields=["name", "case_type", "status", "severity", "incident_date", 
                   "lead_investigator", "sla_deadline"],
            order_by="incident_date desc"
        )
        
        # Group by status
        by_status = {}
        for case in cases:
            s = case.get("status")
            if s not in by_status:
                by_status[s] = []
            by_status[s].append(case)
        
        return by_status
    except Exception as e:
        frappe.log_error(f"Failed to get cases by status: {str(e)}")
        frappe.throw(f"Failed to get cases by status: {str(e)}")


@frappe.whitelist()
def get_sla_metrics():
    """
    Get SLA compliance metrics
    
    Returns:
        SLA metrics
    """
    try:
        # Get all closed cases
        closed_cases = frappe.db.get_list(
            "Case",
            filters={"status": "Closed"},
            fields=["name", "sla_deadline", "resolution_date"]
        )
        
        on_time = 0
        overdue = 0
        
        for case in closed_cases:
            if case.get("resolution_date") and case.get("sla_deadline"):
                if case["resolution_date"] <= case["sla_deadline"]:
                    on_time += 1
                else:
                    overdue += 1
        
        total = on_time + overdue
        compliance_rate = (on_time / total * 100) if total > 0 else 0
        
        return {
            "total_closed_cases": total,
            "on_time": on_time,
            "overdue": overdue,
            "compliance_rate": compliance_rate
        }
    except Exception as e:
        frappe.log_error(f"Failed to get SLA metrics: {str(e)}")
        frappe.throw(f"Failed to get SLA metrics: {str(e)}")


@frappe.whitelist()
def get_asset_theft_report():
    """
    Get asset theft report
    
    Returns:
        Asset theft statistics
    """
    try:
        theft_cases = frappe.db.get_list(
            "Asset Theft",
            fields=["name", "asset_type", "recovery_status", "asset_value", "currency"]
        )
        
        total_value = 0
        recovered_value = 0
        
        for theft in theft_cases:
            total_value += theft.get("asset_value", 0)
            if theft.get("recovery_status") == "Fully Recovered":
                recovered_value += theft.get("asset_value", 0)
        
        return {
            "total_thefts": len(theft_cases),
            "total_value": total_value,
            "recovered_value": recovered_value,
            "recovery_rate": (recovered_value / total_value * 100) if total_value > 0 else 0
        }
    except Exception as e:
        frappe.log_error(f"Failed to get asset theft report: {str(e)}")
        frappe.throw(f"Failed to get asset theft report: {str(e)}")


@frappe.whitelist()
def export_case_for_legal(case_name):
    """
    Export case data for legal proceedings
    
    Args:
        case_name: Case name
    
    Returns:
        Case data for legal export
    """
    try:
        case = frappe.get_doc("Case", case_name)
        
        # Get all evidence
        evidence = frappe.db.get_list(
            "Case Evidence",
            filters={"case": case_name},
            fields=["name", "evidence_type", "evidence_category", "file_hash", "integrity_verified"]
        )
        
        # Get all communications
        communications = frappe.db.get_list(
            "Case External Communication",
            filters={"case": case_name},
            fields=["name", "stakeholder_type", "subject", "communication_date"]
        )
        
        # Get timeline
        timeline = frappe.db.get_list(
            "Case Activity Log",
            filters={"case": case_name},
            fields=["activity_type", "activity_date", "performed_by", "activity_description"],
            order_by="activity_date asc"
        )
        
        return {
            "case_id": case.name,
            "case_type": case.case_type,
            "status": case.status,
            "severity": case.severity,
            "incident_date": case.incident_date,
            "reported_by": case.reported_by,
            "incident_details": case.incident_details,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "communications": communications,
            "timeline": timeline
        }
    except Exception as e:
        frappe.log_error(f"Failed to export case for legal: {str(e)}")
        frappe.throw(f"Failed to export case for legal: {str(e)}")

