# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SurchargeRecord(Document):
	"""
	Tracks financial surcharges for SLA compliance violations.
	
	Calculates surcharge amounts based on contract value and violation severity,
	and links to accounting module for debit note generation.
	"""

	def validate(self):
		"""Validate surcharge record data"""
		self.validate_compliance_notice()
		self.validate_service_contract()
		self.calculate_surcharge_amount()

	def validate_compliance_notice(self):
		"""Ensure compliance notice exists"""
		if not frappe.db.exists("Compliance Notice", self.compliance_notice):
			frappe.throw(f"Compliance Notice {self.compliance_notice} does not exist")

	def validate_service_contract(self):
		"""Ensure service contract exists"""
		if not frappe.db.exists("Contract", self.service_contract):
			frappe.throw(f"Service Contract {self.service_contract} does not exist")

	def calculate_surcharge_amount(self):
		"""Calculate surcharge amount based on calculation method"""
		if self.calculation_method == "Percentage of Contract":
			if self.contract_value and self.surcharge_percentage:
				self.surcharge_amount = (self.contract_value * self.surcharge_percentage) / 100
		elif self.calculation_method == "Fixed Amount":
			# Amount should be set manually
			pass
		elif self.calculation_method == "Per Day Rate":
			# Amount should be calculated based on days
			pass

	def on_submit(self):
		"""Generate debit note when surcharge is submitted"""
		self.generate_debit_note()

	def generate_debit_note(self):
		"""Generate a debit note for the surcharge"""
		try:
			supplier = frappe.get_doc("Supplier", self.supplier)
			
			debit_note = frappe.new_doc("Debit Note")
			debit_note.supplier = self.supplier
			debit_note.posting_date = self.surcharge_date
			debit_note.due_date = frappe.utils.add_days(self.surcharge_date, 30)
			debit_note.remarks = f"Surcharge for compliance violation - Notice: {self.compliance_notice}"
			
			# Add line item
			debit_note.append("items", {
				"item_code": "SLA-SURCHARGE",
				"description": f"SLA Compliance Surcharge - {self.compliance_notice}",
				"qty": 1,
				"rate": self.surcharge_amount,
				"amount": self.surcharge_amount
			})
			
			debit_note.insert(ignore_permissions=True)
			debit_note.submit()
			
			self.debit_note = debit_note.name
			self.debit_note_date = debit_note.posting_date
			self.status = "Invoiced"
			
			frappe.db.set_value("Surcharge Record", self.name, {
				"debit_note": debit_note.name,
				"debit_note_date": debit_note.posting_date,
				"status": "Invoiced"
			})
			
		except Exception as e:
			frappe.log_error(f"Failed to generate debit note: {str(e)}")
			frappe.msgprint(f"Warning: Could not generate debit note. Error: {str(e)}")

