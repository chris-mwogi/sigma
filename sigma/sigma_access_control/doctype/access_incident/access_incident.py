# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds, now_datetime


class AccessIncident(Document):
    def validate(self):
        self.calculate_resolution_duration()
    
    def calculate_resolution_duration(self):
        """Calculate resolution duration if resolved"""
        if self.resolved_time and self.incident_time:
            seconds = time_diff_in_seconds(self.resolved_time, self.incident_time)
            self.resolution_duration_minutes = int(seconds / 60)
    
    def on_update(self):
        """Trigger notifications based on severity"""
        if self.has_value_changed("severity") or self.is_new():
            if self.severity in ["High", "Critical"]:
                self.notify_security_team()
    
    def notify_security_team(self):
        """Send notification for high severity incidents"""
        frappe.publish_realtime(
            "access_incident_alert",
            message={
                "incident": self.name,
                "type": self.incident_type,
                "severity": self.severity,
                "location": self.location
            },
            user="All"
        )
    
    def escalate(self, escalate_to, reason=None):
        """Escalate the incident"""
        self.escalated = 1
        self.escalated_to = escalate_to
        if reason:
            self.notes = (self.notes or "") + f"\n\nEscalation Reason: {reason}"
        self.save()
    
    def create_case(self):
        """Create a linked case from this incident"""
        if self.linked_case:
            frappe.throw("A case is already linked to this incident")
        
        case = frappe.get_doc({
            "doctype": "Case",
            "case_type": "Security Incident",
            "title": f"Access Incident: {self.incident_type}",
            "description": self.description,
            "location": self.location,
            "priority": self.severity
        })
        case.insert()
        self.linked_case = case.name
        self.save()
        return case.name

