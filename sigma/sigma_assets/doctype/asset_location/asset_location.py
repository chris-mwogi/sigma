# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import math


class AssetLocation(Document):
	"""
	Hierarchical asset location with GPS tracking and geofencing.
	
	Supports:
	- Hierarchical structure (Site → Building → Floor → Room)
	- GPS coordinates and geofencing
	- Capacity management
	- Environmental conditions
	- Security clearance levels
	"""
	
	def validate(self):
		"""Validate location configuration."""
		self.validate_gps_coordinates()
		self.validate_geofence()
		self.validate_capacity()
		self.validate_environmental_conditions()
		self.calculate_occupancy()
	
	def validate_gps_coordinates(self):
		"""Validate GPS coordinates are within valid ranges."""
		if self.latitude:
			if self.latitude < -90 or self.latitude > 90:
				frappe.throw("Latitude must be between -90 and 90 degrees")
		
		if self.longitude:
			if self.longitude < -180 or self.longitude > 180:
				frappe.throw("Longitude must be between -180 and 180 degrees")
	
	def validate_geofence(self):
		"""Validate geofence configuration."""
		if self.geofence_enabled:
			if not self.latitude or not self.longitude:
				frappe.throw("GPS coordinates (Latitude and Longitude) are required when geofence is enabled")
			
			if self.geofence_shape == "Circle" and not self.geofence_radius_meters:
				frappe.throw("Geofence Radius is required for Circle geofence")
			
			if self.geofence_shape == "Polygon" and not self.geofence_coordinates:
				frappe.throw("Geofence Coordinates are required for Polygon geofence")
			
			# Validate JSON format for polygon coordinates
			if self.geofence_shape == "Polygon" and self.geofence_coordinates:
				try:
					coords = json.loads(self.geofence_coordinates)
					if not isinstance(coords, list) or len(coords) < 3:
						frappe.throw("Polygon geofence must have at least 3 coordinate points")
				except json.JSONDecodeError:
					frappe.throw("Geofence Coordinates must be valid JSON array")
	
	def validate_capacity(self):
		"""Validate capacity settings."""
		if self.total_capacity and self.total_capacity < 0:
			frappe.throw("Total Capacity cannot be negative")
		
		if self.max_asset_count and self.max_asset_count < 0:
			frappe.throw("Maximum Asset Count cannot be negative")
	
	def validate_environmental_conditions(self):
		"""Validate environmental condition ranges."""
		if self.temperature_min and self.temperature_max:
			if self.temperature_min > self.temperature_max:
				frappe.throw("Minimum Temperature cannot be greater than Maximum Temperature")
		
		if self.humidity_min and self.humidity_max:
			if self.humidity_min > self.humidity_max:
				frappe.throw("Minimum Humidity cannot be greater than Maximum Humidity")
	
	def calculate_occupancy(self):
		"""Calculate current occupancy and available capacity."""
		if not self.total_capacity:
			return
		
		# Count assets at this location
		asset_count = frappe.db.count("Asset", filters={"asset_location": self.name})
		
		# Calculate occupancy based on capacity unit
		if self.capacity_unit == "Asset Count":
			self.current_occupancy = asset_count
		else:
			# For other units, sum up asset space requirements
			# This would need to be implemented based on asset size fields
			self.current_occupancy = 0  # Placeholder
		
		# Calculate available capacity
		self.available_capacity = self.total_capacity - self.current_occupancy
		
		# Calculate occupancy percentage
		if self.total_capacity > 0:
			self.occupancy_percentage = (self.current_occupancy / self.total_capacity) * 100
		else:
			self.occupancy_percentage = 0
	
	def is_within_geofence(self, latitude, longitude):
		"""
		Check if given coordinates are within this location's geofence.
		
		Args:
			latitude (float): Latitude to check
			longitude (float): Longitude to check
		
		Returns:
			bool: True if within geofence, False otherwise
		"""
		if not self.geofence_enabled:
			return True
		
		if self.geofence_shape == "Circle":
			return self._is_within_circle_geofence(latitude, longitude)
		elif self.geofence_shape == "Polygon":
			return self._is_within_polygon_geofence(latitude, longitude)
		
		return False
	
	def _is_within_circle_geofence(self, latitude, longitude):
		"""Check if coordinates are within circular geofence."""
		distance = self._calculate_distance(
			self.latitude, self.longitude,
			latitude, longitude
		)
		return distance <= self.geofence_radius_meters
	
	def _is_within_polygon_geofence(self, latitude, longitude):
		"""Check if coordinates are within polygon geofence using ray casting algorithm."""
		try:
			coords = json.loads(self.geofence_coordinates)
			return self._point_in_polygon(latitude, longitude, coords)
		except:
			return False
	
	def _calculate_distance(self, lat1, lon1, lat2, lon2):
		"""
		Calculate distance between two GPS coordinates using Haversine formula.
		
		Returns:
			float: Distance in meters
		"""
		R = 6371000  # Earth's radius in meters
		
		lat1_rad = math.radians(lat1)
		lat2_rad = math.radians(lat2)
		delta_lat = math.radians(lat2 - lat1)
		delta_lon = math.radians(lon2 - lon1)
		
		a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		
		return R * c
	
	def _point_in_polygon(self, lat, lon, polygon):
		"""
		Ray casting algorithm to determine if point is inside polygon.
		
		Args:
			lat (float): Latitude of point
			lon (float): Longitude of point
			polygon (list): List of [lat, lon] coordinates
		
		Returns:
			bool: True if point is inside polygon
		"""
		inside = False
		n = len(polygon)
		
		for i in range(n):
			j = (i + 1) % n
			xi, yi = polygon[i]
			xj, yj = polygon[j]
			
			if ((yi > lon) != (yj > lon)) and (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi):
				inside = not inside
		
		return inside


@frappe.whitelist()
def get_location_hierarchy(location_name):
	"""
	Get full hierarchy path for a location.
	
	Args:
		location_name (str): Name of the location
	
	Returns:
		list: List of location names from root to current
	"""
	hierarchy = []
	current = location_name
	
	while current:
		location = frappe.get_doc("Asset Location", current)
		hierarchy.insert(0, {
			"name": location.name,
			"location_type": location.location_type,
			"location_code": location.location_code
		})
		current = location.parent_location
	
	return hierarchy


@frappe.whitelist()
def get_location_capacity_status(location_name):
	"""
	Get capacity status for a location.
	
	Args:
		location_name (str): Name of the location
	
	Returns:
		dict: Capacity status information
	"""
	location = frappe.get_doc("Asset Location", location_name)
	
	return {
		"total_capacity": location.total_capacity,
		"current_occupancy": location.current_occupancy,
		"available_capacity": location.available_capacity,
		"occupancy_percentage": location.occupancy_percentage,
		"capacity_unit": location.capacity_unit,
		"max_asset_count": location.max_asset_count,
		"is_full": location.occupancy_percentage >= 100 if location.occupancy_percentage else False
	}

