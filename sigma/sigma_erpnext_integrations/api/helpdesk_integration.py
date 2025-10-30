"""
Helpdesk Integration Module

Handles integration between Sigma Case Management and Frappe Helpdesk
"""

import frappe
from frappe import _
from frappe.utils import now
from typing import Dict, Any
from .integration_api import SigmaIntegrationAPI


class HelpdeskIntegration:
    """Manages Case ↔ Ticket synchronization"""
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_case_to_ticket(case_doc, method=None):
        """Create or update Helpdesk Ticket from Case"""
        if not SigmaIntegrationAPI.check_helpdesk_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("helpdesk"):
            return
        
        ticket_name = case_doc.get("sigma_ticket")
        
        if ticket_name and frappe.db.exists("HD Ticket", ticket_name):
            ticket = frappe.get_doc("HD Ticket", ticket_name)
            ticket.status = HelpdeskIntegration._map_case_status_to_ticket(case_doc.status)
            ticket.save(ignore_permissions=True)
        else:
            ticket = frappe.get_doc({
                "doctype": "HD Ticket",
                "subject": case_doc.get("title") or case_doc.name,
                "description": case_doc.get("description"),
                "status": "Open",
                "priority": case_doc.get("priority"),
                "sigma_case": case_doc.name,
                "sigma_case_type": case_doc.get("case_type")
            })
            ticket.insert(ignore_permissions=True)
            frappe.db.set_value("Case Record", case_doc.name, "sigma_ticket", ticket.name)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Case to Ticket",
            status="Success",
            source_doctype="Case Record",
            source_name=case_doc.name,
            target_doctype="HD Ticket",
            target_name=ticket.name
        )
        
        frappe.db.commit()
    
    @staticmethod
    def _map_case_status_to_ticket(case_status):
        """Map Case status to Ticket status"""
        mapping = {
            "Open": "Open",
            "In Progress": "Replied",
            "Resolved": "Resolved",
            "Closed": "Closed"
        }
        return mapping.get(case_status, "Open")

