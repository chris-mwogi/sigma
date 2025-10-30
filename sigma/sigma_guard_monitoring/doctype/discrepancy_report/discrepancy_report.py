# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class DiscrepancyReport(Document):
	"""
	Reports discrepancies found during patrol verification.
	
	Automatically links to SLA compliance system and can trigger
	compliance notices and surcharges for critical issues.
	"""

	def validate(self):
		"""Validate discrepancy report"""
		self.validate_patrol_verification()
		self.populate_from_verification()

	def validate_patrol_verification(self):
		"""Ensure patrol verification exists"""
		if not frappe.db.exists("Patrol Verification Record", self.patrol_verification):
			frappe.throw(f"Patrol Verification Record {self.patrol_verification} does not exist")

	def populate_from_verification(self):
		"""Auto-populate fields from patrol verification"""
		if self.patrol_verification:
			verification = frappe.get_doc("Patrol Verification Record", self.patrol_verification)
			self.patrol_date = verification.patrol_date
			self.checkpoint = verification.checkpoint
			self.patrol_officer = verification.patrol_officer

	def on_submit(self):
		"""Handle escalation for critical discrepancies"""
		if self.severity == "Critical":
			self.escalate_to_compliance()

	def escalate_to_compliance(self):
		"""Create compliance notice for critical discrepancies"""
		# Get service contract from checkpoint location
		checkpoint = frappe.get_doc("Patrol Checkpoint", self.checkpoint)
		
		# Find active contracts for this location
		contracts = frappe.get_all(
			"Contract",
			filters={
				"status": "Active",
				"location": checkpoint.location
			},
			fields=["name"]
		)
		
		if contracts:
			contract = contracts[0]
			self.service_contract = contract["name"]
			
			# Create compliance notice
			notice = frappe.new_doc("Compliance Notice")
			notice.notice_date = datetime.now().date()
			notice.supplier = frappe.db.get_value("Contract", contract["name"], "supplier")
			notice.service_contract = contract["name"]
			notice.violation_type = self.discrepancy_type
			notice.response_deadline = frappe.utils.add_days(datetime.now().date(), 1)
			notice.surcharge_applicable = 1
			
			notice.insert(ignore_permissions=True)
			notice.submit()
			
			self.compliance_notice = notice.name
			self.status = "Escalated"
			frappe.db.set_value("Discrepancy Report", self.name, {
				"compliance_notice": notice.name,
				"status": "Escalated"
			})

	def mark_resolved(self, resolution_notes):
		"""Mark discrepancy as resolved"""
		self.status = "Resolved"
		self.resolution_notes = resolution_notes
		self.resolved_date = datetime.now().date()
		self.save()

	def send_notification(self):
		"""Send notification to relevant parties"""
		subject = f"Discrepancy Report {self.name} - {self.severity} Severity"
		message = f"""
		<p>A discrepancy has been reported:</p>
		<ul>
			<li>Report ID: {self.name}</li>
			<li>Checkpoint: {self.checkpoint}</li>
			<li>Type: {self.discrepancy_type}</li>
			<li>Severity: {self.severity}</li>
			<li>Date: {self.patrol_date}</li>
		</ul>
		<p>{self.description}</p>
		"""
		
		# Send to compliance officers
		compliance_officers = frappe.get_all(
			"User",
			filters={"role": "Compliance Officer"},
			fields=["email"]
		)
		
		for officer in compliance_officers:
			if officer.get("email"):
				frappe.sendmail(
					recipients=[officer["email"]],
					subject=subject,
					message=message
				)

