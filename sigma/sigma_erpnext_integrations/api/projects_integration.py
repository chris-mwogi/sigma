"""
Projects Integration Module

Handles integration between Sigma Operations and ERPNext Projects
"""

import frappe
from frappe import _
from frappe.utils import now
from typing import Dict, Any
from .integration_api import SigmaIntegrationAPI


class ProjectsIntegration:
    """Manages Case/Patrol ↔ Project/Task synchronization"""
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_case_to_project(case_doc, method=None):
        """Create Project from Case"""
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("projects"):
            return
        
        # Only create project for major cases
        if case_doc.get("priority") not in ["High", "Critical"]:
            return
        
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": f"Case: {case_doc.name}",
            "status": "Open",
            "company": frappe.defaults.get_user_default("Company"),
            "expected_start_date": now(),
            "sigma_case": case_doc.name,
            "sigma_case_type": case_doc.get("case_type")
        })
        
        project.insert(ignore_permissions=True)
        frappe.db.set_value("Case Record", case_doc.name, "sigma_project", project.name)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Case to Project",
            status="Success",
            source_doctype="Case Record",
            source_name=case_doc.name,
            target_doctype="Project",
            target_name=project.name
        )
        
        frappe.db.commit()

