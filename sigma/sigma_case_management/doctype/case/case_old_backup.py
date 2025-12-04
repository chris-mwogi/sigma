import frappe
from frappe.model.document import Document

class Case(Document):
    def before_insert(self):
        if not self.case_id:
            self.case_id = frappe.generate_hash(length=8).upper()
    
    def validate(self):
        if self.case_type == "Illegal Connection" and self.assigned_department != "Security":
            frappe.throw("Illegal Connection cases must be handled by Security Department")

    def on_submit(self):
        frappe.msgprint(f"Case {self.case_id} submitted successfully.")