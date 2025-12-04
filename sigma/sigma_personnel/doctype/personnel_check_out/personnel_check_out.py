# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds

class PersonnelCheckOut(Document):
	"""Personnel Check-Out DocType."""
	
	def validate(self):
		"""Validate check-out."""
		self.calculate_duration()
	
	def calculate_duration(self):
		"""Calculate duration on-site."""
		if self.related_check_in:
			check_in = frappe.get_doc("Personnel Check-In", self.related_check_in)
			duration_seconds = time_diff_in_seconds(self.timestamp_out, check_in.timestamp_in)
			self.duration_onsite = duration_seconds
	
	def on_submit(self):
		"""Close zone presence on submit."""
		self.close_zone_presence()
	
	def close_zone_presence(self):
		"""Close all active zone presence records."""
		zone_presences = frappe.get_all("Zone Presence",
			filters={"human": self.human, "status": "Active"},
			pluck="name"
		)
		
		for presence_name in zone_presences:
			presence = frappe.get_doc("Zone Presence", presence_name)
			presence.status = "Exited"
			presence.time_exited = self.timestamp_out
			presence.save(ignore_permissions=True)

@frappe.whitelist()
def quick_check_out(human, exit_gate, method="Manual"):
	"""Quick check-out API for mobile/IoT."""
	# Find latest check-in
	check_in = frappe.get_all("Personnel Check-In",
		filters={"human": human, "docstatus": 1},
		fields=["name"],
		order_by="timestamp_in desc",
		limit=1
	)
	
	doc = frappe.get_doc({
		"doctype": "Personnel Check-Out",
		"human": human,
		"related_check_in": check_in[0].name if check_in else None,
		"timestamp_out": now_datetime(),
		"exit_gate": exit_gate,
		"method": method
	})
	doc.insert(ignore_permissions=True)
	doc.submit()
	
	return {"status": "success", "check_out": doc.name}

