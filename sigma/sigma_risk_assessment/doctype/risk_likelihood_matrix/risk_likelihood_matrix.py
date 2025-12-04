# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RiskLikelihoodMatrix(Document):
	"""Risk Likelihood Matrix DocType for standardized probability level definitions"""
	
	def validate(self):
		"""Validate likelihood matrix"""
		self.validate_likelihood_score()
	
	def validate_likelihood_score(self):
		"""Ensure likelihood score is between 1 and 5"""
		if self.likelihood_score < 1 or self.likelihood_score > 5:
			frappe.throw("Likelihood Score must be between 1 and 5")
	
	def on_trash(self):
		"""Prevent deletion if likelihood level is used in assessments"""
		# Check if likelihood level is used in Risk Assessment
		linked_assessments = frappe.db.count("Risk Assessment", {
			"$or": [
				{"inherent_likelihood": self.name},
				{"residual_likelihood": self.name}
			]
		})
		if linked_assessments > 0:
			frappe.throw(f"Cannot delete likelihood level '{self.name}' as it is used in {linked_assessments} assessment(s)")

