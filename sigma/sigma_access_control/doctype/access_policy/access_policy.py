# sigma_access_control/doctype/access_policy/access_policy.py
import frappe

from frappe.model.document import Document

class AccessPolicy(Document):
    def validate(self):
        if not self.allowed_roles or len(self.allowed_roles) == 0:
            frappe.throw("At least one role must be assigned in Allowed Roles")
