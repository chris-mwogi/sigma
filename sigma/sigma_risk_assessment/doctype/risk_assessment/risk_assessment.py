# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class RiskAssessment(Document):
	"""Risk Assessment DocType for ISO 31000 compliant risk assessments"""

	def validate(self):
		"""Validate risk assessment"""
		self.validate_linked_risk()
		self.fetch_matrix_scores()
		self.calculate_inherent_risk()
		self.calculate_residual_risk()
		self.validate_residual_risk()
		self.set_priority()

	def validate_linked_risk(self):
		"""Ensure linked risk exists and is submitted"""
		if self.linked_risk:
			risk = frappe.get_doc("Risk Register", self.linked_risk)
			if risk.docstatus != 1:
				frappe.throw(f"Risk Register '{self.linked_risk}' must be submitted before creating an assessment")

	def fetch_matrix_scores(self):
		"""Fetch scores from impact and likelihood matrices"""
		# Fetch inherent impact score
		if self.inherent_impact:
			impact = frappe.get_doc("Risk Impact Matrix", self.inherent_impact)
			self.inherent_impact_score = impact.impact_score

		# Fetch inherent likelihood score
		if self.inherent_likelihood:
			likelihood = frappe.get_doc("Risk Likelihood Matrix", self.inherent_likelihood)
			self.inherent_likelihood_score = likelihood.likelihood_score

		# Fetch residual impact score
		if self.residual_impact:
			impact = frappe.get_doc("Risk Impact Matrix", self.residual_impact)
			self.residual_impact_score = impact.impact_score

		# Fetch residual likelihood score
		if self.residual_likelihood:
			likelihood = frappe.get_doc("Risk Likelihood Matrix", self.residual_likelihood)
			self.residual_likelihood_score = likelihood.likelihood_score

	def calculate_inherent_risk(self):
		"""Calculate inherent risk score and rating"""
		if self.inherent_impact_score and self.inherent_likelihood_score:
			self.inherent_risk_score = self.inherent_impact_score * self.inherent_likelihood_score
			self.inherent_risk_rating = self.get_risk_rating(self.inherent_risk_score)

	def calculate_residual_risk(self):
		"""Calculate residual risk score and rating"""
		if self.residual_impact_score and self.residual_likelihood_score:
			self.residual_risk_score = self.residual_impact_score * self.residual_likelihood_score
			self.residual_risk_rating = self.get_risk_rating(self.residual_risk_score)

	def get_risk_rating(self, risk_score):
		"""Get risk rating based on score using Risk Dashboard Settings"""
		settings = frappe.get_single("Risk Dashboard Settings")

		if risk_score <= settings.risk_score_low_threshold:
			return "Low"
		elif risk_score <= settings.risk_score_medium_threshold:
			return "Medium"
		elif risk_score <= settings.risk_score_high_threshold:
			return "High"
		else:
			return "Critical"

	def validate_residual_risk(self):
		"""Ensure residual risk is not greater than inherent risk"""
		if self.inherent_risk_score and self.residual_risk_score:
			if self.residual_risk_score > self.inherent_risk_score:
				frappe.msgprint(
					"Warning: Residual risk score is greater than inherent risk score. "
					"This suggests controls are increasing risk rather than mitigating it.",
					indicator="orange",
					alert=True
				)

	def set_priority(self):
		"""Set priority based on residual risk rating"""
		if self.residual_risk_rating:
			priority_map = {
				"Low": "Low",
				"Medium": "Medium",
				"High": "High",
				"Critical": "Critical"
			}
			if not self.priority:
				self.priority = priority_map.get(self.residual_risk_rating, "Medium")

	def on_submit(self):
		"""Actions on submit"""
		self.status = "Completed"
		self.update_risk_register()

	def on_cancel(self):
		"""Actions on cancel"""
		self.status = "Draft"

	def update_risk_register(self):
		"""Update linked risk register with latest assessment date"""
		if self.linked_risk:
			risk = frappe.get_doc("Risk Register", self.linked_risk)
			risk.last_review_date = self.assessment_date
			risk.save(ignore_permissions=True)


@frappe.whitelist()
def get_risk_color(risk_rating):
	"""Get color for risk rating from Risk Dashboard Settings"""
	settings = frappe.get_single("Risk Dashboard Settings")
	color_map = {
		"Low": settings.color_low,
		"Medium": settings.color_medium,
		"High": settings.color_high,
		"Critical": settings.color_critical
	}
	return color_map.get(risk_rating, "#6c757d")
