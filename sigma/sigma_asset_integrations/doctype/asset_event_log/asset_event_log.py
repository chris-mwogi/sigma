"""
Asset Event Log DocType
Tracks all asset-related events including GPS updates, network events, component changes, and status changes
"""
import frappe
import json
from frappe.model.document import Document


class AssetEventLog(Document):
    """Asset Event Log DocType for tracking asset events"""
    
    def validate(self):
        """Validate Asset Event Log"""
        self.validate_asset_exists()
        self.validate_gps_coordinates()
        self.validate_event_data()
    
    def validate_asset_exists(self):
        """Ensure the linked asset exists"""
        if self.asset and not frappe.db.exists("Asset", self.asset):
            frappe.throw(f"Asset {self.asset} does not exist")
    
    def validate_gps_coordinates(self):
        """Validate GPS coordinates if provided"""
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                frappe.throw("Latitude must be between -90 and 90")
        
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                frappe.throw("Longitude must be between -180 and 180")
    
    def validate_event_data(self):
        """Validate event data JSON format"""
        if self.event_data:
            try:
                if isinstance(self.event_data, str):
                    json.loads(self.event_data)
            except json.JSONDecodeError:
                frappe.throw("Event Data must be valid JSON")
        
        if self.raw_data:
            try:
                if isinstance(self.raw_data, str):
                    json.loads(self.raw_data)
            except json.JSONDecodeError:
                frappe.throw("Raw Data must be valid JSON")
    
    def before_insert(self):
        """Set processing date if not already set"""
        if not self.processing_date and self.processed:
            self.processing_date = frappe.utils.now()
    
    def on_update(self):
        """Update processing date when marked as processed"""
        if self.processed and not self.processing_date:
            self.db_set("processing_date", frappe.utils.now())

