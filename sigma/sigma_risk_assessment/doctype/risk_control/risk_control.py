# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days


class RiskControl(Document):
	def validate(self):
		"""Validate Risk Control"""
		self.validate_control_owner()
		self.calculate_next_review_date()
	
	def validate_control_owner(self):
		"""Validate that control owner is a valid user"""
		if self.control_owner:
			if not frappe.db.exists("User", self.control_owner):
				frappe.throw(f"Control Owner '{self.control_owner}' is not a valid user")
	
	def calculate_next_review_date(self):
		"""Calculate next review date based on review frequency"""
		if self.review_frequency_days and not self.next_review_date:
			base_date = self.last_review_date or self.implementation_date or getdate()
			self.next_review_date = add_days(base_date, self.review_frequency_days)
	
	def before_save(self):
		"""Update next review date when last review date changes"""
		if self.has_value_changed("last_review_date") and self.last_review_date and self.review_frequency_days:
			self.next_review_date = add_days(self.last_review_date, self.review_frequency_days)
	
	def on_update(self):
		"""Update linked information"""
		self.update_linked_risks()
		self.update_linked_compliance()
	
	def update_linked_risks(self):
		"""Update the list of linked risks"""
		# Find all Risk Assessments that reference this control in existing_controls
		linked_risks = frappe.db.sql("""
			SELECT DISTINCT ra.linked_risk, rr.risk_title
			FROM `tabRisk Assessment` ra
			INNER JOIN `tabRisk Register` rr ON ra.linked_risk = rr.name
			WHERE ra.existing_controls LIKE %s
			AND ra.docstatus < 2
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_risks:
			risk_list = [f"{r.linked_risk}: {r.risk_title}" for r in linked_risks]
			self.linked_risks = "\n".join(risk_list)
		else:
			self.linked_risks = ""
	
	def update_linked_compliance(self):
		"""Update the list of linked compliance requirements"""
		# This will be implemented when Compliance Requirement DocType is created
		pass
	
	def on_trash(self):
		"""Prevent deletion if control is referenced in assessments"""
		linked_assessments = frappe.db.sql("""
			SELECT name
			FROM `tabRisk Assessment`
			WHERE existing_controls LIKE %s
			AND docstatus < 2
		""", ('%' + self.name + '%',))
		
		if linked_assessments:
			frappe.throw(
				f"Cannot delete control '{self.name}' as it is referenced in {len(linked_assessments)} risk assessment(s). "
				"Please remove the references first."
			)


@frappe.whitelist()
def get_control_effectiveness_summary(control_name):
	"""Get effectiveness summary for a control"""
	control = frappe.get_doc("Risk Control", control_name)
	
	# Count assessments where this control is mentioned
	assessments = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabRisk Assessment`
		WHERE existing_controls LIKE %s
		AND docstatus = 1
	""", ('%' + control_name + '%',), as_dict=True)
	
	return {
		"control_name": control.control_name,
		"effectiveness_rating": control.effectiveness_rating,
		"implementation_status": control.implementation_status,
		"linked_assessments": assessments[0].count if assessments else 0,
		"cost_of_control": control.cost_of_control,
		"automation_level": control.automation_level
	}

