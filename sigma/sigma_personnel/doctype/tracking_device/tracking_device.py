# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, date_diff, now

class TrackingDevice(Document):
	"""
	Tracking Device DocType for Personnel Tracking Module.
	
	Manages IoT devices used for personnel tracking:
	- RFID/HID/NFC badges
	- BLE beacons
	- LoRaWAN trackers
	- GPS trackers
	- Panic buttons
	"""
	
	def validate(self):
		"""Validate tracking device."""
		self.validate_device_id()
		self.validate_assignment()
		self.check_battery_level()
	
	def validate_device_id(self):
		"""Ensure device ID is uppercase."""
		if self.device_id:
			self.device_id = self.device_id.upper()
	
	def validate_assignment(self):
		"""Validate device assignment."""
		if self.assigned_to and self.status not in ["Active", "Maintenance"]:
			frappe.throw(f"Cannot assign device with status '{self.status}' to personnel")
	
	def check_battery_level(self):
		"""Alert if battery level is low."""
		if self.battery_level and self.battery_level < 20:
			frappe.msgprint(
				f"Warning: Device {self.device_id} has low battery ({self.battery_level}%)",
				indicator="orange",
				alert=True
			)

@frappe.whitelist()
def update_device_location(device_id, latitude, longitude, timestamp=None):
	"""Update device location from IoT gateway."""
	if not timestamp:
		timestamp = now_datetime()
	
	device = frappe.get_doc("Tracking Device", device_id)
	device.last_seen = timestamp
	device.save(ignore_permissions=True)
	
	# If device is assigned, create location event
	if device.assigned_to:
		frappe.get_doc({
			"doctype": "Human Location Event",
			"human": device.assigned_to,
			"timestamp": timestamp,
			"source_type": device.device_type,
			"source_id": device_id,
			"latitude": latitude,
			"longitude": longitude,
			"confidence": 0.95
		}).insert(ignore_permissions=True)
	
	return {"status": "success", "device": device_id, "timestamp": timestamp}

@frappe.whitelist()
def update_battery_level(device_id, battery_level):
	"""Update device battery level."""
	device = frappe.get_doc("Tracking Device", device_id)
	device.battery_level = battery_level
	device.last_battery_check = now_datetime()
	device.save(ignore_permissions=True)
	
	return {"status": "success", "device": device_id, "battery_level": battery_level}

@frappe.whitelist()
def get_device_status(device_id):
	"""Get device status and last seen."""
	device = frappe.get_doc("Tracking Device", device_id)
	
	return {
		"device_id": device.device_id,
		"status": device.status,
		"assigned_to": device.assigned_to,
		"last_seen": device.last_seen,
		"battery_level": device.battery_level
	}

