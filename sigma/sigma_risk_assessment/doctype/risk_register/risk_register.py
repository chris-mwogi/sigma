# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate


class RiskRegister(Document):
	"""Risk Register DocType for managing enterprise-wide risks"""
	
	def validate(self):
		"""Validate risk register"""
		self.validate_risk_owner()
		self.calculate_next_review_date()
	
	def validate_risk_owner(self):
		"""Ensure risk owner is a valid user"""
		if self.risk_owner:
			if not frappe.db.exists("User", self.risk_owner):
				frappe.throw(f"Risk Owner '{self.risk_owner}' is not a valid user")
	
	def calculate_next_review_date(self):
		"""Calculate next review date based on review frequency"""
		if self.review_frequency_days and not self.next_review_date:
			base_date = self.last_review_date or self.date_identified or getdate()
			self.next_review_date = add_days(base_date, self.review_frequency_days)
	
	def on_submit(self):
		"""Actions on submit"""
		self.status = "Active"
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.status = "Closed"
	
	def before_save(self):
		"""Actions before save"""
		# Update last review date if status changed to "Under Review"
		if self.has_value_changed("status") and self.status == "Under Review":
			self.last_review_date = getdate()
			if self.review_frequency_days:
				self.next_review_date = add_days(self.last_review_date, self.review_frequency_days)


@frappe.whitelist()
def get_risk_summary(risk_register):
	"""Get summary of risk assessments for a risk register"""
	assessments = frappe.get_all(
		"Risk Assessment",
		filters={"linked_risk": risk_register, "docstatus": 1},
		fields=["name", "assessment_date", "inherent_risk_rating", "residual_risk_rating"],
		order_by="assessment_date desc",
		limit=10
	)
	return assessments

