# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LocationSecurityAssessment(Document):
	"""
	Location Security Assessment DocType - Security risk assessments per location
	"""
	
	def validate(self):
		"""Validate security assessment before save"""
		self.validate_vulnerability_score()
		self.calculate_overall_risk()
	
	def validate_vulnerability_score(self):
		"""Validate vulnerability score is between 0-100"""
		if self.vulnerability_score and (self.vulnerability_score < 0 or self.vulnerability_score > 100):
			frappe.throw("Vulnerability Score must be between 0 and 100")
	
	def calculate_overall_risk(self):
		"""Calculate overall risk level based on threat level and vulnerability"""
		# Auto-calculate if not set
		if not self.overall_risk_level and self.threat_level and self.vulnerability_score:
			if self.threat_level == "Critical" or self.vulnerability_score >= 80:
				self.overall_risk_level = "Critical"
			elif self.threat_level == "High" or self.vulnerability_score >= 60:
				self.overall_risk_level = "High"
			elif self.threat_level == "Medium" or self.vulnerability_score >= 40:
				self.overall_risk_level = "Medium"
			else:
				self.overall_risk_level = "Low"
	
	def on_submit(self):
		"""Actions on submit"""
		if self.status == "Draft" or self.status == "In Progress":
			self.status = "Completed"
			self.save()

