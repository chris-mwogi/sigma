# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Vehicle(Document):
	def validate(self):
		"""Validate vehicle record before saving"""
		self.validate_company_vehicle_fields()
		self.set_default_values()
	
	def validate_company_vehicle_fields(self):
		"""Validate company vehicle specific fields"""
		if self.owner_type == "Company Vehicle":
			# Validate assignment type is set
			if not self.assignment_type:
				frappe.throw("Assignment Type is required for Company Vehicles")
			
			# Validate driver assignment
			if self.assignment_type == "Driver-Assigned" and not self.assigned_to_driver:
				frappe.throw("Assigned to Driver is required for Driver-Assigned vehicles")
			
			# Validate office assignment
			if self.assignment_type == "Office-Assigned" and not self.assigned_to_office:
				frappe.throw("Assigned to Office/Position is required for Office-Assigned vehicles")
	
	def set_default_values(self):
		"""Set default values based on owner type"""
		if self.owner_type == "Company Vehicle":
			# Company vehicles don't require passes by default
			if self.requires_pass is None:
				self.requires_pass = 0
		else:
			# Non-company vehicles require passes by default
			if self.requires_pass is None:
				self.requires_pass = 1

