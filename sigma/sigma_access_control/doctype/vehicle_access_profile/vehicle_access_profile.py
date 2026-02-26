# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class VehicleAccessProfile(Document):
    def validate(self):
        self.validate_validity_dates()
        self.check_duplicate_active_profile()
    
    def validate_validity_dates(self):
        """Validate date range"""
        if self.valid_until and self.valid_from:
            if getdate(self.valid_until) < getdate(self.valid_from):
                frappe.throw("Valid Until date must be after Valid From date")
    
    def check_duplicate_active_profile(self):
        """Check for duplicate active profiles for same vehicle"""
        if self.status == "Active":
            existing = frappe.db.exists("Vehicle Access Profile", {
                "vehicle": self.vehicle,
                "status": "Active",
                "name": ("!=", self.name)
            })
            if existing:
                frappe.throw(f"An active access profile already exists for this vehicle ({existing})")
    
    def on_update(self):
        """Auto-expire if past valid_until date"""
        if self.valid_until and getdate(self.valid_until) < getdate(today()) and self.status == "Active":
            self.db_set("status", "Expired")
            frappe.msgprint("Vehicle access profile has expired", indicator="orange")
    
    def blacklist(self, reason=None):
        """Blacklist the vehicle"""
        self.status = "Blacklisted"
        if reason:
            self.notes = (self.notes or "") + f"\n\nBlacklisted: {reason}"
        self.save()
        
        # Log the action
        frappe.get_doc({
            "doctype": "Access Event",
            "event_type": "Vehicle Blacklisted",
            "notes": f"Vehicle {self.license_plate} blacklisted. Reason: {reason}"
        }).insert(ignore_permissions=True)

