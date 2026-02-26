# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ResourceAvailability(Document):
	"""
	Resource Availability DocType - Tracks resource availability windows
	"""
	
	def validate(self):
		"""Validate resource availability"""
		self.validate_dates()
		self.validate_resource_exists()
	
	def validate_dates(self):
		"""Validate availability dates"""
		if self.availability_from >= self.availability_to:
			frappe.throw("Availability From must be before Availability To")
	
	def validate_resource_exists(self):
		"""Verify resource exists"""
		if not frappe.db.exists("Security Resource", self.resource):
			frappe.throw(f"Resource {self.resource} does not exist")
	
	def on_submit(self):
		"""Actions on submit"""
		frappe.msgprint(
			f"Resource Availability {self.name} submitted. "
			f"{self.resource} is {self.availability_status} from {self.availability_from} to {self.availability_to}"
		)
	
	def on_cancel(self):
		"""Actions on cancel"""
		frappe.msgprint(f"Resource Availability {self.name} cancelled")

