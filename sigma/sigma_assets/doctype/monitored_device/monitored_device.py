# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import math


class MonitoredDevice(Document):
	"""Neutral representation of any monitored device from any monitoring system."""

	def validate(self):
		"""Validate device identifiers and update device_uid if needed."""
		if not self.device_uid:
			# Generate device_uid from available identifiers
			if self.mac_address:
				self.device_uid = self.mac_address
			elif self.imei:
				self.device_uid = self.imei
			elif self.serial_number:
				self.device_uid = self.serial_number
			elif self.ip_address:
				self.device_uid = self.ip_address
			else:
				frappe.throw("At least one device identifier (MAC, IMEI, Serial, or IP) is required")

		# Validate location coordinates if location tracking is enabled
		if self.enable_location_tracking:
			self.validate_location_coordinates()

		# Check geofence if enabled
		if self.geofence_enabled and self.current_latitude and self.current_longitude:
			self.check_geofence()

	def on_update(self):
		"""Update last_seen timestamp."""
		pass

	def validate_location_coordinates(self):
		"""Validate latitude and longitude ranges."""
		if self.current_latitude is not None:
			if not (-90 <= self.current_latitude <= 90):
				frappe.throw(f"Latitude must be between -90 and 90 degrees. Got: {self.current_latitude}")

		if self.current_longitude is not None:
			if not (-180 <= self.current_longitude <= 180):
				frappe.throw(f"Longitude must be between -180 and 180 degrees. Got: {self.current_longitude}")

		if self.heading is not None:
			if not (0 <= self.heading <= 360):
				frappe.throw(f"Heading must be between 0 and 360 degrees. Got: {self.heading}")

	def update_location(self, latitude, longitude, altitude=None, accuracy=None,
	                    speed=None, heading=None, location_source=None, address=None):
		"""
		Update device location and add to location history.

		Args:
			latitude: GPS latitude coordinate
			longitude: GPS longitude coordinate
			altitude: Altitude in meters (optional)
			accuracy: GPS accuracy in meters (optional)
			speed: Speed in km/h (optional)
			heading: Direction in degrees (optional)
			location_source: Source of location data (optional)
			address: Physical address (optional)
		"""
		# Update current location
		self.current_latitude = latitude
		self.current_longitude = longitude
		self.current_altitude = altitude
		self.location_accuracy = accuracy
		self.speed = speed
		self.heading = heading
		self.location_source = location_source or "GPS"
		self.last_location_update = now_datetime()

		# Add to location history
		self.append("location_history", {
			"timestamp": now_datetime(),
			"latitude": latitude,
			"longitude": longitude,
			"altitude": altitude,
			"accuracy": accuracy,
			"speed": speed,
			"heading": heading,
			"location_source": location_source or "GPS",
			"address": address
		})

		# Check geofence
		if self.geofence_enabled:
			self.check_geofence()

		self.save()

	def check_geofence(self):
		"""Check if device is within geofence boundaries."""
		if not (self.geofence_center_lat and self.geofence_center_lon and self.geofence_radius):
			return

		if not (self.current_latitude and self.current_longitude):
			return

		# Calculate distance from geofence center
		distance = self.calculate_distance(
			self.geofence_center_lat,
			self.geofence_center_lon,
			self.current_latitude,
			self.current_longitude
		)

		# Check if outside geofence
		was_outside = self.is_outside_geofence
		self.is_outside_geofence = distance > self.geofence_radius

		# Create alert if status changed
		if self.is_outside_geofence and not was_outside:
			self.create_geofence_alert("exited")
		elif not self.is_outside_geofence and was_outside:
			self.create_geofence_alert("entered")

	def create_geofence_alert(self, event_type):
		"""Create a monitoring alert when device enters/exits geofence."""
		try:
			alert = frappe.new_doc("Monitoring Alert")
			alert.monitored_device = self.name
			alert.alert_type = "Geofence Violation" if event_type == "exited" else "Geofence Entry"
			alert.severity = "Warning" if event_type == "exited" else "Info"
			alert.workflow_state = "Open"
			alert.message = f"Device {event_type} geofence at {self.last_location_update}"
			alert.timestamp = now_datetime()

			# Add location details to metadata
			alert.metadata = frappe.as_json({
				"latitude": self.current_latitude,
				"longitude": self.current_longitude,
				"geofence_center_lat": self.geofence_center_lat,
				"geofence_center_lon": self.geofence_center_lon,
				"geofence_radius": self.geofence_radius,
				"distance_from_center": self.calculate_distance(
					self.geofence_center_lat,
					self.geofence_center_lon,
					self.current_latitude,
					self.current_longitude
				)
			})

			alert.insert(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to create geofence alert: {str(e)}")

	@staticmethod
	def calculate_distance(lat1, lon1, lat2, lon2):
		"""
		Calculate distance between two GPS coordinates using Haversine formula.
		Returns distance in meters.
		"""
		# Earth's radius in meters
		R = 6371000

		# Convert to radians
		lat1_rad = math.radians(lat1)
		lat2_rad = math.radians(lat2)
		delta_lat = math.radians(lat2 - lat1)
		delta_lon = math.radians(lon2 - lon1)

		# Haversine formula
		a = (math.sin(delta_lat / 2) ** 2 +
		     math.cos(lat1_rad) * math.cos(lat2_rad) *
		     math.sin(delta_lon / 2) ** 2)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

		distance = R * c
		return distance

	def get_location_history(self, limit=100):
		"""Get location history for this device."""
		return frappe.get_all(
			"Device Location History",
			filters={"parent": self.name, "parenttype": "Monitored Device"},
			fields=["timestamp", "latitude", "longitude", "altitude", "speed", "heading", "location_source"],
			order_by="timestamp desc",
			limit=limit
		)

