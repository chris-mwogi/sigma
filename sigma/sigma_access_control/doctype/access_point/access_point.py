# sigma_access_control/doctype/access_point/access_point.py
import frappe

from frappe.model.document import Document

class AccessPoint(Document):
    def validate(self):
        # Optional: Ensure Active Hours format is correct
        if self.active_hours:
            import re
            pattern = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
            if not re.match(pattern, self.active_hours):
                frappe.throw("Active Hours must be in HH:MM-HH:MM format")
