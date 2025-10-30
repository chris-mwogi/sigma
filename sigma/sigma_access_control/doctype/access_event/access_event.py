# sigma_access_control/doctype/access_event/access_event.py
import frappe
from frappe.model.document import Document

class AccessEvent(Document):
    def validate(self):
        # Ensure result is either 'Granted' or 'Denied'
        if self.result not in ("Granted", "Denied"):
            self.result = "Denied"

    def after_insert(self):
        # Real-time alert for denied access
        if self.result == "Denied":
            frappe.publish_realtime(
                "access_event_alert",
                message=f"Access denied at {self.access_point} for {self.card_id}",
                user="All"
            )
