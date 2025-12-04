# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RiskDashboardSettings(Document):
	"""Risk Dashboard Settings Single DocType for configuring dashboard visualization and thresholds"""
	
	def validate(self):
		"""Validate dashboard settings"""
		self.validate_thresholds()
	
	def validate_thresholds(self):
		"""Ensure thresholds are in ascending order"""
		if not (self.risk_score_low_threshold < self.risk_score_medium_threshold < 
				self.risk_score_high_threshold < self.risk_score_critical_threshold):
			frappe.throw("Risk score thresholds must be in ascending order: Low < Medium < High < Critical")
		
		if self.risk_score_critical_threshold > 25:
			frappe.throw("Critical threshold cannot exceed 25 (maximum risk score is 5 × 5 = 25)")


@frappe.whitelist()
def get_risk_rating(risk_score):
	"""Get risk rating based on risk score and configured thresholds"""
	settings = frappe.get_single("Risk Dashboard Settings")
	
	risk_score = int(risk_score)
	
	if risk_score <= settings.risk_score_low_threshold:
		return "Low"
	elif risk_score <= settings.risk_score_medium_threshold:
		return "Medium"
	elif risk_score <= settings.risk_score_high_threshold:
		return "High"
	else:
		return "Critical"


@frappe.whitelist()
def get_risk_color(risk_rating):
	"""Get color for risk rating"""
	settings = frappe.get_single("Risk Dashboard Settings")
	
	color_map = {
		"Low": settings.color_low,
		"Medium": settings.color_medium,
		"High": settings.color_high,
		"Critical": settings.color_critical
	}
	
	return color_map.get(risk_rating, "#6c757d")

