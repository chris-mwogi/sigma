# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SLAComplianceRecord(Document):
	"""
	Tracks daily compliance of service contracts against SLA requirements.
	
	Compares required resources from the service contract with actually deployed
	resources on a specific date and generates compliance status and notices.
	"""

	def validate(self):
		"""Validate compliance record data"""
		self.validate_service_contract()
		self.validate_compliance_date()
		self.calculate_compliance_status()

	def validate_service_contract(self):
		"""Ensure service contract exists and is active"""
		if not frappe.db.exists("Contract", self.service_contract):
			frappe.throw(f"Service Contract {self.service_contract} does not exist")
		
		contract = frappe.get_doc("Contract", self.service_contract)
		if contract.status != "Active":
			frappe.throw(f"Service Contract {self.service_contract} is not active")

	def validate_compliance_date(self):
		"""Ensure compliance date is not in the future"""
		from frappe.utils import getdate, today
		if getdate(self.compliance_date) > getdate(today()):
			frappe.throw("Compliance date cannot be in the future")

	def calculate_compliance_status(self):
		"""
		Calculate compliance status based on required vs deployed resources.
		
		Status:
		- Compliant: All required resources deployed
		- Partial: Some required resources deployed
		- Non-Compliant: No resources deployed or major shortfall
		"""
		if not self.required_resources:
			self.compliance_status = "Compliant"
			return

		required_count = len(self.required_resources)
		deployed_count = len(self.deployed_resources)

		if deployed_count == 0:
			self.compliance_status = "Non-Compliant"
		elif deployed_count >= required_count:
			self.compliance_status = "Compliant"
		else:
			self.compliance_status = "Partial"

	def on_submit(self):
		"""Generate compliance notice if non-compliant"""
		if self.compliance_status in ["Non-Compliant", "Partial"]:
			self.generate_compliance_notice()

	def generate_compliance_notice(self):
		"""Generate a compliance notice for non-compliance"""
		contract = frappe.get_doc("Contract", self.service_contract)
		
		notice = frappe.new_doc("Compliance Notice")
		notice.notice_date = frappe.utils.today()
		notice.supplier = contract.party_name
		notice.service_contract = self.service_contract
		notice.compliance_record = self.name
		notice.violation_type = "Resource Shortfall"
		notice.description = self.get_shortfall_description()
		notice.response_deadline = frappe.utils.add_days(frappe.utils.today(), 1)
		notice.status = "Pending"
		
		notice.insert(ignore_permissions=True)
		notice.submit()
		
		self.notice_generated = notice.name
		frappe.db.set_value("SLA Compliance Record", self.name, "notice_generated", notice.name)

	def get_shortfall_description(self):
		"""Generate description of resource shortfall"""
		description = f"Compliance check for {self.compliance_date}:\n\n"
		description += f"Required Resources: {len(self.required_resources)}\n"
		description += f"Deployed Resources: {len(self.deployed_resources)}\n"
		description += f"Status: {self.compliance_status}\n\n"
		
		if self.shortfall_details:
			description += "Shortfall Details:\n"
			for shortfall in self.shortfall_details:
				description += f"- {shortfall.resource_type}: {shortfall.required_count} required, {shortfall.deployed_count} deployed\n"
		
		return description

