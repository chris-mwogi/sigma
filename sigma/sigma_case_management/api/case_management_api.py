"""
Case Management API - Core case management endpoints
"""
import frappe
from frappe.utils import now, today
from frappe import _
from datetime import datetime, timedelta


@frappe.whitelist()
def create_case(case_type, severity, incident_date, reported_by, incident_details, 
                location=None, related_asset=None, related_employee=None):
    """
    Create a new case
    
    Args:
        case_type: Type of case (Asset Theft, Indiscipline, Staff Complaint, etc.)
        severity: Severity level (Critical, High, Medium, Low)
        incident_date: Date of incident
        reported_by: User reporting the case
        incident_details: Details of the incident
        location: Location of incident
        related_asset: Related asset (optional)
        related_employee: Related employee (optional)
    
    Returns:
        Case document
    """
    try:
        case = frappe.new_doc("Case")
        case.case_type = case_type
        case.severity = severity
        case.incident_date = incident_date
        case.reported_by = reported_by
        case.incident_details = incident_details
        case.status = "Reported"
        case.reported_date = today()
        
        if location:
            case.location = location
        if related_asset:
            case.related_asset = related_asset
        if related_employee:
            case.related_employee = related_employee
        
        # Calculate SLA deadline based on severity
        case.sla_deadline = _calculate_sla_deadline(severity)
        
        case.save()
        frappe.db.commit()
        
        # Log activity
        _log_activity(case.name, "Case Created", f"Case created by {reported_by}")
        
        return case
    except Exception as e:
        frappe.log_error(f"Failed to create case: {str(e)}")
        frappe.throw(f"Failed to create case: {str(e)}")


@frappe.whitelist()
def assign_case(case_name, investigator, role="Lead Investigator"):
    """
    Assign case to investigator
    
    Args:
        case_name: Case name
        investigator: Investigator user
        role: Role (Lead Investigator, Supporting Investigator)
    
    Returns:
        Case Assignment document
    """
    try:
        case = frappe.get_doc("Case", case_name)
        
        # Check investigator workload
        workload = _get_investigator_workload(investigator)
        if workload >= 20:  # Max 20 cases per investigator
            frappe.throw(f"Investigator {investigator} has reached maximum workload")
        
        # Create assignment
        assignment = frappe.new_doc("Case Assignment")
        assignment.case = case_name
        assignment.investigator = investigator
        assignment.role = role
        assignment.assignment_date = today()
        assignment.assigned_by = frappe.session.user
        assignment.status = "Active"
        assignment.save()
        
        # Update case
        case.lead_investigator = investigator
        case.status = "Assigned"
        case.save()
        
        # Log activity
        _log_activity(case_name, "Assignment", f"Case assigned to {investigator} as {role}")
        
        return assignment
    except Exception as e:
        frappe.log_error(f"Failed to assign case: {str(e)}")
        frappe.throw(f"Failed to assign case: {str(e)}")


@frappe.whitelist()
def update_case_status(case_name, new_status):
    """
    Update case status with workflow validation
    
    Args:
        case_name: Case name
        new_status: New status
    
    Returns:
        Updated case document
    """
    try:
        case = frappe.get_doc("Case", case_name)
        old_status = case.status
        
        # Validate status transition
        valid_transitions = {
            "Reported": ["Under Review"],
            "Under Review": ["Assigned", "Reported"],
            "Assigned": ["Investigation"],
            "Investigation": ["Evidence Collection", "Assigned"],
            "Evidence Collection": ["Resolution Pending", "Investigation"],
            "Resolution Pending": ["Closed"],
            "Closed": ["Archived", "Reopened"],
            "Archived": []
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            frappe.throw(f"Invalid status transition from {old_status} to {new_status}")
        
        case.status = new_status
        case.save()
        
        # Log activity
        _log_activity(case_name, "Status Changed", f"Status changed from {old_status} to {new_status}")
        
        return case
    except Exception as e:
        frappe.log_error(f"Failed to update case status: {str(e)}")
        frappe.throw(f"Failed to update case status: {str(e)}")


@frappe.whitelist()
def escalate_case(case_name, reason):
    """
    Escalate case to higher priority
    
    Args:
        case_name: Case name
        reason: Escalation reason
    
    Returns:
        Updated case document
    """
    try:
        case = frappe.get_doc("Case", case_name)
        
        # Escalate severity
        severity_levels = ["Low", "Medium", "High", "Critical"]
        current_index = severity_levels.index(case.severity)
        if current_index < len(severity_levels) - 1:
            case.severity = severity_levels[current_index + 1]
        
        case.save()
        
        # Log activity
        _log_activity(case_name, "Escalation", f"Case escalated: {reason}")
        
        # Notify lead investigator
        if case.lead_investigator:
            frappe.share.add("Case", case_name, user=case.lead_investigator, notify=1)
        
        return case
    except Exception as e:
        frappe.log_error(f"Failed to escalate case: {str(e)}")
        frappe.throw(f"Failed to escalate case: {str(e)}")


@frappe.whitelist()
def close_case(case_name, resolution_notes):
    """
    Close case with resolution
    
    Args:
        case_name: Case name
        resolution_notes: Resolution notes
    
    Returns:
        Closed case document
    """
    try:
        case = frappe.get_doc("Case", case_name)
        case.status = "Closed"
        case.resolution_date = now()
        case.resolution_notes = resolution_notes
        case.save()
        
        # Log activity
        _log_activity(case_name, "Closure", f"Case closed: {resolution_notes}")
        
        return case
    except Exception as e:
        frappe.log_error(f"Failed to close case: {str(e)}")
        frappe.throw(f"Failed to close case: {str(e)}")


@frappe.whitelist()
def reopen_case(case_name, reason):
    """
    Reopen closed case
    
    Args:
        case_name: Case name
        reason: Reason for reopening
    
    Returns:
        Reopened case document
    """
    try:
        case = frappe.get_doc("Case", case_name)
        if case.status != "Closed":
            frappe.throw("Only closed cases can be reopened")
        
        case.status = "Investigation"
        case.save()
        
        # Log activity
        _log_activity(case_name, "Reopening", f"Case reopened: {reason}")
        
        return case
    except Exception as e:
        frappe.log_error(f"Failed to reopen case: {str(e)}")
        frappe.throw(f"Failed to reopen case: {str(e)}")


def _calculate_sla_deadline(severity):
    """Calculate SLA deadline based on severity"""
    sla_hours = {
        "Critical": 4,
        "High": 24,
        "Medium": 72,
        "Low": 168  # 1 week
    }
    hours = sla_hours.get(severity, 168)
    return datetime.now() + timedelta(hours=hours)


def _get_investigator_workload(investigator):
    """Get current workload for investigator"""
    active_cases = frappe.db.count(
        "Case Assignment",
        filters={
            "investigator": investigator,
            "status": "Active"
        }
    )
    return active_cases


def _log_activity(case_name, activity_type, description):
    """Log activity for case"""
    try:
        activity = frappe.new_doc("Case Activity Log")
        activity.case = case_name
        activity.activity_type = activity_type
        activity.activity_description = description
        activity.performed_by = frappe.session.user
        activity.activity_date = now()
        activity.save()
    except Exception as e:
        frappe.log_error(f"Failed to log activity: {str(e)}")

