# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatrolVerificationItem(Document):
	"""Child table for Patrol Verification Record - tracks verified resources"""
	
	def validate(self):
		"""Validate patrol verification item"""
		self.validate_resource_exists()
		self.set_resource_name()

	def validate_resource_exists(self):
		"""Ensure resource exists"""
		if not frappe.db.exists("Security Resource", self.resource_id):
			frappe.throw(f"Security Resource {self.resource_id} does not exist")

	def set_resource_name(self):
		"""Auto-populate resource name from Security Resource"""
		if self.resource_id:
			resource = frappe.get_doc("Security Resource", self.resource_id)
			self.resource_name = resource.name

