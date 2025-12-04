# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class CaseActionPlan(Document):
	"""Case Action Plan DocType for managing corrective and preventive actions"""
	
	def validate(self):
		"""Validate action plan data"""
		self.validate_dates()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.completion_date and self.due_date:
			if get_datetime(self.completion_date) < get_datetime(self.due_date):
				# Allow early completion
				pass
	
	def before_save(self):
		"""Actions before saving"""
		# Auto-set completion date when status is Completed
		if self.status == "Completed" and not self.completion_date:
			self.completion_date = frappe.utils.today()

