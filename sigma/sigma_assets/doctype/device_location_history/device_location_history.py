# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import math


class DeviceLocationHistory(Document):
    """Child table for tracking device location history over time."""
    
    def validate(self):
        """Validate location coordinates."""
        self.validate_coordinates()
    
    def validate_coordinates(self):
        """Validate latitude and longitude ranges."""
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                frappe.throw(f"Latitude must be between -90 and 90 degrees. Got: {self.latitude}")
        
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                frappe.throw(f"Longitude must be between -180 and 180 degrees. Got: {self.longitude}")
        
        if self.heading is not None:
            if not (0 <= self.heading <= 360):
                frappe.throw(f"Heading must be between 0 and 360 degrees. Got: {self.heading}")
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        Returns distance in meters.
        """
        # Earth's radius in meters
        R = 6371000
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance

