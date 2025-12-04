# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds, now_datetime

class ZonePresence(Document):
	"""Zone Presence DocType - Current location state."""
	
	def validate(self):
		"""Validate zone presence."""
		self.calculate_duration()
		self.check_max_duration()
	
	def calculate_duration(self):
		"""Calculate presence duration."""
		if self.time_entered:
			end_time = self.time_exited or self.last_seen or now_datetime()
			duration_seconds = time_diff_in_seconds(end_time, self.time_entered)
			self.presence_duration = duration_seconds
	
	def check_max_duration(self):
		"""Check if max duration exceeded."""
		if self.status == "Active" and self.zone:
			zone = frappe.get_doc("Zone Configuration", self.zone)
			
			if zone.max_duration_minutes and zone.max_duration_minutes > 0:
				duration_minutes = (self.presence_duration or 0) / 60
				
				if duration_minutes > zone.max_duration_minutes:
					self.status = "Alert"
					self.alert_triggered = 1
					
					# Create alert
					frappe.get_doc({
						"doctype": "Lone Worker Alert",
						"human": self.human,
						"alert_type": "Max Duration Exceeded",
						"zone": self.zone,
						"severity": "Medium",
						"resolution_status": "Open"
					}).insert(ignore_permissions=True)

@frappe.whitelist()
def get_zone_occupants(zone_name):
	"""Get all personnel currently in a zone."""
	presences = frappe.get_all("Zone Presence",
		filters={"zone": zone_name, "status": "Active"},
		fields=["human", "time_entered", "last_seen"]
	)
	
	return presences

@frappe.whitelist()
def get_personnel_location(human):
	"""Get current location of personnel."""
	presence = frappe.get_all("Zone Presence",
		filters={"human": human, "status": "Active"},
		fields=["zone", "time_entered", "last_seen"],
		order_by="last_seen desc",
		limit=1
	)
	
	return presence[0] if presence else None

