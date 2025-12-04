# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class GuardDeploymentSchedule(Document):
	"""
	Guard Deployment Schedule DocType - Deployment planning and scheduling
	"""
	
	def validate(self):
		"""Validate deployment schedule before save"""
		self.validate_dates()
		self.calculate_resource_summary()
	
	def validate_dates(self):
		"""Validate start and end dates"""
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("Start Date cannot be after End Date")
	
	def calculate_resource_summary(self):
		"""Calculate resource summary from deployment items"""
		self.total_guards = 0
		self.total_k9 = 0
		self.total_vehicles = 0
		self.total_equipment = 0

		for item in self.deployment_items_table:
			if item.resource:
				# Get resource type from Security Resource (using db.get_value to avoid loading child tables)
				resource_type = frappe.db.get_value("Security Resource", item.resource, "resource_type")
				item.resource_type = resource_type

				# Count by type (handle both old and new naming conventions)
				if resource_type and ("Guard" in resource_type or "Supervisor" in resource_type):
					self.total_guards += 1
				elif resource_type and "Dog" in resource_type:
					self.total_k9 += 1
				elif resource_type and "Vehicle" in resource_type:
					self.total_vehicles += 1
				elif resource_type and "Equipment" in resource_type:
					self.total_equipment += 1
	
	def on_submit(self):
		"""Actions on submit"""
		if self.status == "Draft":
			self.status = "Active"
			self.save()

