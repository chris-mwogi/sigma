# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime
import hashlib


class Case(Document):
	"""
	Comprehensive Case Management DocType
	Implements ISO 31000 Risk Management, ISO 37001 Anti-Bribery, 
	ISO 27001 Information Security standards
	"""
	
	def before_insert(self):
		"""Actions before inserting new case"""
		# Calculate SLA due date
		self.calculate_sla_due_date()
	
	def validate(self):
		"""Validate case data"""
		# Calculate risk score based on severity and category
		self.calculate_risk_score()
		
		# Validate dates
		self.validate_dates()
		
		# Set target closure date if not set
		if not self.target_closure_date and self.sla_due_date:
			self.target_closure_date = self.sla_due_date.date()
	
	def on_submit(self):
		"""Actions on case submission"""
		# Update status to Under Investigation if still Open
		if self.status == "Open":
			self.db_set("status", "Under Investigation")
	
	def on_cancel(self):
		"""Actions on case cancellation"""
		self.db_set("status", "Rejected")
	
	def calculate_risk_score(self):
		"""
		Calculate risk score based on ISO 31000 methodology
		Risk Score = Severity Score × Category Risk Weight
		"""
		if not self.severity or not self.case_category:
			self.risk_score = 0
			return
		
		try:
			# Get severity score
			severity_doc = frappe.get_doc("Case Severity Matrix", self.severity)
			severity_score = severity_doc.severity_score or 1
			
			# Get category risk weight
			category_doc = frappe.get_doc("Case Category", self.case_category)
			risk_weight = category_doc.risk_weight or 1
			
			# Calculate risk score
			self.risk_score = severity_score * risk_weight
			
		except Exception as e:
			frappe.log_error(f"Error calculating risk score: {str(e)}", "Case Risk Score Calculation")
			self.risk_score = 0
	
	def calculate_sla_due_date(self):
		"""Calculate SLA due date based on severity and settings"""
		if not self.severity:
			return
		
		try:
			# Get severity response time
			severity_doc = frappe.get_doc("Case Severity Matrix", self.severity)
			response_hours = severity_doc.response_time_hours or 72
			
			# Calculate SLA due date
			self.sla_due_date = add_to_date(now_datetime(), hours=response_hours)
			
		except Exception as e:
			frappe.log_error(f"Error calculating SLA: {str(e)}", "Case SLA Calculation")
			# Fallback to default SLA from settings
			settings = frappe.get_single("Case Settings")
			default_hours = settings.default_sla_hours or 72
			self.sla_due_date = add_to_date(now_datetime(), hours=default_hours)
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.target_closure_date and self.date_reported:
			if get_datetime(self.target_closure_date) < get_datetime(self.date_reported):
				frappe.throw("Target Closure Date cannot be before Date Reported")
		
		if self.actual_closure_date and self.date_reported:
			if get_datetime(self.actual_closure_date) < get_datetime(self.date_reported):
				frappe.throw("Actual Closure Date cannot be before Date Reported")
	
	def before_save(self):
		"""Actions before saving"""
		# Auto-set actual closure date when status is Closed
		if self.status == "Closed" and not self.actual_closure_date:
			self.actual_closure_date = now_datetime().date()
	
	def check_sla_breach(self):
		"""Check if case has breached SLA"""
		if not self.sla_due_date:
			return False
		
		if self.status in ["Closed", "Rejected"]:
			return False
		
		return now_datetime() > get_datetime(self.sla_due_date)
	
	def get_linked_investigations(self):
		"""Get all investigations linked to this case"""
		return frappe.get_all(
			"Case Investigation",
			filters={"linked_case": self.name},
			fields=["name", "investigation_title", "status", "lead_investigator"]
		)
	
	def get_linked_evidence(self):
		"""Get all evidence linked to this case"""
		return frappe.get_all(
			"Case Evidence",
			filters={"linked_case": self.name},
			fields=["name", "evidence_title", "evidence_type", "collection_date"]
		)
	
	def get_action_plans(self):
		"""Get all action plans linked to this case"""
		return frappe.get_all(
			"Case Action Plan",
			filters={"linked_case": self.name},
			fields=["name", "action_type", "responsible_person", "completion_status"]
		)


@frappe.whitelist()
def get_case_dashboard_data(case_name):
	"""Get dashboard data for a specific case"""
	case = frappe.get_doc("Case", case_name)
	
	return {
		"case": case.as_dict(),
		"investigations": case.get_linked_investigations(),
		"evidence": case.get_linked_evidence(),
		"action_plans": case.get_action_plans(),
		"sla_breached": case.check_sla_breach()
	}

