"""
Sigma Integration API - Unified API Layer

Provides centralized integration operations with error handling,
logging, and transaction management.
"""

import frappe
from frappe import _
from frappe.utils import now, get_datetime
import json
from typing import Dict, Any, Optional, List
import traceback


class IntegrationError(Exception):
    """Custom exception for integration errors"""
    pass


class SigmaIntegrationAPI:
    """
    Unified API layer for Sigma-ERPNext integrations
    
    Provides:
    - Error handling and logging
    - Transaction management
    - Integration status tracking
    - Retry mechanisms
    """
    
    @staticmethod
    def safe_integration_call(func):
        """
        Decorator for safe integration calls with error handling and logging
        
        Usage:
            @SigmaIntegrationAPI.safe_integration_call
            def my_integration_function(doc, method):
                # integration logic
        """
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                SigmaIntegrationAPI.log_integration(
                    integration_type=func.__name__,
                    status="Success",
                    details={"result": str(result)[:500]}
                )
                return result
            except Exception as e:
                error_msg = f"Integration error in {func.__name__}: {str(e)}"
                frappe.log_error(
                    title=f"Integration Error: {func.__name__}",
                    message=f"{error_msg}\n\n{traceback.format_exc()}"
                )
                SigmaIntegrationAPI.log_integration(
                    integration_type=func.__name__,
                    status="Failed",
                    details={"error": error_msg, "traceback": traceback.format_exc()[:1000]}
                )
                # Don't raise - allow document save to continue
                frappe.msgprint(
                    _("Integration warning: {0}").format(str(e)),
                    indicator="orange",
                    alert=True
                )
        return wrapper
    
    @staticmethod
    def log_integration(integration_type: str, status: str, details: Dict[str, Any] = None,
                       source_doctype: str = None, source_name: str = None,
                       target_doctype: str = None, target_name: str = None):
        """
        Log integration operation to Integration Log DocType
        
        Args:
            integration_type: Type of integration (e.g., "Asset to Item Sync")
            status: Success, Failed, Pending
            details: Additional details as dict
            source_doctype: Source DocType name
            source_name: Source document name
            target_doctype: Target DocType name
            target_name: Target document name
        """
        try:
            if not frappe.db.exists("DocType", "Integration Log"):
                # Integration Log DocType not yet created
                return
                
            log = frappe.get_doc({
                "doctype": "Integration Log",
                "integration_type": integration_type,
                "status": status,
                "timestamp": now(),
                "source_doctype": source_doctype,
                "source_name": source_name,
                "target_doctype": target_doctype,
                "target_name": target_name,
                "details": json.dumps(details) if details else None,
                "error_message": details.get("error") if details else None
            })
            log.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            # Don't fail if logging fails
            frappe.log_error(f"Failed to log integration: {str(e)}")
    
    @staticmethod
    def check_erpnext_installed() -> bool:
        """Check if ERPNext is installed"""
        return "erpnext" in frappe.get_installed_apps()
    
    @staticmethod
    def check_helpdesk_installed() -> bool:
        """Check if Frappe Helpdesk is installed"""
        return "helpdesk" in frappe.get_installed_apps()
    
    @staticmethod
    def get_integration_settings() -> Dict[str, Any]:
        """
        Get integration settings from Sigma Integration Settings DocType
        
        Returns dict with integration configuration
        """
        if not frappe.db.exists("DocType", "Sigma Integration Settings"):
            return {
                "enable_stock_integration": True,
                "enable_buying_integration": True,
                "enable_selling_integration": True,
                "enable_support_integration": True,
                "enable_crm_integration": True,
                "enable_projects_integration": True,
                "enable_helpdesk_integration": True,
                "auto_sync": True,
                "sync_interval": 3600  # 1 hour
            }
        
        settings = frappe.get_single("Sigma Integration Settings")
        return {
            "enable_stock_integration": settings.get("enable_stock_integration", True),
            "enable_buying_integration": settings.get("enable_buying_integration", True),
            "enable_selling_integration": settings.get("enable_selling_integration", True),
            "enable_support_integration": settings.get("enable_support_integration", True),
            "enable_crm_integration": settings.get("enable_crm_integration", True),
            "enable_projects_integration": settings.get("enable_projects_integration", True),
            "enable_helpdesk_integration": settings.get("enable_helpdesk_integration", True),
            "auto_sync": settings.get("auto_sync", True),
            "sync_interval": settings.get("sync_interval", 3600)
        }
    
    @staticmethod
    def is_integration_enabled(integration_name: str) -> bool:
        """
        Check if specific integration is enabled
        
        Args:
            integration_name: Name of integration (e.g., "stock", "buying", "support")
        """
        settings = SigmaIntegrationAPI.get_integration_settings()
        return settings.get(f"enable_{integration_name}_integration", False)
    
    @staticmethod
    @frappe.whitelist()
    def manual_sync(source_doctype: str, source_name: str, target_integration: str):
        """
        Manually trigger sync for a specific document
        
        Args:
            source_doctype: Source DocType (e.g., "Asset")
            source_name: Source document name
            target_integration: Target integration (e.g., "stock", "support")
        """
        if not frappe.has_permission(source_doctype, "write"):
            frappe.throw(_("Insufficient permissions"))
        
        doc = frappe.get_doc(source_doctype, source_name)
        
        if target_integration == "stock":
            from .stock_integration import StockIntegration
            return StockIntegration.sync_asset_to_item(doc)
        elif target_integration == "support":
            from .support_integration import SupportIntegration
            return SupportIntegration.sync_asset_maintenance(doc)
        elif target_integration == "buying":
            from .buying_integration import BuyingIntegration
            return BuyingIntegration.create_purchase_request(doc)
        elif target_integration == "selling":
            from .selling_integration import SellingIntegration
            return SellingIntegration.create_disposal_request(doc)
        elif target_integration == "crm":
            from .crm_integration import CRMIntegration
            return CRMIntegration.sync_visitor_to_contact(doc)
        elif target_integration == "projects":
            from .projects_integration import ProjectsIntegration
            return ProjectsIntegration.sync_case_to_project(doc)
        elif target_integration == "helpdesk":
            from .helpdesk_integration import HelpdeskIntegration
            return HelpdeskIntegration.sync_case_to_ticket(doc)
        else:
            frappe.throw(_("Unknown integration: {0}").format(target_integration))
    
    @staticmethod
    @frappe.whitelist()
    def get_integration_status(doctype: str, name: str) -> Dict[str, Any]:
        """
        Get integration status for a document
        
        Returns dict with sync status for each integration
        """
        if not frappe.has_permission(doctype, "read"):
            frappe.throw(_("Insufficient permissions"))
        
        doc = frappe.get_doc(doctype, name)
        status = {}
        
        # Check Stock integration
        if hasattr(doc, "sigma_item_code"):
            status["stock"] = {
                "synced": bool(doc.sigma_item_code),
                "target_doc": doc.sigma_item_code,
                "last_sync": doc.get("sigma_last_stock_sync")
            }
        
        # Check Support integration
        if hasattr(doc, "sigma_maintenance_schedule"):
            status["support"] = {
                "synced": bool(doc.sigma_maintenance_schedule),
                "target_doc": doc.sigma_maintenance_schedule,
                "last_sync": doc.get("sigma_last_support_sync")
            }
        
        # Add more integration status checks as needed
        
        return status

