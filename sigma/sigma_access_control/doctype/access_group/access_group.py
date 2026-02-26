# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccessGroup(Document):
    def validate(self):
        self.validate_access_points()
    
    def validate_access_points(self):
        """Check for duplicate access points"""
        access_point_names = [row.access_point for row in self.access_points]
        if len(access_point_names) != len(set(access_point_names)):
            frappe.throw("Duplicate access points found in the list. Each access point can only appear once.")
    
    def on_update(self):
        """Clear cache when group is updated"""
        frappe.cache().delete_key(f"access_group_{self.name}")
    
    def get_all_access_points(self):
        """Get all access point names in this group"""
        return [row.access_point for row in self.access_points]

