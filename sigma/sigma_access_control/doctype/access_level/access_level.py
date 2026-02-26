# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccessLevel(Document):
    def validate(self):
        self.validate_time_restrictions()
        self.validate_priority_unique()
    
    def validate_time_restrictions(self):
        """Validate time restriction fields if enabled"""
        if self.time_restrictions:
            if self.valid_from_time and self.valid_to_time:
                if self.valid_from_time >= self.valid_to_time:
                    frappe.throw("Valid From Time must be before Valid To Time")
    
    def validate_priority_unique(self):
        """Warn if priority conflicts with another level"""
        existing = frappe.db.exists("Access Level", {
            "level_priority": self.level_priority,
            "name": ("!=", self.name)
        })
        if existing:
            frappe.msgprint(
                f"Warning: Priority {self.level_priority} is also used by {existing}. Consider using unique priorities.",
                indicator="orange"
            )

