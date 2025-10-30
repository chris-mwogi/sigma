# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


class VisitorRegistration(Document):
	"""
	Visitor Registration DocType
	
	Pre-registration of expected visitors
	"""
	
	def validate(self):
		"""Validate registration"""
		self.validate_visitor()
		self.validate_dates()
		self.validate_host()
	
	def validate_visitor(self):
		"""Validate visitor exists"""
		if not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
	
	def validate_dates(self):
		"""Validate dates"""
		if self.expected_arrival_date < getdate():
			frappe.throw("Expected Arrival Date cannot be in the past")
	
	def validate_host(self):
		"""Validate host employee if specified"""
		if self.host_employee and not frappe.db.exists("Employee", self.host_employee):
			frappe.throw(f"Employee {self.host_employee} not found")
	
	def before_insert(self):
		"""Set default values"""
		self.registration_date = getdate()
		self.registered_by = frappe.session.user
	
	def on_update(self):
		"""Handle registration updates"""
		# Send notification if status changed
		if self.status == "Confirmed":
			self.send_confirmation_notification()
	
	def send_confirmation_notification(self):
		"""Send confirmation notification"""
		try:
			visitor = frappe.get_doc("Visitor", self.visitor)
			if visitor.email:
				frappe.sendmail(
					recipients=[visitor.email],
					subject=f"Visitor Registration Confirmed - {self.location}",
					message=f"""
					Dear {visitor.get_full_name()},
					
					Your visitor registration has been confirmed for {self.expected_arrival_date}.
					
					Location: {self.location}
					Expected Arrival Time: {self.expected_arrival_time}
					Purpose: {self.purpose_of_visit}
					
					Please arrive on time and check in at the reception.
					
					Best regards,
					Security Team
					"""
				)
		except Exception as e:
			frappe.log_error(f"Error sending confirmation notification: {str(e)}")
	
	@staticmethod
	def get_pending_registrations(location=None):
		"""Get pending registrations"""
		filters = {"status": "Pending"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Registration",
			filters=filters,
			fields=["name", "visitor", "expected_arrival_date", "expected_arrival_time", "location"],
			order_by="expected_arrival_date asc"
		)
	
	@staticmethod
	def get_today_registrations(location=None):
		"""Get registrations for today"""
		today = getdate()
		filters = {
			"expected_arrival_date": today,
			"status": ["in", ["Pending", "Confirmed"]]
		}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Registration",
			filters=filters,
			fields=["name", "visitor", "expected_arrival_time", "location", "status"],
			order_by="expected_arrival_time asc"
		)
	
	@staticmethod
	def get_overdue_registrations():
		"""Get registrations that haven't been checked in"""
		from frappe.utils import add_days, get_datetime
		
		yesterday = add_days(getdate(), -1)
		
		return frappe.get_all(
			"Visitor Registration",
			filters={
				"expected_arrival_date": ["<=", yesterday],
				"status": ["in", ["Pending", "Confirmed"]]
			},
			fields=["name", "visitor", "expected_arrival_date", "location"],
			order_by="expected_arrival_date asc"
		)

