# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days

class HumanProfile(Document):
	"""
	Human Profile DocType for Personnel Tracking Module.
	
	Master record for all personnel (employees, contractors, visitors).
	Includes:
	- Clearance levels (ISO 27001, IEC 62443)
	- Training levels (ISO 45001)
	- PPE requirements
	- Tracking device assignments
	- Emergency contact information
	- Risk scoring (ISO 31000)
	"""
	
	def validate(self):
		"""Validate human profile."""
		self.validate_employee_link()
		self.validate_clearance_vs_training()
		self.validate_tracking_consent()
		self.validate_emergency_contact()
		self.calculate_risk_score()
		self.check_training_expiry()
	
	def validate_employee_link(self):
		"""Validate employee link if person type is Employee."""
		if self.person_type == "Employee" and not self.linked_employee:
			frappe.msgprint(
				"Warning: Employee type should be linked to an Employee record",
				indicator="orange"
			)
	
	def validate_clearance_vs_training(self):
		"""Ensure training level is appropriate for clearance level."""
		clearance_to_training = {
			"Low": ["Basic"],
			"Medium": ["Basic", "Intermediate"],
			"High": ["Intermediate", "Advanced"],
			"Critical": ["Advanced", "Expert"]
		}
		
		if self.clearance_level and self.hazard_training_level:
			valid_training = clearance_to_training.get(self.clearance_level, [])
			if self.hazard_training_level not in valid_training:
				frappe.msgprint(
					f"Warning: Training level '{self.hazard_training_level}' may not be sufficient for clearance level '{self.clearance_level}'",
					indicator="orange"
				)
	
	def validate_tracking_consent(self):
		"""Ensure consent is signed if tracking is enabled (GDPR compliance)."""
		if self.tracking_enabled and not self.consent_signed:
			frappe.throw("Tracking consent must be signed before enabling tracking (GDPR/Data Privacy)")
	
	def validate_emergency_contact(self):
		"""Validate emergency contact information."""
		if self.status == "Active":
			if not self.emergency_contact_name or not self.emergency_contact_phone:
				frappe.msgprint(
					"Warning: Emergency contact information is recommended for active personnel",
					indicator="orange"
				)
	
	def calculate_risk_score(self):
		"""Calculate risk score based on clearance, training, and PPE (ISO 31000)."""
		score = 0.0
		
		# Clearance level risk
		clearance_risk = {
			"Low": 1.0,
			"Medium": 2.0,
			"High": 3.0,
			"Critical": 4.0
		}
		score += clearance_risk.get(self.clearance_level, 1.0)
		
		# Training level mitigation
		training_mitigation = {
			"Basic": 1.0,
			"Intermediate": 0.75,
			"Advanced": 0.5,
			"Expert": 0.25
		}
		score *= training_mitigation.get(self.hazard_training_level, 1.0)
		
		# PPE compliance
		if not self.ppe_required or not self.ppe_certified_date:
			score *= 1.5  # Increase risk if PPE not certified
		
		# Training expiry
		if self.next_training_due and getdate(self.next_training_due) < getdate():
			score *= 1.3  # Increase risk if training expired
		
		self.risk_score = round(score, 2)
	
	def check_training_expiry(self):
		"""Alert if training is expiring soon."""
		if self.next_training_due:
			days_until_expiry = (getdate(self.next_training_due) - getdate()).days
			if days_until_expiry < 0:
				frappe.msgprint(
					f"Alert: Training expired {abs(days_until_expiry)} days ago",
					indicator="red",
					alert=True
				)
			elif days_until_expiry <= 30:
				frappe.msgprint(
					f"Warning: Training expires in {days_until_expiry} days",
					indicator="orange",
					alert=True
				)
	
	def on_submit(self):
		"""Actions on submit."""
		self.activate_tracking_devices()
	
	def activate_tracking_devices(self):
		"""Activate assigned tracking devices."""
		if self.primary_tracking_device:
			device = frappe.get_doc("Tracking Device", self.primary_tracking_device)
			device.assigned_to = self.name
			device.status = "Active"
			device.save(ignore_permissions=True)
		
		if self.secondary_tracking_device:
			device = frappe.get_doc("Tracking Device", self.secondary_tracking_device)
			device.assigned_to = self.name
			device.status = "Active"
			device.save(ignore_permissions=True)

@frappe.whitelist()
def get_current_location(human_profile):
	"""Get current location of a person."""
	zone_presence = frappe.get_all("Zone Presence", 
		filters={"human": human_profile, "status": "Active"},
		fields=["zone", "time_entered", "last_seen"],
		order_by="last_seen desc",
		limit=1
	)
	
	if zone_presence:
		return zone_presence[0]
	return None

@frappe.whitelist()
def check_zone_access(human_profile, zone_name):
	"""Check if person has access to a zone."""
	human = frappe.get_doc("Human Profile", human_profile)
	zone = frappe.get_doc("Zone Configuration", zone_name)
	
	# Check clearance level
	clearance_hierarchy = ["Low", "Medium", "High", "Critical"]
	human_clearance_idx = clearance_hierarchy.index(human.clearance_level)
	zone_clearance_idx = clearance_hierarchy.index(zone.clearance_level_required)
	
	has_access = human_clearance_idx >= zone_clearance_idx
	
	return {
		"has_access": has_access,
		"human_clearance": human.clearance_level,
		"zone_clearance_required": zone.clearance_level_required,
		"reason": "Insufficient clearance level" if not has_access else "Access granted"
	}

