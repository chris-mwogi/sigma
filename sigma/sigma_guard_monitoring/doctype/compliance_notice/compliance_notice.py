# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class ComplianceNotice(Document):
	"""
	Tracks compliance violations and notices sent to service providers.
	
	Manages the lifecycle of compliance notices from generation through
	provider response and resolution.
	"""

	def validate(self):
		"""Validate compliance notice data"""
		self.validate_supplier()
		self.validate_service_contract()
		self.validate_response_deadline()

	def validate_supplier(self):
		"""Ensure supplier exists"""
		if not frappe.db.exists("Supplier", self.supplier):
			frappe.throw(f"Supplier {self.supplier} does not exist")

	def validate_service_contract(self):
		"""Ensure service contract exists and belongs to supplier"""
		if not frappe.db.exists("Contract", self.service_contract):
			frappe.throw(f"Service Contract {self.service_contract} does not exist")
		
		contract = frappe.get_doc("Contract", self.service_contract)
		if contract.party_name != self.supplier:
			frappe.throw(f"Service Contract {self.service_contract} does not belong to {self.supplier}")

	def validate_response_deadline(self):
		"""Ensure response deadline is in the future"""
		if self.response_deadline <= self.notice_date:
			frappe.throw("Response deadline must be after notice date")

	def on_submit(self):
		"""Send notification to provider when notice is submitted"""
		self.send_notice_notification()

	def send_notice_notification(self):
		"""Send email notification to service provider"""
		supplier = frappe.get_doc("Supplier", self.supplier)
		
		if not supplier.email:
			frappe.msgprint(f"No email found for supplier {self.supplier}")
			return
		
		subject = f"Compliance Notice {self.name} - {self.violation_type}"
		message = f"""
		<p>Dear {supplier.supplier_name},</p>
		
		<p>A compliance notice has been issued for your service contract.</p>
		
		<p><strong>Notice Details:</strong></p>
		<ul>
			<li>Notice ID: {self.name}</li>
			<li>Notice Date: {self.notice_date}</li>
			<li>Violation Type: {self.violation_type}</li>
			<li>Response Deadline: {self.response_deadline}</li>
		</ul>
		
		<p><strong>Description:</strong></p>
		<p>{self.description}</p>
		
		<p>Please respond to this notice by the deadline.</p>
		
		<p>Regards,<br/>Compliance Team</p>
		"""
		
		try:
			frappe.sendmail(
				recipients=[supplier.email],
				subject=subject,
				message=message,
				reference_doctype="Compliance Notice",
				reference_name=self.name
			)
		except Exception as e:
			frappe.log_error(f"Failed to send compliance notice email: {str(e)}")

	def on_update_after_submit(self):
		"""Handle status changes after submission"""
		if self.status == "Responded" and not self.response_date:
			self.response_date = frappe.utils.today()
			self.db_update()

	def check_response_overdue(self):
		"""Check if response is overdue"""
		from datetime import datetime
		today = datetime.now().date()
		return today > self.response_deadline and self.status == "Pending"

