"""
CRM Integration Module

Handles integration between Sigma Visitor Management and ERPNext CRM
"""

import frappe
from frappe import _
from frappe.utils import now
from typing import Dict, Any
from .integration_api import SigmaIntegrationAPI


class CRMIntegration:
    """Manages Visitor ↔ Contact/Lead synchronization"""
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_visitor_to_contact(visitor_doc, method=None):
        """Create or update Contact from Visitor"""
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("crm"):
            return
        
        # Check if Contact already exists
        contact_name = visitor_doc.get("sigma_contact")
        
        if contact_name and frappe.db.exists("Contact", contact_name):
            contact = frappe.get_doc("Contact", contact_name)
        else:
            contact = frappe.get_doc({
                "doctype": "Contact",
                "first_name": visitor_doc.get("first_name"),
                "last_name": visitor_doc.get("last_name"),
                "email_id": visitor_doc.get("email"),
                "phone": visitor_doc.get("phone"),
                "sigma_visitor": visitor_doc.name,
                "sigma_visitor_type": visitor_doc.get("visitor_type")
            })
            contact.insert(ignore_permissions=True)
            frappe.db.set_value("Visitor", visitor_doc.name, "sigma_contact", contact.name)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Visitor to Contact",
            status="Success",
            source_doctype="Visitor",
            source_name=visitor_doc.name,
            target_doctype="Contact",
            target_name=contact.name
        )
        
        frappe.db.commit()

