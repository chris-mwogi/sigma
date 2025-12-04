# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HumanLocationEvent(Document):
	"""Human Location Event DocType - High-volume logging."""
	
	def after_insert(self):
		"""Update zone presence after location event."""
		if self.zone:
			self.update_zone_presence()
	
	def update_zone_presence(self):
		"""Update or create zone presence."""
		# Find active presence in this zone
		existing = frappe.get_all("Zone Presence",
			filters={"human": self.human, "zone": self.zone, "status": "Active"},
			limit=1
		)
		
		if existing:
			# Update last_seen
			presence = frappe.get_doc("Zone Presence", existing[0].name)
			presence.last_seen = self.timestamp
			presence.save(ignore_permissions=True)
		else:
			# Close any other active presences
			other_presences = frappe.get_all("Zone Presence",
				filters={"human": self.human, "status": "Active"},
				pluck="name"
			)
			for presence_name in other_presences:
				presence = frappe.get_doc("Zone Presence", presence_name)
				presence.status = "Exited"
				presence.time_exited = self.timestamp
				presence.save(ignore_permissions=True)
			
			# Create new presence
			frappe.get_doc({
				"doctype": "Zone Presence",
				"human": self.human,
				"zone": self.zone,
				"time_entered": self.timestamp,
				"last_seen": self.timestamp,
				"status": "Active"
			}).insert(ignore_permissions=True)

@frappe.whitelist()
def log_location(human, zone=None, latitude=None, longitude=None, source_type="Mobile App", source_id=None):
	"""API to log location event from IoT/Mobile."""
	from frappe.utils import now_datetime
	
	doc = frappe.get_doc({
		"doctype": "Human Location Event",
		"human": human,
		"timestamp": now_datetime(),
		"zone": zone,
		"latitude": latitude,
		"longitude": longitude,
		"source_type": source_type,
		"source_id": source_id,
		"confidence": 0.9
	})
	doc.insert(ignore_permissions=True)
	
	return {"status": "success", "event": doc.name}

