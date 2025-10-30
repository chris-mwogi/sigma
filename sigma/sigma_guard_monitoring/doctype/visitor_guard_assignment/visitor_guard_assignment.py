# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class VisitorGuardAssignment(Document):
	"""
	Links visitors to security guards for escort and tracking.
	
	Manages visitor-guard assignments, tracks escort status, and handles
	emergency evacuation responsibilities.
	"""

	def validate(self):
		"""Validate visitor-guard assignment"""
		self.validate_visitor()
		self.validate_guard()
		self.validate_times()
		self.set_visitor_name()
		self.set_guard_name()

	def validate_visitor(self):
		"""Ensure visitor exists"""
		if not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} does not exist")

	def validate_guard(self):
		"""Ensure guard is a valid security resource"""
		if not frappe.db.exists("Security Resource", self.guard):
			frappe.throw(f"Security Resource {self.guard} does not exist")
		
		guard = frappe.get_doc("Security Resource", self.guard)
		if guard.resource_type != "Guard":
			frappe.throw("Assigned resource must be a Guard")

	def validate_times(self):
		"""Validate assignment and check-out times"""
		if self.check_out_time and self.assignment_time:
			if self.check_out_time < self.assignment_time:
				frappe.throw("Check-out time cannot be before assignment time")

	def set_visitor_name(self):
		"""Auto-populate visitor name"""
		if self.visitor:
			visitor = frappe.get_doc("Visitor", self.visitor)
			self.visitor_name = visitor.name

	def set_guard_name(self):
		"""Auto-populate guard name"""
		if self.guard:
			guard = frappe.get_doc("Security Resource", self.guard)
			self.guard_name = guard.name

	def on_submit(self):
		"""Send notification to assigned guard"""
		self.notify_guard()

	def notify_guard(self):
		"""Send notification to guard about visitor assignment"""
		guard = frappe.get_doc("Security Resource", self.guard)
		visitor = frappe.get_doc("Visitor", self.visitor)
		
		# Get guard's user email
		guard_user = frappe.db.get_value("User", {"security_resource": self.guard}, "email")
		
		if guard_user:
			subject = f"Visitor Assignment: {visitor.name}"
			message = f"""
			<p>You have been assigned to escort a visitor:</p>
			<ul>
				<li>Visitor: {visitor.name}</li>
				<li>Assignment ID: {self.name}</li>
				<li>Assignment Time: {self.assignment_time}</li>
				<li>Location: {self.location or 'Not specified'}</li>
			</ul>
			<p>Please acknowledge receipt and begin escort duties.</p>
			"""
			
			frappe.sendmail(
				recipients=[guard_user],
				subject=subject,
				message=message
			)

	def mark_escorting(self):
		"""Mark assignment as escorting"""
		self.status = "Escorting"
		self.db_update()

	def mark_checked_out(self):
		"""Mark visitor as checked out"""
		self.status = "Checked Out"
		self.check_out_time = datetime.now()
		self.db_update()

	def mark_evacuation_completed(self):
		"""Mark evacuation as completed"""
		self.evacuation_completed = 1
		self.evacuation_time = datetime.now()
		self.db_update()

	def get_evacuation_status(self):
		"""Get evacuation status for this assignment"""
		return {
			"responsible": self.evacuation_responsible,
			"completed": self.evacuation_completed,
			"evacuation_time": self.evacuation_time
		}

