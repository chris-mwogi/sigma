# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class EmergencyAccessRule(Document):
    def validate(self):
        self.validate_scope()

    def validate_scope(self):
        """Ensure at least one scope is defined"""
        # Check if at least one zone or access point is specified
        has_zones = self.affected_zones and len(self.affected_zones) > 0
        has_access_points = self.affected_access_points and len(self.affected_access_points) > 0
        if not has_zones and not has_access_points:
            frappe.throw("Please specify at least one affected zone or access point")
    
    def activate(self, authorized_by=None):
        """Activate the emergency rule"""
        if getattr(self, 'requires_confirmation', False) and not authorized_by:
            frappe.throw("This rule requires confirmation")

        self.db_set("status", "Triggered")
        self.db_set("last_triggered", now_datetime())
        if authorized_by:
            self.db_set("triggered_by", authorized_by)

        # Execute door actions
        self.execute_door_actions()

        # Send notifications
        self.send_notifications()

        # Schedule auto-revert if configured
        duration = getattr(self, 'duration_minutes', 0) or 0
        if duration > 0:
            self.schedule_revert()

        # Log the activation
        self.log_activation(authorized_by)

    def execute_door_actions(self):
        """Execute door actions on affected access points"""
        access_points = self.get_affected_access_points()
        action = getattr(self, 'action', 'Unlock All')
        for ap_name in access_points:
            frappe.publish_realtime(
                "emergency_door_action",
                message={"access_point": ap_name, "action": action, "rule": self.name},
                user="All"
            )

    def send_notifications(self):
        """Send notifications to configured recipients"""
        if not self.notification_recipients:
            return
        for recipient in self.notification_recipients:
            notification_type = getattr(recipient, 'notification_type', 'Email')
            email = getattr(recipient, 'email', None)
            if notification_type in ["Email", "All"] and email:
                frappe.sendmail(
                    recipients=[email],
                    subject=f"EMERGENCY: {self.emergency_type} - {self.rule_name}",
                    message=f"Emergency rule '{self.rule_name}' has been activated.\nType: {self.emergency_type}"
                )

    def get_affected_access_points(self):
        """Get list of affected access point names"""
        # Get from affected_access_points table
        if self.affected_access_points:
            return [row.access_point for row in self.affected_access_points]
        # If no specific access points, get from affected zones
        if self.affected_zones:
            zone_names = [row.zone for row in self.affected_zones]
            return frappe.get_all("Access Point", filters={"zone": ["in", zone_names]}, pluck="name")
        return []
    
    def schedule_revert(self):
        """Schedule automatic revert"""
        duration = getattr(self, 'duration_minutes', 0) or 0
        if duration > 0:
            frappe.enqueue(
                "sigma.sigma_access_control.doctype.emergency_access_rule.emergency_access_rule.revert_emergency_rule",
                rule_name=self.name,
                enqueue_after_commit=True,
                at_front=True,
                job_name=f"revert_emergency_{self.name}"
            )

    def log_activation(self, authorized_by=None):
        """Log emergency rule activation"""
        # Get first access point for logging
        access_points = self.get_affected_access_points()
        ap = access_points[0] if access_points else None
        frappe.get_doc({
            "doctype": "Access Event",
            "event_type": "Emergency Override",
            "access_point": ap,
            "event_time": now_datetime(),
            "notes": f"Emergency rule '{self.rule_name}' ({self.emergency_type}) activated. Authorized by: {authorized_by or 'System'}"
        }).insert(ignore_permissions=True)
    
    def deactivate(self):
        """Deactivate/revert the emergency rule"""
        self.db_set("status", "Active")
        frappe.publish_realtime(
            "emergency_rule_deactivated",
            message={"rule": self.name, "rule_name": self.rule_name},
            user="All"
        )


def revert_emergency_rule(rule_name):
    """Revert an emergency rule (called by scheduler)"""
    rule = frappe.get_doc("Emergency Access Rule", rule_name)
    if rule.status == "Triggered":
        rule.deactivate()

