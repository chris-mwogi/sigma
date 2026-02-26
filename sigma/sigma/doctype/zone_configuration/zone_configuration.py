# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ZoneConfiguration(Document):
	"""
	Zone Configuration DocType for Personnel Tracking Module.
	
	Defines zones with:
	- Hazard levels (ISO 45001)
	- Clearance requirements (IEC 62443)
	- PPE requirements
	- Occupancy limits
	- Lone worker monitoring
	- Emergency assembly points (ISO 22301)
	"""
	
	def validate(self):
		"""Validate zone configuration."""
		self.validate_zone_code()
		self.validate_clearance_vs_hazard()
		self.validate_parent_zone()
		self.validate_emergency_assembly_point()
		self.validate_occupancy_limits()
	
	def validate_zone_code(self):
		"""Ensure zone code is uppercase and unique."""
		if self.zone_code:
			self.zone_code = self.zone_code.upper()
	
	def validate_clearance_vs_hazard(self):
		"""Ensure clearance level matches hazard level (ISO 31000)."""
		hazard_to_clearance = {
			"Low": ["Low"],
			"Medium": ["Low", "Medium"],
			"High": ["Medium", "High"],
			"Critical": ["High", "Critical"]
		}
		
		if self.hazard_level and self.clearance_level_required:
			valid_clearances = hazard_to_clearance.get(self.hazard_level, [])
			if self.clearance_level_required not in valid_clearances:
				frappe.msgprint(
					f"Warning: Clearance level '{self.clearance_level_required}' may not be appropriate for hazard level '{self.hazard_level}'",
					indicator="orange"
				)
	
	def validate_parent_zone(self):
		"""Prevent circular references in zone hierarchy."""
		if self.parent_zone:
			if self.parent_zone == self.name:
				frappe.throw("Zone cannot be its own parent")
			
			# Check for circular reference
			parent = frappe.get_doc("Zone Configuration", self.parent_zone)
			visited = set([self.name])
			while parent.parent_zone:
				if parent.parent_zone in visited:
					frappe.throw("Circular reference detected in zone hierarchy")
				visited.add(parent.parent_zone)
				parent = frappe.get_doc("Zone Configuration", parent.parent_zone)
	
	def validate_emergency_assembly_point(self):
		"""Ensure emergency assembly point is a valid muster point."""
		if self.emergency_assembly_point:
			assembly_zone = frappe.get_doc("Zone Configuration", self.emergency_assembly_point)
			if assembly_zone.zone_type != "Muster Point":
				frappe.msgprint(
					f"Warning: Emergency assembly point '{self.emergency_assembly_point}' is not designated as a Muster Point",
					indicator="orange"
				)
	
	def validate_occupancy_limits(self):
		"""Validate occupancy and duration limits."""
		if self.max_occupancy and self.max_occupancy < 1:
			frappe.throw("Max occupancy must be at least 1")
		
		if self.max_duration_minutes and self.max_duration_minutes < 0:
			frappe.throw("Max duration cannot be negative")
		
		if self.lone_worker_alert_minutes and self.lone_worker_alert_minutes < 0:
			frappe.throw("Lone worker alert duration cannot be negative")

@frappe.whitelist()
def get_zone_hierarchy(zone_name):
	"""Get the full hierarchy path for a zone."""
	zone = frappe.get_doc("Zone Configuration", zone_name)
	hierarchy = [zone.zone_name]
	
	while zone.parent_zone:
		zone = frappe.get_doc("Zone Configuration", zone.parent_zone)
		hierarchy.insert(0, zone.zone_name)
	
	return " > ".join(hierarchy)

@frappe.whitelist()
def get_current_occupancy(zone_name):
	"""Get current number of personnel in a zone."""
	from frappe.utils import now_datetime
	
	occupancy = frappe.db.count("Zone Presence", {
		"zone": zone_name,
		"status": "Active"
	})
	
	return occupancy

@frappe.whitelist()
def check_zone_capacity(zone_name):
	"""Check if zone has reached capacity."""
	zone = frappe.get_doc("Zone Configuration", zone_name)
	
	if not zone.max_occupancy:
		return {"has_capacity": True, "current": 0, "max": None}
	
	current = get_current_occupancy(zone_name)
	has_capacity = current < zone.max_occupancy
	
	return {
		"has_capacity": has_capacity,
		"current": current,
		"max": zone.max_occupancy,
		"available": zone.max_occupancy - current if has_capacity else 0
	}

