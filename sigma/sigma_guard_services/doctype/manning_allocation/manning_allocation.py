# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ManningAllocation(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_totals()
    
    def validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw(_("End Date cannot be before Start Date"))
    
    def calculate_totals(self):
        """Calculate total guards and K9 units"""
        total_guards = 0
        total_k9 = 0
        total_supervisors = 0
        
        for slot in self.manning_slots:
            if slot.resource_type in ["Security Guard", "Armed Guard", "Access Controller"]:
                total_guards += slot.quantity
            elif slot.resource_type in ["K9 Unit", "K9 Handler"]:
                total_k9 += slot.quantity
            elif slot.resource_type == "Security Supervisor":
                total_supervisors += slot.quantity
        
        self.total_guards = total_guards
        self.total_k9_units = total_k9
        self.total_supervisors = total_supervisors
    
    def on_submit(self):
        """Notify the security firm about the allocation"""
        self.notify_security_firm()
    
    def notify_security_firm(self):
        """Send notification to security firm about new allocation"""
        # Get supplier contact
        if self.security_firm:
            frappe.publish_realtime(
                "manning_allocation_created",
                {
                    "allocation": self.name,
                    "location": self.location,
                    "security_firm": self.security_firm
                },
                doctype="Manning Allocation",
                docname=self.name
            )

