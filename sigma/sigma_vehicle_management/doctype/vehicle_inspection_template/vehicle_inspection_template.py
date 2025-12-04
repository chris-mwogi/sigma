# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleInspectionTemplate(Document):
	"""
	Vehicle Inspection Template
	Master template for vehicle inspections
	OSHA 29 CFR 1910 - Occupational Safety and Health Standards
	"""
	
	def validate(self):
		"""Validate template"""
		self.validate_inspection_items()
	
	def validate_inspection_items(self):
		"""Validate that template has inspection items"""
		if not self.inspection_items:
			frappe.throw("Please add at least one inspection item to the template")

