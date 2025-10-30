# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatrolSchedule(Document):
	"""
	Tracks patrol schedules for security resources.
	
	Defines which patrol officer will visit which checkpoints on a specific date
	and tracks the status of the patrol.
	"""

	def validate(self):
		"""Validate patrol schedule data"""
		self.validate_location()
		self.validate_patrol_date()
		self.validate_patrol_officer()
		self.validate_checkpoints()

	def validate_location(self):
		"""Ensure location exists"""
		if not frappe.db.exists("Location", self.location):
			frappe.throw(f"Location {self.location} does not exist")

	def validate_patrol_date(self):
		"""Ensure patrol date is not in the past"""
		from datetime import datetime
		if self.patrol_date < datetime.now().date():
			frappe.msgprint("Warning: Patrol date is in the past")

	def validate_patrol_officer(self):
		"""Ensure patrol officer is a valid security resource"""
		if not frappe.db.exists("Security Resource", self.patrol_officer):
			frappe.throw(f"Security Resource {self.patrol_officer} does not exist")
		
		officer = frappe.get_doc("Security Resource", self.patrol_officer)
		if officer.resource_type != "Guard":
			frappe.throw("Patrol officer must be a Guard resource")

	def validate_checkpoints(self):
		"""Ensure at least one checkpoint is assigned"""
		if not self.checkpoints:
			frappe.throw("At least one checkpoint must be assigned to the patrol schedule")

	def on_submit(self):
		"""Update status to In Progress when submitted"""
		self.status = "In Progress"
		self.db_update()

	def get_pending_verifications(self):
		"""Get all pending patrol verifications for this schedule"""
		verifications = frappe.get_all(
			"Patrol Verification Record",
			filters={
				"patrol_schedule": self.name,
				"docstatus": 0
			},
			fields=["name", "checkpoint", "verification_time"]
		)
		return verifications

	def mark_completed(self):
		"""Mark patrol schedule as completed"""
		self.status = "Completed"
		self.db_update()

