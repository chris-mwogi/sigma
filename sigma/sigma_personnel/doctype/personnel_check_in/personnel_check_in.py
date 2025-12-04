# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class PersonnelCheckIn(Document):
	"""Personnel Check-In DocType."""
	
	def validate(self):
		"""Validate check-in."""
		self.validate_human_status()
		self.validate_zone_access()
		self.validate_ppe_requirements()
		self.validate_escort_requirements()
	
	def validate_human_status(self):
		"""Ensure human profile is active."""
		human = frappe.get_doc("Human Profile", self.human)
		if human.status != "Active":
			frappe.throw(f"Cannot check in {human.full_name} - Status is {human.status}")
	
	def validate_zone_access(self):
		"""Validate zone access clearance."""
		human = frappe.get_doc("Human Profile", self.human)
		zone = frappe.get_doc("Zone Configuration", self.initial_zone)
		
		clearance_hierarchy = ["Low", "Medium", "High", "Critical"]
		human_idx = clearance_hierarchy.index(human.clearance_level)
		zone_idx = clearance_hierarchy.index(zone.clearance_level_required)
		
		if human_idx < zone_idx:
			frappe.throw(
				f"Access Denied: {human.full_name} has {human.clearance_level} clearance, "
				f"but zone {zone.zone_name} requires {zone.clearance_level_required} clearance"
			)
	
	def validate_ppe_requirements(self):
		"""Validate PPE requirements for zone."""
		zone = frappe.get_doc("Zone Configuration", self.initial_zone)
		
		if zone.ppe_requirements and self.ppe_verification_status == "Not Required":
			frappe.msgprint(
				f"Warning: Zone {zone.zone_name} requires PPE: {zone.ppe_requirements}",
				indicator="orange"
			)
	
	def validate_escort_requirements(self):
		"""Validate escort requirements."""
		zone = frappe.get_doc("Zone Configuration", self.initial_zone)
		
		if zone.requires_escort and not self.escort_assigned:
			frappe.throw(f"Zone {zone.zone_name} requires an escort")
	
	def on_submit(self):
		"""Create initial zone presence on submit."""
		self.create_zone_presence()
		self.create_location_event()
	
	def create_zone_presence(self):
		"""Create zone presence record."""
		frappe.get_doc({
			"doctype": "Zone Presence",
			"human": self.human,
			"zone": self.initial_zone,
			"time_entered": self.timestamp_in,
			"last_seen": self.timestamp_in,
			"status": "Active",
			"related_check_in": self.name
		}).insert(ignore_permissions=True)
	
	def create_location_event(self):
		"""Create location event."""
		frappe.get_doc({
			"doctype": "Human Location Event",
			"human": self.human,
			"timestamp": self.timestamp_in,
			"zone": self.initial_zone,
			"source_type": self.method,
			"source_id": self.device_id or "Manual",
			"confidence": 1.0
		}).insert(ignore_permissions=True)

@frappe.whitelist()
def quick_check_in(human, entry_gate, initial_zone, method="Manual"):
	"""Quick check-in API for mobile/IoT."""
	doc = frappe.get_doc({
		"doctype": "Personnel Check-In",
		"human": human,
		"timestamp_in": now_datetime(),
		"entry_gate": entry_gate,
		"initial_zone": initial_zone,
		"method": method,
		"ppe_verification_status": "Not Required"
	})
	doc.insert(ignore_permissions=True)
	doc.submit()
	
	return {"status": "success", "check_in": doc.name}

