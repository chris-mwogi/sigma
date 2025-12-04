# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RiskImpactMatrix(Document):
	"""Risk Impact Matrix DocType for standardized impact level definitions"""
	
	def validate(self):
		"""Validate impact matrix"""
		self.validate_impact_score()
	
	def validate_impact_score(self):
		"""Ensure impact score is between 1 and 5"""
		if self.impact_score < 1 or self.impact_score > 5:
			frappe.throw("Impact Score must be between 1 and 5")
	
	def on_trash(self):
		"""Prevent deletion if impact level is used in assessments"""
		# Check if impact level is used in Risk Assessment
		linked_assessments = frappe.db.count("Risk Assessment", {
			"$or": [
				{"inherent_impact": self.name},
				{"residual_impact": self.name}
			]
		})
		if linked_assessments > 0:
			frappe.throw(f"Cannot delete impact level '{self.name}' as it is used in {linked_assessments} assessment(s)")

