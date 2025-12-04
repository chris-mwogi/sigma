# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ParkingZone(Document):
	"""Parking Zone management with auto-allocation and IoT integration"""
	
	def validate(self):
		"""Validate parking zone"""
		self.validate_capacity()
		self.calculate_utilization()
		self.update_status()
	
	def validate_capacity(self):
		"""Validate capacity settings"""
		if self.capacity < 0:
			frappe.throw("Capacity cannot be negative")
		
		if self.current_occupancy < 0:
			self.current_occupancy = 0
		
		if self.current_occupancy > self.capacity:
			frappe.msgprint(f"Warning: Current occupancy ({self.current_occupancy}) exceeds capacity ({self.capacity})")
	
	def calculate_utilization(self):
		"""Calculate utilization percentage and available spaces"""
		if self.capacity > 0:
			self.utilization_percentage = (self.current_occupancy / self.capacity) * 100
			self.available_spaces = self.capacity - self.current_occupancy
		else:
			self.utilization_percentage = 0
			self.available_spaces = 0
	
	def update_status(self):
		"""Auto-update status based on occupancy"""
		if self.status == "Maintenance" or self.status == "Inactive":
			return  # Don't auto-update if manually set to Maintenance or Inactive
		
		if self.current_occupancy >= self.capacity:
			self.status = "Full"
		else:
			self.status = "Active"
	
	def increment_occupancy(self):
		"""Increment occupancy when vehicle checks in"""
		self.current_occupancy += 1
		self.calculate_utilization()
		self.update_status()
		self.save()
	
	def decrement_occupancy(self):
		"""Decrement occupancy when vehicle checks out"""
		if self.current_occupancy > 0:
			self.current_occupancy -= 1
		self.calculate_utilization()
		self.update_status()
		self.save()
	
	def is_vehicle_type_allowed(self, vehicle_type):
		"""Check if vehicle type is allowed in this zone"""
		if not self.allowed_vehicle_types:
			return True  # If no restrictions, all types allowed
		
		for allowed_type in self.allowed_vehicle_types:
			if allowed_type.vehicle_type == vehicle_type:
				return True
		
		return False
	
	def can_accommodate_vehicle(self, vehicle_type, has_dangerous_goods=False):
		"""Check if zone can accommodate a vehicle"""
		# Check if zone is active
		if self.status not in ["Active"]:
			return False, f"Parking zone is {self.status}"
		
		# Check if space available
		if self.current_occupancy >= self.capacity:
			return False, "Parking zone is full"
		
		# Check vehicle type restrictions
		if not self.is_vehicle_type_allowed(vehicle_type):
			return False, f"Vehicle type '{vehicle_type}' not allowed in this zone"
		
		# Check hazmat approval
		if has_dangerous_goods and not self.hazmat_approved:
			return False, "Parking zone not approved for dangerous goods vehicles"
		
		return True, "Space available"


@frappe.whitelist()
def get_available_parking_zone(vehicle_type, has_dangerous_goods=0, location=None):
	"""
	Auto-allocation algorithm to find best available parking zone
	
	Args:
		vehicle_type: Type of vehicle (Car, Truck, etc.)
		has_dangerous_goods: 1 if vehicle carries dangerous goods, 0 otherwise
		location: Preferred location (optional)
	
	Returns:
		dict: Best parking zone or None if no space available
	"""
	has_dangerous_goods = int(has_dangerous_goods)
	
	# Build filters
	filters = {
		"status": "Active",
		"docstatus": 0
	}
	
	if location:
		filters["location"] = location
	
	# Get all active parking zones
	zones = frappe.get_all(
		"Parking Zone",
		filters=filters,
		fields=["name", "zone_name", "zone_code", "location", "capacity", "current_occupancy", 
		        "hazmat_approved", "utilization_percentage"],
		order_by="utilization_percentage ASC"  # Prefer zones with lower utilization
	)
	
	# Find best zone
	for zone_data in zones:
		zone = frappe.get_doc("Parking Zone", zone_data.name)
		can_accommodate, message = zone.can_accommodate_vehicle(vehicle_type, has_dangerous_goods)
		
		if can_accommodate:
			return {
				"zone_name": zone.zone_name,
				"zone_code": zone.zone_code,
				"location": zone.location,
				"available_spaces": zone.available_spaces,
				"utilization_percentage": zone.utilization_percentage
			}
	
	return None


@frappe.whitelist()
def allocate_parking_space(vehicle_license_plate, zone_name):
	"""
	Allocate a parking space to a vehicle
	
	Args:
		vehicle_license_plate: License plate of vehicle
		zone_name: Name of parking zone
	
	Returns:
		dict: Allocation result
	"""
	try:
		# Get vehicle
		vehicle = frappe.get_doc("Vehicle", vehicle_license_plate)
		
		# Get parking zone
		zone = frappe.get_doc("Parking Zone", zone_name)
		
		# Check if can accommodate
		can_accommodate, message = zone.can_accommodate_vehicle(
			vehicle.vehicle_type, 
			vehicle.dangerous_goods_flag
		)
		
		if not can_accommodate:
			return {"success": False, "message": message}
		
		# Increment occupancy
		zone.increment_occupancy()
		
		return {
			"success": True,
			"message": f"Parking space allocated in {zone.zone_name}",
			"zone_name": zone.zone_name,
			"zone_code": zone.zone_code,
			"available_spaces": zone.available_spaces
		}
	
	except Exception as e:
		frappe.log_error(f"Parking allocation error: {str(e)}")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def release_parking_space(zone_name):
	"""
	Release a parking space when vehicle checks out
	
	Args:
		zone_name: Name of parking zone
	
	Returns:
		dict: Release result
	"""
	try:
		zone = frappe.get_doc("Parking Zone", zone_name)
		zone.decrement_occupancy()
		
		return {
			"success": True,
			"message": f"Parking space released in {zone.zone_name}",
			"available_spaces": zone.available_spaces
		}
	
	except Exception as e:
		frappe.log_error(f"Parking release error: {str(e)}")
		return {"success": False, "message": str(e)}

