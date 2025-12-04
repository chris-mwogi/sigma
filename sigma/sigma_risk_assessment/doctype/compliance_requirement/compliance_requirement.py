# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days


class ComplianceRequirement(Document):
	def validate(self):
		"""Validate Compliance Requirement"""
		self.validate_compliance_owner()
		self.calculate_next_review_date()
		self.validate_dates()
	
	def validate_compliance_owner(self):
		"""Validate that compliance owner is a valid user"""
		if self.compliance_owner:
			if not frappe.db.exists("User", self.compliance_owner):
				frappe.throw(f"Compliance Owner '{self.compliance_owner}' is not a valid user")
	
	def calculate_next_review_date(self):
		"""Calculate next review date based on review frequency"""
		if self.review_frequency_days and not self.next_review_date:
			base_date = self.last_review_date or self.effective_date or getdate()
			self.next_review_date = add_days(base_date, self.review_frequency_days)
	
	def validate_dates(self):
		"""Validate date logic"""
		if self.target_compliance_date and self.effective_date:
			if getdate(self.target_compliance_date) < getdate(self.effective_date):
				frappe.throw("Target Compliance Date cannot be before Effective Date")
	
	def before_save(self):
		"""Update next review date when last review date changes"""
		if self.has_value_changed("last_review_date") and self.last_review_date and self.review_frequency_days:
			self.next_review_date = add_days(self.last_review_date, self.review_frequency_days)
	
	def on_update(self):
		"""Update linked information"""
		self.update_linked_risks()
		self.update_linked_controls()
	
	def update_linked_risks(self):
		"""Update the list of linked risks"""
		# Find all Risk Registers that reference this compliance requirement
		linked_risks = frappe.db.sql("""
			SELECT name, risk_title
			FROM `tabRisk Register`
			WHERE notes LIKE %s
			AND docstatus < 2
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_risks:
			risk_list = [f"{r.name}: {r.risk_title}" for r in linked_risks]
			self.linked_risks = "\n".join(risk_list)
		else:
			self.linked_risks = ""
	
	def update_linked_controls(self):
		"""Update the list of linked controls"""
		# Find all Risk Controls that reference this compliance requirement
		linked_controls = frappe.db.sql("""
			SELECT name, control_name
			FROM `tabRisk Control`
			WHERE notes LIKE %s
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_controls:
			control_list = [f"{c.name}: {c.control_name}" for c in linked_controls]
			self.linked_controls = "\n".join(control_list)
		else:
			self.linked_controls = ""


@frappe.whitelist()
def get_compliance_summary(requirement_name):
	"""Get compliance summary for a requirement"""
	requirement = frappe.get_doc("Compliance Requirement", requirement_name)
	
	# Count linked risks
	linked_risks_count = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabRisk Register`
		WHERE notes LIKE %s
		AND docstatus < 2
	""", ('%' + requirement_name + '%',), as_dict=True)
	
	# Count linked controls
	linked_controls_count = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabRisk Control`
		WHERE notes LIKE %s
	""", ('%' + requirement_name + '%',), as_dict=True)
	
	return {
		"requirement_title": requirement.requirement_title,
		"compliance_status": requirement.compliance_status,
		"current_compliance_level": requirement.current_compliance_level,
		"priority": requirement.priority,
		"regulatory_framework": requirement.regulatory_framework,
		"linked_risks_count": linked_risks_count[0].count if linked_risks_count else 0,
		"linked_controls_count": linked_controls_count[0].count if linked_controls_count else 0,
		"target_compliance_date": requirement.target_compliance_date,
		"next_review_date": requirement.next_review_date
	}

