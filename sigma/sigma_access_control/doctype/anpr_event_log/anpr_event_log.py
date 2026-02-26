# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ANPREventLog(Document):
    def before_insert(self):
        """Auto-match vehicle and profile on insert"""
        self.match_vehicle()
    
    def match_vehicle(self):
        """Attempt to match detected plate to database"""
        if not self.detected_plate:
            return
        
        # Clean the plate number
        clean_plate = self.detected_plate.upper().replace(" ", "").replace("-", "")
        
        # Search for matching vehicle
        vehicles = frappe.get_all("Vehicle", 
            filters={"license_plate": ["like", f"%{clean_plate}%"]},
            fields=["name", "license_plate"]
        )
        
        if vehicles:
            self.matched_vehicle = vehicles[0].name
            self.match_status = "Exact Match"
            
            # Find active access profile
            profile = frappe.db.get_value("Vehicle Access Profile", 
                {"vehicle": self.matched_vehicle, "status": "Active"},
                "name"
            )
            if profile:
                self.vehicle_access_profile = profile
        else:
            self.match_status = "No Match"
    
    def after_insert(self):
        """Process access decision and gate action"""
        if self.match_status == "No Match":
            self.create_alert()
        elif self.match_status == "Blacklisted":
            self.create_security_alert()
    
    def create_alert(self):
        """Create alert for unrecognized vehicle"""
        frappe.publish_realtime(
            "anpr_unknown_vehicle",
            message={
                "event": self.name,
                "plate": self.detected_plate,
                "location": self.location,
                "direction": self.direction
            },
            user="All"
        )
    
    def create_security_alert(self):
        """Create high priority alert for blacklisted vehicle"""
        frappe.get_doc({
            "doctype": "Access Incident",
            "incident_type": "Unauthorized Access",
            "severity": "High",
            "location": self.location,
            "access_point": self.access_point,
            "description": f"Blacklisted vehicle detected: {self.detected_plate}"
        }).insert(ignore_permissions=True)

