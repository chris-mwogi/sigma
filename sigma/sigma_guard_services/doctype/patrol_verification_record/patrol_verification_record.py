# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatrolVerificationRecord(Document):
	"""
	Records patrol verification at checkpoints.
	
	Captures GPS coordinates, photos, and resource verification data.
	Automatically detects discrepancies and creates reports.
	"""

	def validate(self):
		"""Validate patrol verification record"""
		self.validate_patrol_schedule()
		self.validate_checkpoint()
		self.validate_gps_coordinates()
		self.set_patrol_officer()

	def validate_patrol_schedule(self):
		"""Ensure patrol schedule exists"""
		if not frappe.db.exists("Patrol Schedule", self.patrol_schedule):
			frappe.throw(f"Patrol Schedule {self.patrol_schedule} does not exist")

	def validate_checkpoint(self):
		"""Ensure checkpoint exists"""
		if not frappe.db.exists("Patrol Checkpoint", self.checkpoint):
			frappe.throw(f"Patrol Checkpoint {self.checkpoint} does not exist")

	def validate_gps_coordinates(self):
		"""Validate GPS coordinates if provided"""
		if self.gps_latitude:
			if not (-90 <= self.gps_latitude <= 90):
				frappe.throw("GPS Latitude must be between -90 and 90")
		
		if self.gps_longitude:
			if not (-180 <= self.gps_longitude <= 180):
				frappe.throw("GPS Longitude must be between -180 and 180")

	def set_patrol_officer(self):
		"""Auto-populate patrol officer from patrol schedule"""
		if self.patrol_schedule:
			schedule = frappe.get_doc("Patrol Schedule", self.patrol_schedule)
			self.patrol_officer = schedule.patrol_officer

	def on_submit(self):
		"""Check for discrepancies and create report if needed"""
		self.check_for_discrepancies()

	def check_for_discrepancies(self):
		"""Check if resources verified match checkpoint requirements"""
		checkpoint = frappe.get_doc("Patrol Checkpoint", self.checkpoint)
		
		# Get required resources
		required_resources = {}
		for req in checkpoint.required_resources:
			required_resources[req.resource_type] = req.required_count
		
		# Get verified resources
		verified_resources = {}
		for item in self.resources_verified:
			verified_resources[item.resource_type] = verified_resources.get(item.resource_type, 0) + 1
		
		# Check for discrepancies
		discrepancies = []
		for resource_type, required_count in required_resources.items():
			verified_count = verified_resources.get(resource_type, 0)
			if verified_count < required_count:
				discrepancies.append({
					"resource_type": resource_type,
					"required_count": required_count,
					"verified_count": verified_count,
					"shortfall": required_count - verified_count
				})
		
		if discrepancies:
			self.discrepancies_found = 1
			self.create_discrepancy_report(discrepancies)
		else:
			self.discrepancies_found = 0

	def create_discrepancy_report(self, discrepancies):
		"""Create a discrepancy report"""
		report = frappe.new_doc("Discrepancy Report")
		report.patrol_verification = self.name
		report.patrol_date = self.patrol_date
		report.checkpoint = self.checkpoint
		report.patrol_officer = self.patrol_officer
		report.discrepancy_type = "Resource Shortfall"
		report.severity = self.calculate_severity(discrepancies)
		report.description = self.get_discrepancy_description(discrepancies)
		
		report.insert(ignore_permissions=True)
		report.submit()
		
		self.discrepancy_report = report.name
		frappe.db.set_value("Patrol Verification Record", self.name, "discrepancy_report", report.name)

	def calculate_severity(self, discrepancies):
		"""Calculate severity based on shortfalls"""
		total_shortfall = sum(d["shortfall"] for d in discrepancies)
		if total_shortfall >= 3:
			return "Critical"
		elif total_shortfall >= 2:
			return "High"
		else:
			return "Medium"

	def get_discrepancy_description(self, discrepancies):
		"""Generate description of discrepancies"""
		description = f"Discrepancies found at checkpoint {self.checkpoint}:\n\n"
		for d in discrepancies:
			description += f"- {d['resource_type']}: Required {d['required_count']}, Verified {d['verified_count']}, Shortfall {d['shortfall']}\n"
		return description

