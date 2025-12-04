# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class RiskIncident(Document):
	def validate(self):
		"""Validate Risk Incident"""
		self.validate_dates()
		self.update_status_based_on_investigation()
	
	def validate_dates(self):
		"""Validate date logic"""
		if self.investigation_start_date and self.incident_date:
			if getdate(self.investigation_start_date) < getdate(self.incident_date):
				frappe.throw("Investigation Start Date cannot be before Incident Date")
		
		if self.investigation_completion_date and self.investigation_start_date:
			if getdate(self.investigation_completion_date) < getdate(self.investigation_start_date):
				frappe.throw("Investigation Completion Date cannot be before Investigation Start Date")
	
	def update_status_based_on_investigation(self):
		"""Update incident status based on investigation status"""
		if self.investigation_status == "Completed" and self.incident_status == "Under Investigation":
			self.incident_status = "Contained"
	
	def on_submit(self):
		"""Actions on submit"""
		if not self.investigation_owner:
			self.investigation_owner = self.reported_by
		
		if not self.investigation_start_date:
			self.investigation_start_date = getdate()
		
		if not self.investigation_status:
			self.investigation_status = "In Progress"
		
		self.create_incident_notification()
		self.trigger_risk_assessment()
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.incident_status = "Closed"
	
	def before_save(self):
		"""Update closure date when status is closed"""
		if self.incident_status == "Closed" and not self.closure_date:
			self.closure_date = getdate()
	
	def create_incident_notification(self):
		"""Create notification for incident"""
		# Notify investigation owner
		if self.investigation_owner:
			notification = frappe.new_doc("Notification Log")
			notification.subject = f"Risk Incident Assigned: {self.incident_title}"
			notification.for_user = self.investigation_owner
			notification.type = "Alert"
			notification.document_type = "Risk Incident"
			notification.document_name = self.name
			notification.email_content = f"""
				<p><strong>Risk Incident Assigned</strong></p>
				<p><strong>Incident:</strong> {self.incident_title}</p>
				<p><strong>Type:</strong> {self.incident_type}</p>
				<p><strong>Impact Level:</strong> {self.impact_level}</p>
				<p><strong>Incident Date:</strong> {self.incident_date}</p>
				<p><strong>Reported By:</strong> {self.reported_by}</p>
				<p>Please investigate and take appropriate action.</p>
			"""
			notification.insert(ignore_permissions=True)
		
		# Notify linked risk owner if risk is linked
		if self.linked_risk:
			risk = frappe.get_doc("Risk Register", self.linked_risk)
			if risk.risk_owner:
				notification = frappe.new_doc("Notification Log")
				notification.subject = f"Incident Related to Risk: {risk.risk_title}"
				notification.for_user = risk.risk_owner
				notification.type = "Alert"
				notification.document_type = "Risk Incident"
				notification.document_name = self.name
				notification.email_content = f"""
					<p><strong>Incident Related to Your Risk</strong></p>
					<p><strong>Risk:</strong> {risk.risk_title}</p>
					<p><strong>Incident:</strong> {self.incident_title}</p>
					<p><strong>Impact Level:</strong> {self.impact_level}</p>
					<p><strong>Incident Date:</strong> {self.incident_date}</p>
					<p>An incident has occurred related to a risk you own. Please review.</p>
				"""
				notification.insert(ignore_permissions=True)
	
	def trigger_risk_assessment(self):
		"""Suggest creating a risk assessment if linked risk exists"""
		if self.linked_risk and self.impact_level in ["High", "Critical"]:
			# This could trigger a workflow or notification to create an incident-triggered assessment
			pass


@frappe.whitelist()
def get_incident_summary(incident_name):
	"""Get summary of incident"""
	incident = frappe.get_doc("Risk Incident", incident_name)
	
	return {
		"incident_title": incident.incident_title,
		"incident_type": incident.incident_type,
		"incident_status": incident.incident_status,
		"impact_level": incident.impact_level,
		"financial_impact": incident.financial_impact,
		"incident_date": incident.incident_date,
		"investigation_status": incident.investigation_status,
		"investigation_owner": incident.investigation_owner,
		"linked_risk": incident.linked_risk,
		"linked_control": incident.linked_control,
		"closure_date": incident.closure_date
	}

