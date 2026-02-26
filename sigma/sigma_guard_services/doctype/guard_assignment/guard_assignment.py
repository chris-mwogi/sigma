# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GuardAssignment(Document):
    def validate(self):
        self.validate_manning_allocation()
        self.validate_security_resources()
        self.calculate_assignment_stats()
    
    def validate_manning_allocation(self):
        """Ensure assignment matches the manning allocation"""
        if self.manning_allocation:
            allocation = frappe.get_doc("Manning Allocation", self.manning_allocation)
            if allocation.security_firm != self.security_firm:
                frappe.throw(_("Security firm must match the manning allocation"))
    
    def validate_security_resources(self):
        """Ensure resources belong to the security firm"""
        for item in self.assigned_guards:
            resource = frappe.get_doc("Security Resource", item.security_resource)
            if resource.supplier != self.security_firm:
                frappe.throw(
                    _("Resource {0} does not belong to {1}").format(
                        item.security_resource, self.security_firm
                    )
                )
    
    def calculate_assignment_stats(self):
        """Calculate assignment statistics"""
        total_assigned = len(self.assigned_guards)
        day_shift = sum(1 for g in self.assigned_guards if g.shift_type == "Day Shift")
        night_shift = sum(1 for g in self.assigned_guards if g.shift_type == "Night Shift")
        
        self.total_assigned = total_assigned
        self.day_shift_count = day_shift
        self.night_shift_count = night_shift
    
    def on_submit(self):
        """Update manning allocation status and resource status"""
        self.update_manning_allocation_status()
        self.update_resource_status("Deployed")
    
    def on_cancel(self):
        """Revert resource status"""
        self.update_resource_status("Available")
    
    def update_manning_allocation_status(self):
        """Update the manning allocation status based on assignments"""
        if self.manning_allocation:
            allocation = frappe.get_doc("Manning Allocation", self.manning_allocation)
            # Calculate total required vs assigned
            total_required = sum(slot.quantity for slot in allocation.manning_slots)
            total_assigned = frappe.db.count("Guard Assignment Item", {
                "parent": ["in", frappe.get_all("Guard Assignment", 
                    filters={"manning_allocation": self.manning_allocation, "docstatus": 1},
                    pluck="name"
                )]
            })
            
            if total_assigned >= total_required:
                allocation.db_set("status", "Fully Staffed")
            elif total_assigned > 0:
                allocation.db_set("status", "Partially Filled")
    
    def update_resource_status(self, status):
        """Update the status of assigned resources"""
        for item in self.assigned_guards:
            frappe.db.set_value("Security Resource", item.security_resource, "status", status)

