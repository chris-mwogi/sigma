# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleCheckinCheckout(Document):
	def validate(self):
		"""Validate vehicle checkin/checkout record before saving"""
		self.calculate_distance_traveled()
		self.update_vehicle_status()
		self.auto_allocate_parking()

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

	def auto_allocate_parking(self):
		"""Auto-allocate parking zone on check-in"""
		# Only allocate on check-in, not check-out
		if self.check_in_time and not self.check_out_time and not self.parking_zone:
			try:
				# Get vehicle details
				if self.license_plate and frappe.db.exists("Vehicle", self.license_plate):
					vehicle = frappe.get_doc("Vehicle", self.license_plate)

					# Find available parking zone
					from sigma.sigma_vehicle_management.doctype.parking_zone.parking_zone import get_available_parking_zone

					zone_data = get_available_parking_zone(
						vehicle.vehicle_type,
						vehicle.dangerous_goods_flag or 0,
						None  # No location preference for now
					)

					if zone_data:
						self.parking_zone = zone_data.get("zone_name")
						frappe.msgprint(f"Parking allocated: {zone_data.get('zone_name')} ({zone_data.get('available_spaces')} spaces available)")
					else:
						frappe.msgprint("No parking zones available for this vehicle", alert=True)

			except Exception as e:
				frappe.log_error(f"Auto parking allocation error: {str(e)}")

	def after_insert(self):
		"""Actions after document is inserted"""
		# Increment parking zone occupancy on check-in
		if self.parking_zone and self.check_in_time and not self.check_out_time:
			self.update_parking_zone_occupancy("increment")

	def on_update(self):
		"""Actions when document is updated"""
		# Release parking zone on check-out
		if self.has_value_changed("check_out_time") and self.check_out_time and self.parking_zone:
			self.update_parking_zone_occupancy("decrement")

	def on_submit(self):
		"""Actions to perform when document is submitted"""
		pass

	def on_cancel(self):
		"""Actions to perform when document is cancelled"""
		# Release parking zone if assigned
		if self.parking_zone and not self.check_out_time:
			self.update_parking_zone_occupancy("decrement")

	def update_parking_zone_occupancy(self, action):
		"""Update parking zone occupancy"""
		try:
			if self.parking_zone and frappe.db.exists("Parking Zone", self.parking_zone):
				zone = frappe.get_doc("Parking Zone", self.parking_zone)

				if action == "increment":
					zone.increment_occupancy()
				elif action == "decrement":
					zone.decrement_occupancy()

		except Exception as e:
			frappe.log_error(f"Error updating parking zone occupancy: {str(e)}")

