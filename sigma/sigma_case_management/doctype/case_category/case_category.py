# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CaseCategory(Document):
	"""Case Category - Master data for case categorization"""
	
	def validate(self):
		"""Validate case category"""
		# Validate risk weight
		if self.risk_weight and self.risk_weight < 1:
			frappe.throw("Risk Weight must be at least 1")

