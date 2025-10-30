"""
Sigma Automation Hooks
Handles automated workflows and business logic
"""

import frappe
from frappe import _

def auto_create_case_from_call_log(doc, method):
    """Auto-create Case Record from high-severity Call Log"""
    if doc.severity in ["High", "Critical"]:
        case = frappe.new_doc("Case Record")
        case.case_number = f"CASE-{doc.name}"
        case.title = f"Case from Call: {doc.caller_name}"
        case.description = doc.description
        case.severity = doc.severity
        case.status = "Open"
        case.assigned_to = frappe.session.user
        case.insert(ignore_permissions=True)
        frappe.db.commit()

        # Link back to call log
        doc.db_set("linked_case", case.name)
        frappe.msgprint(f"Case {case.name} created automatically")


def auto_create_helpdesk_ticket_from_call_log(doc, method):
    """Auto-create Helpdesk Ticket from high-severity Call Log (requires Helpdesk)."""
    try:
        if doc.severity in ["High", "Critical"] and not getattr(doc, "helpdesk_ticket", None):
            if frappe.db.exists("DocType", "HD Ticket"):
                res = frappe.get_attr("sigma.api.api.create_helpdesk_ticket_from_call_log")(doc.name)
                if isinstance(res, dict) and res.get("ticket"):
                    # Link back if field exists
                    if frappe.db.has_column("Call Log", "helpdesk_ticket"):
                        doc.db_set("helpdesk_ticket", res["ticket"])
                    frappe.msgprint(_(f"Helpdesk Ticket {res['ticket']} created automatically"))
    except Exception as e:
        frappe.log_error(f"auto_create_helpdesk_ticket_from_call_log failed: {e}", "Sigma Automation")


def auto_escalate_overdue_cases(doc, method):
    """Auto-escalate cases that are overdue"""
    if doc.sla_due_date and frappe.utils.getdate(doc.sla_due_date) < frappe.utils.getdate():
        if doc.status not in ["Resolved", "Closed"]:
            doc.db_set("status", "Pending Review")
            frappe.msgprint("Case escalated due to SLA breach")

def auto_create_mitigation_from_risk(doc, method):
    """Auto-create Mitigation Action from Risk Assessment"""
    if doc.status == "Assessed":
        mitigation = frappe.new_doc("Mitigation Action")
        mitigation.risk_id = doc.name
        mitigation.action_description = f"Mitigate risk: {doc.title}"
        mitigation.status = "Open"
        mitigation.priority = "High" if doc.risk_score >= 15 else "Medium"
        mitigation.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(f"Mitigation action created for risk {doc.name}")

def auto_notify_access_violation(doc, method):
    """Auto-notify on access policy violation"""
    if doc.result == "Denied":
        # Create notification
        notification_msg = f"""
        Access Denied Event
        Door: {doc.door}
        User: {doc.user_id}
        Time: {getattr(doc, 'timestamp', None) or getattr(doc, 'event_time', '')}
        """

        # Log to system
        frappe.logger().warning(notification_msg)

        # Create case if critical
        if doc.severity == "Critical":
            case = frappe.new_doc("Case Record")
            case.case_number = f"ACCESS-{doc.name}"
            case.title = f"Access Violation: {doc.door}"
            case.description = notification_msg
            case.severity = "High"
            case.status = "Open"
            case.insert(ignore_permissions=True)
            frappe.db.commit()

def auto_check_in_guard_shift(doc, method):
    """Auto-update guard shift status on check-in"""
    if doc.status == "Checked In":
        # Create guard activity log
        activity = frappe.new_doc("Guard Activity")
        activity.guard_id = doc.guard_id
        activity.activity_type = "Check In"
        activity.timestamp = frappe.utils.now()
        activity.location = doc.location
        activity.insert(ignore_permissions=True)
        frappe.db.commit()

def auto_calculate_risk_score(doc, method):
    """Auto-calculate risk score from likelihood and impact"""
    if hasattr(doc, 'likelihood_score') and hasattr(doc, 'impact_score'):
        if doc.likelihood_score and doc.impact_score:
            doc.risk_score = doc.likelihood_score * doc.impact_score
            frappe.msgprint(f"Risk score calculated: {doc.risk_score}")

# Register hooks
def setup_automation_hooks():
    """Register all automation hooks"""
    frappe.db.add_hook("Call Log", "on_update", auto_create_case_from_call_log)
    frappe.db.add_hook("Case Record", "on_update", auto_escalate_overdue_cases)
    frappe.db.add_hook("Risk Assessment", "on_update", auto_create_mitigation_from_risk)
    frappe.db.add_hook("Access Event", "on_insert", auto_notify_access_violation)
    frappe.db.add_hook("Guard Shift", "on_update", auto_check_in_guard_shift)
    frappe.db.add_hook("Risk Heatmap", "on_update", auto_calculate_risk_score)

