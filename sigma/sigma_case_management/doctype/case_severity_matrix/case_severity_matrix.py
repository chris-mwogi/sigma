# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CaseSeverityMatrix(Document):
	"""Case Severity Matrix - Defines severity levels and response times"""
	
	def validate(self):
		"""Validate severity matrix"""
		# Validate severity score
		if self.severity_score and self.severity_score < 1:
			frappe.throw("Severity Score must be at least 1")
		
		# Validate response time
		if self.response_time_hours and self.response_time_hours < 1:
			frappe.throw("Response Time must be at least 1 hour")

