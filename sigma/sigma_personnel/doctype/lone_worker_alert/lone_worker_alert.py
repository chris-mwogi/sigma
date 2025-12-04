# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds

class LoneWorkerAlert(Document):
	"""Lone Worker Alert DocType - ISO 45001 compliance."""
	
	def validate(self):
		"""Validate alert."""
		self.calculate_response_time()
		self.check_escalation()
	
	def calculate_response_time(self):
		"""Calculate response time if responder assigned."""
		if self.responder and self.resolution_status in ["Acknowledged", "Investigating", "Resolved"]:
			response_seconds = time_diff_in_seconds(now_datetime(), self.raised_at)
			self.response_time = response_seconds
	
	def check_escalation(self):
		"""Check if alert needs escalation."""
		if self.resolution_status == "Open":
			time_open_seconds = time_diff_in_seconds(now_datetime(), self.raised_at)
			time_open_minutes = time_open_seconds / 60
			
			# Escalate based on severity
			escalation_thresholds = {
				"Critical": 5,   # 5 minutes
				"High": 15,      # 15 minutes
				"Medium": 30,    # 30 minutes
				"Low": 60        # 60 minutes
			}
			
			threshold = escalation_thresholds.get(self.severity, 30)
			
			if time_open_minutes > threshold:
				self.escalation_level = int(time_open_minutes / threshold)
				
				if self.escalation_level > 2:
					frappe.msgprint(
						f"CRITICAL: Alert {self.name} has been open for {int(time_open_minutes)} minutes!",
						indicator="red",
						alert=True
					)

@frappe.whitelist()
def acknowledge_alert(alert_name, responder):
	"""Acknowledge an alert."""
	alert = frappe.get_doc("Lone Worker Alert", alert_name)
	alert.resolution_status = "Acknowledged"
	alert.responder = responder
	alert.save(ignore_permissions=True)
	
	return {"status": "success", "alert": alert_name}

@frappe.whitelist()
def resolve_alert(alert_name, resolution_notes):
	"""Resolve an alert."""
	alert = frappe.get_doc("Lone Worker Alert", alert_name)
	alert.resolution_status = "Resolved"
	alert.resolution_notes = resolution_notes
	alert.save(ignore_permissions=True)
	
	return {"status": "success", "alert": alert_name}

