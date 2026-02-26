# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds


class AccessController(Document):
    def validate(self):
        self.validate_ip_address()
    
    def validate_ip_address(self):
        """Basic IP address validation"""
        if self.ip_address:
            parts = self.ip_address.split(".")
            if len(parts) != 4:
                frappe.throw("Invalid IP address format")
            for part in parts:
                try:
                    num = int(part)
                    if num < 0 or num > 255:
                        frappe.throw("Invalid IP address format")
                except ValueError:
                    frappe.throw("Invalid IP address format")
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.db_set("last_heartbeat", now_datetime())
        self.check_and_update_status()
    
    def check_and_update_status(self):
        """Check heartbeat and update status if needed"""
        if self.last_heartbeat:
            seconds_since_heartbeat = time_diff_in_seconds(now_datetime(), self.last_heartbeat)
            if seconds_since_heartbeat > 300:  # 5 minutes
                if self.status == "Online":
                    self.db_set("status", "Offline")
                    self.send_offline_alert()
    
    def send_offline_alert(self):
        """Send alert when controller goes offline"""
        frappe.publish_realtime(
            "controller_offline",
            message={
                "controller": self.name,
                "location": self.location,
                "last_heartbeat": str(self.last_heartbeat)
            },
            user="All"
        )
    
    def sync_credentials(self):
        """Sync credentials to controller (placeholder for integration)"""
        # This would integrate with actual hardware API
        self.db_set("last_sync_time", now_datetime())
        return {"status": "success", "message": "Credentials synced"}

