# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccessZone(Document):
    def validate(self):
        self.validate_parent_zone()
        self.calculate_risk_score()
    
    def validate_parent_zone(self):
        """Prevent circular parent references"""
        if self.parent_zone:
            if self.parent_zone == self.name:
                frappe.throw("A zone cannot be its own parent")
            
            # Check for circular reference
            parent = self.parent_zone
            visited = {self.name}
            while parent:
                if parent in visited:
                    frappe.throw("Circular parent zone reference detected")
                visited.add(parent)
                parent = frappe.db.get_value("Access Zone", parent, "parent_zone")
    
    def calculate_risk_score(self):
        """Calculate risk score based on zone attributes"""
        score = 0
        
        # Zone type weights
        zone_weights = {
            "Public": 1, "Restricted": 2, "Secure": 3,
            "Critical Infrastructure": 5, "Hazardous": 4,
            "Data Center": 5, "Executive": 3
        }
        score += zone_weights.get(self.zone_type, 1) * 10
        
        # Clearance weights
        clearance_weights = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 5}
        score += clearance_weights.get(self.minimum_clearance, 0) * 5
        
        # Hazard weights
        hazard_weights = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Extreme": 5}
        score += hazard_weights.get(self.hazard_level, 0) * 8
        
        # Security feature adjustments
        if self.dual_person_rule:
            score += 10
        if self.anti_passback_enabled:
            score += 5
        if self.escort_required:
            score += 5
        
        self.risk_score = min(score, 100)  # Cap at 100
    
    def update_occupancy(self, delta):
        """Update current occupancy count"""
        new_occupancy = max(0, (self.current_occupancy or 0) + delta)
        self.db_set("current_occupancy", new_occupancy)
        
        if self.max_occupancy and new_occupancy >= self.max_occupancy:
            self.send_occupancy_alert()
    
    def send_occupancy_alert(self):
        """Send alert when max occupancy reached"""
        frappe.publish_realtime(
            "zone_occupancy_alert",
            message={
                "zone": self.name,
                "zone_name": self.zone_name,
                "current": self.current_occupancy,
                "max": self.max_occupancy
            },
            user="All"
        )
    
    def lockdown(self, reason=None):
        """Put zone in lockdown"""
        self.db_set("status", "Lockdown")
        frappe.publish_realtime(
            "zone_lockdown",
            message={"zone": self.name, "zone_name": self.zone_name, "reason": reason},
            user="All"
        )

