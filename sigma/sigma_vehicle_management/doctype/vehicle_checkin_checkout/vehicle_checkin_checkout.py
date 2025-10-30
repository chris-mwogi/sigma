# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleCheckinCheckout(Document):
	def validate(self):
		"""Validate vehicle checkin/checkout record before saving"""
		self.calculate_distance_traveled()
		self.update_vehicle_status()
	
	def calculate_distance_traveled(self):
		"""Calculate distance traveled for company vehicles"""
		if self.is_company_vehicle and self.odometer_in and self.odometer_out:
			self.distance_traveled = self.odometer_out - self.odometer_in
	
	def update_vehicle_status(self):
		"""Update status based on check-out time"""
		if self.check_out_time:
			self.status = "Checked Out"
		elif not self.check_in_time:
			self.status = "Checked In"
	
	def on_submit(self):
		"""Actions to perform when document is submitted"""
		# Update parking space if assigned
		if self.parking_space_assigned and self.status == "Checked In":
			self.update_parking_space_status("Occupied")
	
	def on_cancel(self):
		"""Actions to perform when document is cancelled"""
		# Release parking space if assigned
		if self.parking_space_assigned:
			self.update_parking_space_status("Available")
	
	def update_parking_space_status(self, status):
		"""Update parking space status"""
		try:
			# This would update the parking space record
			# Using Data field, so we just store the reference
			pass
		except Exception as e:
			frappe.log_error(f"Error updating parking space: {str(e)}")

