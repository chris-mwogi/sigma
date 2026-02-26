# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SecurityResource(Document):
	"""
	Security Resource DocType - Parent class for all security resources
	Supports: Guards, Guard Dogs (K9), Security Vehicles, Security Equipment, Stations
	"""
	
	def validate(self):
		"""Validate security resource before save"""
		self.validate_guard_resource()
		self.validate_k9_resource()
		self.validate_vehicle_resource()
		self.validate_equipment_resource()
		self.validate_station_resource()
	
	def validate_guard_resource(self):
		"""Validate guard-specific fields"""
		if self.resource_type == "Guard":
			if not self.employee_id:
				frappe.throw("Employee ID is required for Guard resources")
			
			# Check for duplicate active guards
			existing = frappe.db.count(
				"Security Resource",
				filters={
					"resource_type": "Guard",
					"employee_id": self.employee_id,
					"status": "Active",
					"name": ["!=", self.name]
				}
			)
			if existing > 0:
				frappe.throw(f"Guard {self.employee_id} already has an active resource")
	
	def validate_k9_resource(self):
		"""Validate K9-specific fields"""
		if self.resource_type == "Guard Dog":
			if not self.handler:
				frappe.throw("Handler (Guard) is required for K9 resources")
			
			# Verify handler is a Guard resource
			try:
				handler = frappe.get_doc("Security Resource", self.handler)
				if handler.resource_type != "Guard":
					frappe.throw("Handler must be a Guard resource")
			except frappe.DoesNotExistError:
				frappe.throw(f"Handler {self.handler} does not exist")
	
	def validate_vehicle_resource(self):
		"""Validate vehicle-specific fields"""
		if self.resource_type == "Security Vehicle":
			if not self.registration_number:
				frappe.throw("Registration number is required for vehicles")
			
			# Check for duplicate registration
			existing = frappe.db.count(
				"Security Resource",
				filters={
					"resource_type": "Security Vehicle",
					"registration_number": self.registration_number,
					"name": ["!=", self.name]
				}
			)
			if existing > 0:
				frappe.throw(f"Vehicle {self.registration_number} already exists")
	
	def validate_equipment_resource(self):
		"""Validate equipment-specific fields"""
		if self.resource_type == "Security Equipment":
			if not self.equipment_category:
				frappe.throw("Equipment category is required for equipment resources")
			
			if not self.serial_number:
				frappe.throw("Serial number is required for equipment resources")
	
	def validate_station_resource(self):
		"""Validate station-specific fields"""
		if self.resource_type == "Stations":
			if not self.location:
				frappe.throw("Location is required for station resources")
			
			if not self.station_type:
				frappe.throw("Station type is required for station resources")
	
	def on_submit(self):
		"""Actions on submit"""
		frappe.msgprint(f"Security Resource {self.name} submitted successfully")
	
	def on_cancel(self):
		"""Actions on cancel"""
		# Check if resource is deployed
		deployments = frappe.db.count(
			"Resource Deployment Item",
			filters={"resource": self.name}
		)
		if deployments > 0:
			frappe.throw("Cannot cancel resource that has active deployments")

