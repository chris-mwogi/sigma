# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TelemetryEvent(Document):
	"""Stores sensor readings and performance metrics from any monitoring system."""
	
	def validate(self):
		"""Validate telemetry data and denormalize asset from monitored device."""
		if self.monitored_device and not self.asset:
			# Denormalize asset from monitored device for faster queries
			device = frappe.get_doc("Monitored Device", self.monitored_device)
			if device.asset:
				self.asset = device.asset
	
	def on_update(self):
		"""Update monitored device last_seen timestamp."""
		if self.monitored_device:
			frappe.db.set_value("Monitored Device", self.monitored_device, "last_seen", self.timestamp)

