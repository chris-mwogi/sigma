# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds, now_datetime


class DoorAlarm(Document):
    def validate(self):
        self.calculate_duration()
    
    def calculate_duration(self):
        """Calculate alarm duration"""
        if self.cleared_time and self.alarm_time:
            self.duration_seconds = int(time_diff_in_seconds(self.cleared_time, self.alarm_time))
    
    def acknowledge(self, user=None):
        """Acknowledge the alarm"""
        self.status = "Acknowledged"
        self.acknowledged_time = now_datetime()
        self.acknowledged_by = user or frappe.session.user
        self.save()
    
    def clear(self, user=None, action=None):
        """Clear the alarm"""
        self.status = "Cleared"
        self.cleared_time = now_datetime()
        self.cleared_by = user or frappe.session.user
        if action:
            self.response_action = action
        self.save()
    
    def create_incident(self):
        """Create an incident from this alarm"""
        if self.linked_incident:
            return self.linked_incident
        
        incident = frappe.get_doc({
            "doctype": "Access Incident",
            "incident_type": self.get_incident_type(),
            "severity": self.severity,
            "location": self.location,
            "zone": self.zone,
            "access_point": self.access_point,
            "incident_time": self.alarm_time,
            "description": f"Door alarm: {self.alarm_type} at {self.access_point}"
        })
        incident.insert()
        self.linked_incident = incident.name
        self.save()
        return incident.name
    
    def get_incident_type(self):
        """Map alarm type to incident type"""
        mapping = {
            "Door Forced Open": "Forced Entry",
            "Door Held Open": "Door Propped Open",
            "Tamper": "System Tampering"
        }
        return mapping.get(self.alarm_type, "Other")

