# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CaseSettings(Document):
	"""Case Management Settings - Single DocType for global configuration"""
	
	def validate(self):
		"""Validate settings"""
		# Validate SLA hours
		if self.default_sla_hours and self.default_sla_hours < 1:
			frappe.throw("Default SLA Hours must be at least 1 hour")
		
		if self.sla_reminder_hours_before and self.sla_reminder_hours_before < 1:
			frappe.throw("SLA Reminder Hours must be at least 1 hour")
		
		# Validate file size
		if self.max_file_size_mb and self.max_file_size_mb < 1:
			frappe.throw("Max File Size must be at least 1 MB")

