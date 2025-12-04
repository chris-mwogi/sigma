# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class CaseInvestigation(Document):
	"""Case Investigation DocType for managing investigations"""
	
	def validate(self):
		"""Validate investigation data"""
		self.validate_dates()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.target_completion_date and self.start_date:
			if get_datetime(self.target_completion_date) < get_datetime(self.start_date):
				frappe.throw("Target Completion Date cannot be before Start Date")
		
		if self.actual_completion_date and self.start_date:
			if get_datetime(self.actual_completion_date) < get_datetime(self.start_date):
				frappe.throw("Actual Completion Date cannot be before Start Date")
	
	def before_save(self):
		"""Actions before saving"""
		# Auto-set actual completion date when status is Completed
		if self.status == "Completed" and not self.actual_completion_date:
			self.actual_completion_date = frappe.utils.today()
	
	def on_submit(self):
		"""Actions on investigation submission"""
		if self.status != "Completed":
			frappe.throw("Investigation must be marked as Completed before submission")

