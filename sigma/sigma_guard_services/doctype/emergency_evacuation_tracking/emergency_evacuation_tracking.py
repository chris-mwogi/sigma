# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class EmergencyEvacuationTracking(Document):
	"""
	Tracks emergency evacuations and visitor-guard assignments during emergencies.
	
	Manages evacuation status, tracks which visitors have been evacuated,
	and ensures all assigned visitors are accounted for.
	"""

	def validate(self):
		"""Validate evacuation tracking"""
		self.validate_location()
		self.validate_times()
		self.calculate_evacuation_stats()

	def validate_location(self):
		"""Ensure location exists"""
		if not frappe.db.exists("Location", self.location):
			frappe.throw(f"Location {self.location} does not exist")

	def validate_times(self):
		"""Validate evacuation times"""
		if self.evacuation_end_time and self.evacuation_start_time:
			if self.evacuation_end_time < self.evacuation_start_time:
				frappe.throw("Evacuation end time cannot be before start time")

	def calculate_evacuation_stats(self):
		"""Calculate evacuation statistics"""
		if self.assigned_visitors:
			self.total_visitors = len(self.assigned_visitors)
			self.total_evacuated = sum(1 for item in self.assigned_visitors if item.evacuated)

	def on_submit(self):
		"""Send evacuation notifications"""
		self.send_evacuation_alerts()
		self.update_visitor_assignments()

	def send_evacuation_alerts(self):
		"""Send evacuation alerts to all assigned guards"""
		guards = set()
		for item in self.assigned_visitors:
			if item.guard:
				guards.add(item.guard)
		
		for guard_id in guards:
			guard_user = frappe.db.get_value("User", {"security_resource": guard_id}, "email")
			if guard_user:
				subject = f"EMERGENCY EVACUATION ALERT - {self.location}"
				message = f"""
				<p><strong>EMERGENCY EVACUATION IN PROGRESS</strong></p>
				<p>Location: {self.location}</p>
				<p>Evacuation Type: {self.evacuation_type}</p>
				<p>Start Time: {self.evacuation_start_time}</p>
				<p>Please proceed with evacuation of assigned visitors immediately.</p>
				"""
				
				frappe.sendmail(
					recipients=[guard_user],
					subject=subject,
					message=message
				)

	def update_visitor_assignments(self):
		"""Update visitor-guard assignments for evacuation"""
		for item in self.assigned_visitors:
			if item.visitor_guard_assignment:
				assignment = frappe.get_doc("Visitor Guard Assignment", item.visitor_guard_assignment)
				assignment.evacuation_responsible = 1
				assignment.db_update()

	def mark_visitor_evacuated(self, visitor_guard_assignment_id):
		"""Mark a visitor as evacuated"""
		for item in self.assigned_visitors:
			if item.visitor_guard_assignment == visitor_guard_assignment_id:
				item.evacuated = 1
				item.evacuation_time = datetime.now()
				self.db_update()
				break

	def complete_evacuation(self):
		"""Mark evacuation as completed"""
		self.status = "Completed"
		self.evacuation_end_time = datetime.now()
		self.calculate_evacuation_stats()
		self.db_update()

	def get_evacuation_report(self):
		"""Generate evacuation report"""
		report = {
			"location": self.location,
			"evacuation_type": self.evacuation_type,
			"start_time": str(self.evacuation_start_time),
			"end_time": str(self.evacuation_end_time) if self.evacuation_end_time else None,
			"total_visitors": self.total_visitors,
			"total_evacuated": self.total_evacuated,
			"evacuation_percentage": (self.total_evacuated / self.total_visitors * 100) if self.total_visitors > 0 else 0,
			"status": self.status,
			"assigned_visitors": []
		}
		
		for item in self.assigned_visitors:
			report["assigned_visitors"].append({
				"visitor": item.visitor,
				"guard": item.guard,
				"evacuated": item.evacuated,
				"evacuation_time": str(item.evacuation_time) if item.evacuation_time else None
			})
		
		return report

