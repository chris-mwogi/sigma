# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SLADeployedResource(Document):
	"""Child table for SLA Compliance Record - tracks actually deployed resources"""
	
	def validate(self):
		"""Validate deployed resource"""
		self.validate_resource_exists()
		self.set_resource_type()

	def validate_resource_exists(self):
		"""Ensure the security resource exists"""
		if not frappe.db.exists("Security Resource", self.resource):
			frappe.throw(f"Security Resource {self.resource} does not exist")

	def set_resource_type(self):
		"""Auto-populate resource type from Security Resource"""
		if self.resource:
			resource_doc = frappe.get_doc("Security Resource", self.resource)
			self.resource_type = resource_doc.resource_type

