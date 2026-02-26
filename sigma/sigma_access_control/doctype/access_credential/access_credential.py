# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class AccessCredential(Document):
    def validate(self):
        self.set_holder_name()
        self.validate_expiry_date()
        self.validate_holder()
        self.check_duplicate_active_credential()
    
    def set_holder_name(self):
        """Set holder name based on holder type"""
        if self.holder_type in ["Employee", "Contractor"] and self.human_profile:
            self.holder_name = frappe.db.get_value("Human Profile", self.human_profile, "full_name")
        elif self.holder_type == "Visitor" and self.visitor:
            # Visitor has first_name and last_name, not full_name
            visitor_data = frappe.db.get_value("Visitor", self.visitor, ["first_name", "last_name"], as_dict=True)
            if visitor_data:
                self.holder_name = f"{visitor_data.first_name or ''} {visitor_data.last_name or ''}".strip()
        elif self.holder_type == "Vehicle" and self.vehicle:
            self.holder_name = frappe.db.get_value("Vehicle", self.vehicle, "license_plate")
    
    def validate_expiry_date(self):
        """Validate expiry date is after issue date"""
        if self.expiry_date and self.issue_date:
            if getdate(self.expiry_date) <= getdate(self.issue_date):
                frappe.throw("Expiry Date must be after Issue Date")
    
    def validate_holder(self):
        """Ensure correct holder field is filled based on holder type"""
        if self.holder_type in ["Employee", "Contractor"] and not self.human_profile:
            frappe.throw("Human Profile is required for Employee/Contractor credentials")
        elif self.holder_type == "Visitor" and not self.visitor:
            frappe.throw("Visitor is required for Visitor credentials")
        elif self.holder_type == "Vehicle" and not self.vehicle:
            frappe.throw("Vehicle is required for Vehicle credentials")
    
    def check_duplicate_active_credential(self):
        """Check for duplicate active credentials of same type for same holder"""
        if self.status == "Active":
            filters = {
                "credential_type": self.credential_type,
                "status": "Active",
                "name": ("!=", self.name)
            }
            if self.human_profile:
                filters["human_profile"] = self.human_profile
            elif self.visitor:
                filters["visitor"] = self.visitor
            elif self.vehicle:
                filters["vehicle"] = self.vehicle
            
            existing = frappe.db.exists("Access Credential", filters)
            if existing:
                frappe.msgprint(
                    f"Warning: An active {self.credential_type} credential already exists for this holder ({existing})",
                    indicator="orange"
                )
    
    def on_update(self):
        """Auto-expire if past expiry date"""
        if self.expiry_date and getdate(self.expiry_date) < getdate(today()) and self.status == "Active":
            self.db_set("status", "Expired")
            frappe.msgprint("Credential has been automatically set to Expired", indicator="orange")
    
    def suspend(self, reason=None):
        """Suspend the credential"""
        self.status = "Suspended"
        self.save()
        self.log_status_change("Suspended", reason)
    
    def revoke(self, reason=None):
        """Revoke the credential"""
        self.status = "Revoked"
        self.save()
        self.log_status_change("Revoked", reason)
    
    def log_status_change(self, action, reason=None):
        """Log credential status change"""
        frappe.get_doc({
            "doctype": "Credential Issuance Log",
            "credential": self.name,
            "action": action,
            "reason": reason,
            "previous_status": self.get_doc_before_save().status if self.get_doc_before_save() else None,
            "new_status": self.status
        }).insert(ignore_permissions=True)

