# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MonitoringAlert(Document):
	"""Stores device health alerts and status notifications from monitoring systems."""
	
	def validate(self):
		"""Validate alert data and denormalize asset from monitored device."""
		if self.monitored_device and not self.asset:
			# Denormalize asset from monitored device for faster queries
			device = frappe.get_doc("Monitored Device", self.monitored_device)
			if device.asset:
				self.asset = device.asset
	
	def on_update(self):
		"""Update monitored device last_seen timestamp and trigger workflows."""
		if self.monitored_device:
			frappe.db.set_value("Monitored Device", self.monitored_device, "last_seen", self.timestamp)
		
		# Auto-resolve if marked as resolved
		if self.resolved and not self.resolved_at:
			self.resolved_at = frappe.utils.now()
			self.resolved_by = frappe.session.user
			self.workflow_state = "Resolved"

