# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import frappe
from frappe.model.document import Document


class AssetComponent(Document):
	"""
	Child table for tracking sub-components of assets.
	Supports tracking of components like RAM, hard drives, network cards, batteries, sensors, etc.
	Tracks installation and removal dates, and component status.
	"""

	def validate(self):
		"""Validate component data"""
		self.validate_dates()
		self.validate_component_cost()
		self.validate_gps_coordinates()
		self.validate_iot_configuration()

	def validate_dates(self):
		"""Ensure date_removed is after date_installed if both are provided"""
		if self.date_installed and self.date_removed:
			if self.date_removed < self.date_installed:
				frappe.throw(
					"Date Removed cannot be before Date Installed"
				)

		# If status is "Removed" or "Failed", date_removed should be set
		if self.status in ["Removed", "Failed"] and not self.date_removed:
			frappe.msgprint(
				"Warning: Component status is 'Removed' or 'Failed' but Date Removed is not set. "
				"Consider setting the Date Removed.",
				alert=True
			)

	def validate_component_cost(self):
		"""Ensure component cost is a positive number if provided"""
		if self.component_cost and self.component_cost < 0:
			frappe.throw(
				"Component Cost must be a positive number"
			)

	def validate_gps_coordinates(self):
		"""Validate GPS coordinates if component is tracked"""
		if self.is_tracked_component or self.is_iot_component:
			if self.component_latitude is not None:
				if self.component_latitude < -90 or self.component_latitude > 90:
					frappe.throw("Latitude must be between -90 and 90 degrees")

			if self.component_longitude is not None:
				if self.component_longitude < -180 or self.component_longitude > 180:
					frappe.throw("Longitude must be between -180 and 180 degrees")

	def validate_iot_configuration(self):
		"""Validate IoT configuration if component is an IoT device"""
		if self.is_iot_component:
			if self.component_iot_device_id and not self.component_iot_platform:
				frappe.msgprint(
					"Warning: IoT Device ID is set but IoT Platform is not specified.",
					alert=True
				)

