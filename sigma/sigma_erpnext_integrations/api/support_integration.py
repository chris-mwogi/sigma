"""
Support/Maintenance Integration Module

Handles integration between Sigma Asset Management and ERPNext Support/Maintenance modules

Key Features:
- Asset Maintenance Schedule synchronization
- Maintenance Visit tracking
- Asset downtime recording
- Maintenance cost tracking
- Warranty management
- SLA tracking
"""

import frappe
from frappe import _
from frappe.utils import now, add_days, get_datetime, date_diff, flt, today
from typing import Dict, Any, Optional, List
from .integration_api import SigmaIntegrationAPI, IntegrationError


class SupportIntegration:
    """
    Manages Asset ↔ Maintenance Schedule/Visit synchronization
    
    Integration Points:
    1. Asset → Maintenance Schedule (preventive maintenance)
    2. Asset Issues → Maintenance Visit (corrective maintenance)
    3. Maintenance Visit → Asset Status updates
    4. Warranty tracking
    5. SLA management
    """
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def sync_asset_maintenance(asset_doc, method=None):
        """
        Create or update Maintenance Schedule for Asset
        
        Args:
            asset_doc: Asset document
            method: Hook method (on_insert, on_update, etc.)
        """
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("support"):
            return
        
        # Check if asset requires maintenance
        if not asset_doc.get("requires_maintenance"):
            return
        
        # Check if Maintenance Schedule already exists
        schedule_name = asset_doc.get("sigma_maintenance_schedule")
        
        if schedule_name and frappe.db.exists("Maintenance Schedule", schedule_name):
            # Update existing schedule
            schedule = frappe.get_doc("Maintenance Schedule", schedule_name)
            SupportIntegration._update_maintenance_schedule(schedule, asset_doc)
            schedule.save(ignore_permissions=True)
        else:
            # Create new Maintenance Schedule
            schedule = SupportIntegration._create_maintenance_schedule(asset_doc)
            schedule.insert(ignore_permissions=True)
            
            # Update Asset with schedule reference
            frappe.db.set_value("Asset", asset_doc.name, "sigma_maintenance_schedule", 
                              schedule.name, update_modified=False)
            frappe.db.set_value("Asset", asset_doc.name, "sigma_last_support_sync", 
                              now(), update_modified=False)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Asset to Maintenance Schedule",
            status="Success",
            source_doctype="Asset",
            source_name=asset_doc.name,
            target_doctype="Maintenance Schedule",
            target_name=schedule.name
        )
        
        frappe.db.commit()
    
    @staticmethod
    def _create_maintenance_schedule(asset_doc):
        """Create new Maintenance Schedule from Asset"""

        # Get maintenance frequency from asset or default to monthly
        frequency = asset_doc.get("maintenance_frequency") or "Monthly"

        schedule = frappe.get_doc({
            "doctype": "Maintenance Schedule",
            "item_code": asset_doc.get("sigma_item_code"),
            "item_name": asset_doc.asset_name,
            "company": asset_doc.company,  # Use asset's company instead of user default
            "transaction_date": today(),  # Required field for Maintenance Schedule
            "start_date": today(),
            "periodicity": frequency,
            "no_of_visits": 12,  # Default to 12 visits

            # Custom fields for Sigma integration
            "sigma_asset": asset_doc.name,
            "sigma_asset_location": asset_doc.get("location"),
            "sigma_asset_category": asset_doc.get("asset_category"),

            # Schedule items
            "items": [{
                "item_code": asset_doc.get("sigma_item_code"),
                "item_name": asset_doc.asset_name,
                "start_date": today(),
                "periodicity": frequency,
                "no_of_visits": 12,
                "sales_person": asset_doc.get("custodian")
            }]
        })

        return schedule
    
    @staticmethod
    def _update_maintenance_schedule(schedule, asset_doc):
        """Update existing Maintenance Schedule with Asset data"""
        schedule.item_name = asset_doc.asset_name
        schedule.sigma_asset_location = asset_doc.get("location")
        
        # Update schedule items
        if schedule.items:
            schedule.items[0].item_name = asset_doc.asset_name
            schedule.items[0].sales_person = asset_doc.get("custodian")
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def create_maintenance_visit_from_incident(incident_doc, method=None):
        """
        Create Maintenance Visit from Incident Report
        
        Args:
            incident_doc: Incident Report document
            method: Hook method
        """
        if not SigmaIntegrationAPI.check_erpnext_installed():
            return
        
        if not SigmaIntegrationAPI.is_integration_enabled("support"):
            return
        
        # Only create maintenance visit for asset-related incidents
        if not incident_doc.get("related_asset"):
            return
        
        asset = frappe.get_doc("Asset", incident_doc.related_asset)
        
        if not asset.get("sigma_item_code"):
            # Asset not synced to stock yet
            return
        
        # Create Maintenance Visit
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "company": frappe.defaults.get_user_default("Company"),
            "customer": asset.get("custodian") or "Internal",
            "mntc_date": now(),
            "mntc_time": now(),
            "completion_status": "Pending",
            
            # Custom fields
            "sigma_incident": incident_doc.name,
            "sigma_asset": asset.name,
            "sigma_incident_type": incident_doc.get("incident_type"),
            
            # Visit purposes
            "purposes": [{
                "item_code": asset.sigma_item_code,
                "item_name": asset.asset_name,
                "description": incident_doc.get("description") or "Corrective maintenance",
                "work_done": "",
                "service_person": incident_doc.get("assigned_to")
            }]
        })
        
        visit.insert(ignore_permissions=True)
        
        # Update Incident with Maintenance Visit reference
        frappe.db.set_value("Incident Report", incident_doc.name, 
                          "sigma_maintenance_visit", visit.name, update_modified=False)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Incident to Maintenance Visit",
            status="Success",
            source_doctype="Incident Report",
            source_name=incident_doc.name,
            target_doctype="Maintenance Visit",
            target_name=visit.name
        )
        
        frappe.db.commit()
    
    @staticmethod
    @SigmaIntegrationAPI.safe_integration_call
    def update_asset_from_maintenance_visit(visit_doc, method=None):
        """
        Update Asset status based on Maintenance Visit completion
        
        Args:
            visit_doc: Maintenance Visit document
            method: Hook method (on_submit, on_update)
        """
        if not visit_doc.get("sigma_asset"):
            return
        
        asset = frappe.get_doc("Asset", visit_doc.sigma_asset)
        
        # Update asset status based on visit completion
        if visit_doc.completion_status == "Fully Completed":
            # Asset maintenance completed
            asset.maintenance_status = "Maintained"
            asset.last_maintenance_date = visit_doc.mntc_date
            asset.next_maintenance_date = add_days(visit_doc.mntc_date, 30)  # Default 30 days
            
            # If asset was under maintenance, set back to operational
            if asset.status == "Under Maintenance":
                asset.status = "Operational"
        
        elif visit_doc.completion_status == "Partially Completed":
            asset.maintenance_status = "Partially Maintained"
        
        asset.save(ignore_permissions=True)
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Maintenance Visit to Asset Update",
            status="Success",
            source_doctype="Maintenance Visit",
            source_name=visit_doc.name,
            target_doctype="Asset",
            target_name=asset.name
        )
    
    @staticmethod
    @frappe.whitelist()
    def create_maintenance_request(asset_name: str, issue_description: str, 
                                   priority: str = "Medium") -> str:
        """
        Create Maintenance Visit request for an asset
        
        Args:
            asset_name: Asset document name
            issue_description: Description of the issue
            priority: Priority level (Low, Medium, High, Critical)
        
        Returns:
            Maintenance Visit name
        """
        if not frappe.has_permission("Maintenance Visit", "create"):
            frappe.throw(_("Insufficient permissions"))
        
        asset = frappe.get_doc("Asset", asset_name)
        
        if not asset.get("sigma_item_code"):
            frappe.throw(_("Asset not synced to Stock. Please sync first."))
        
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "company": frappe.defaults.get_user_default("Company"),
            "customer": asset.get("custodian") or "Internal",
            "mntc_date": now(),
            "mntc_time": now(),
            "completion_status": "Pending",
            "sigma_asset": asset.name,
            "sigma_priority": priority,
            "purposes": [{
                "item_code": asset.sigma_item_code,
                "item_name": asset.asset_name,
                "description": issue_description,
                "work_done": ""
            }]
        })
        
        visit.insert()
        
        # Update asset status
        frappe.db.set_value("Asset", asset_name, "status", "Under Maintenance")
        
        SigmaIntegrationAPI.log_integration(
            integration_type="Manual Maintenance Request",
            status="Success",
            source_doctype="Asset",
            source_name=asset_name,
            target_doctype="Maintenance Visit",
            target_name=visit.name
        )
        
        return visit.name
    
    @staticmethod
    @frappe.whitelist()
    def get_asset_maintenance_history(asset_name: str) -> List[Dict[str, Any]]:
        """
        Get complete maintenance history for an asset
        
        Returns list of maintenance visits with details
        """
        asset = frappe.get_doc("Asset", asset_name)
        
        if not asset.get("sigma_item_code"):
            return []
        
        # Get all maintenance visits for this asset
        visits = frappe.get_all(
            "Maintenance Visit",
            filters={"sigma_asset": asset_name},
            fields=["name", "mntc_date", "completion_status", "sigma_incident", 
                   "sigma_priority", "modified"],
            order_by="mntc_date desc"
        )
        
        # Get maintenance costs
        for visit in visits:
            visit["purposes"] = frappe.get_all(
                "Maintenance Visit Purpose",
                filters={"parent": visit.name},
                fields=["item_name", "description", "work_done", "service_person"]
            )
        
        return visits

