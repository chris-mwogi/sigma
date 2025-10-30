# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import frappe
from frappe.model.document import Document


class AssetProjectLink(Document):
	"""
	Child table for linking assets to multiple projects.
	Tracks the role of the asset in each project and assignment dates.
	"""

	def validate(self):
		"""Validate project link data"""
		self.validate_dates()

	def validate_dates(self):
		"""Ensure date_removed is after date_assigned if both are provided"""
		if self.date_assigned and self.date_removed:
			if self.date_removed < self.date_assigned:
				frappe.throw(
					"Date Removed cannot be before Date Assigned"
				)

