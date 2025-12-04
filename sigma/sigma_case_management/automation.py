# -*- coding: utf-8 -*-
# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

"""
Case Management Automation Module
Handles automated tasks for case management including:
- Evidence file hash generation
- SLA monitoring and notifications
- Auto-escalation for overdue cases
- Risk score recalculation
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, date_diff, add_to_date
import hashlib


def generate_file_hash(file_path, algorithm="SHA256"):
    """
    Generate cryptographic hash for evidence files
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (SHA256, SHA512, MD5)
    
    Returns:
        str: Hexadecimal hash string
    """
    try:
        if algorithm == "SHA256":
            hasher = hashlib.sha256()
        elif algorithm == "SHA512":
            hasher = hashlib.sha512()
        elif algorithm == "MD5":
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    except Exception as e:
        frappe.log_error(f"Error generating file hash: {str(e)}", "Case Management Automation")
        return None


def check_sla_breaches():
    """
    Check for SLA breaches and send notifications
    Called via scheduled job (hourly)
    """
    now = now_datetime()
    
    # Get cases approaching SLA deadline (within reminder window)
    settings = frappe.get_single("Case Settings")
    reminder_hours = settings.sla_reminder_hours_before or 24
    
    reminder_threshold = add_to_date(now, hours=reminder_hours)
    
    # Find cases approaching SLA
    approaching_cases = frappe.get_all(
        "Case",
        filters={
            "status": ["in", ["Open", "Under Investigation", "Waiting for Information"]],
            "sla_due_date": ["between", [now, reminder_threshold]],
            "docstatus": 1
        },
        fields=["name", "case_title", "assigned_to", "sla_due_date", "severity"]
    )
    
    for case in approaching_cases:
        send_sla_reminder(case)
    
    # Find cases that have breached SLA
    breached_cases = frappe.get_all(
        "Case",
        filters={
            "status": ["in", ["Open", "Under Investigation", "Waiting for Information"]],
            "sla_due_date": ["<", now],
            "docstatus": 1
        },
        fields=["name", "case_title", "assigned_to", "sla_due_date", "severity"]
    )
    
    for case in breached_cases:
        send_sla_breach_notification(case)
        
        # Auto-escalate if enabled
        if settings.auto_escalation_enabled:
            escalate_case(case)


def send_sla_reminder(case):
    """Send SLA reminder notification"""
    if not case.get("assigned_to"):
        return
    
    hours_remaining = date_diff(get_datetime(case.sla_due_date), now_datetime()) * 24
    
    frappe.sendmail(
        recipients=[case.assigned_to],
        subject=f"SLA Reminder: Case {case.name} - {case.case_title}",
        message=f"""
        <p>This is a reminder that Case <strong>{case.name}</strong> is approaching its SLA deadline.</p>
        <p><strong>Case Title:</strong> {case.case_title}</p>
        <p><strong>Severity:</strong> {case.severity}</p>
        <p><strong>SLA Due Date:</strong> {case.sla_due_date}</p>
        <p><strong>Hours Remaining:</strong> {hours_remaining:.1f}</p>
        <p>Please take necessary action to resolve this case before the deadline.</p>
        """,
        reference_doctype="Case",
        reference_name=case.name
    )


def send_sla_breach_notification(case):
    """Send SLA breach notification"""
    if not case.get("assigned_to"):
        return
    
    hours_overdue = date_diff(now_datetime(), get_datetime(case.sla_due_date)) * 24
    
    frappe.sendmail(
        recipients=[case.assigned_to],
        subject=f"SLA BREACH: Case {case.name} - {case.case_title}",
        message=f"""
        <p><strong style="color: red;">SLA BREACH ALERT</strong></p>
        <p>Case <strong>{case.name}</strong> has breached its SLA deadline.</p>
        <p><strong>Case Title:</strong> {case.case_title}</p>
        <p><strong>Severity:</strong> {case.severity}</p>
        <p><strong>SLA Due Date:</strong> {case.sla_due_date}</p>
        <p><strong>Hours Overdue:</strong> {hours_overdue:.1f}</p>
        <p>Immediate action is required to resolve this case.</p>
        """,
        reference_doctype="Case",
        reference_name=case.name
    )


def escalate_case(case):
    """Auto-escalate overdue case"""
    # Add comment to case
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": "Case",
        "reference_name": case.name,
        "content": f"Case auto-escalated due to SLA breach. Original SLA: {case.sla_due_date}"
    }).insert(ignore_permissions=True)
    
    frappe.log_error(
        f"Case {case.name} auto-escalated due to SLA breach",
        "Case Management Auto-Escalation"
    )

