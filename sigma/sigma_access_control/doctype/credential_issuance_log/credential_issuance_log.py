# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CredentialIssuanceLog(Document):
    def before_insert(self):
        """Capture IP address for audit trail"""
        self.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
    
    def after_insert(self):
        """Send notifications for critical actions"""
        critical_actions = ["Revoked", "Lost Reported", "Stolen"]
        if self.action in critical_actions:
            self.notify_security_team()
    
    def notify_security_team(self):
        """Send notification to security team for critical credential actions"""
        # Get notification recipients from settings
        try:
            settings = frappe.get_single("Access Control Settings")
            if settings and settings.soc_notification_group:
                frappe.publish_realtime(
                    "credential_alert",
                    message={
                        "action": self.action,
                        "credential": self.credential,
                        "holder": self.holder_name,
                        "reason": self.reason
                    },
                    user="All"
                )
        except Exception:
            pass  # Settings may not exist yet

