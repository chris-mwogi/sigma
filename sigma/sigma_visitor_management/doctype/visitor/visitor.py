# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


class Visitor(Document):
	"""
	Visitor DocType - Master record for all visitor types
	
	Supports:
	- External Visitors
	- Inter-Station Staff
	- Contractors
	- Vendors
	"""
	
	def validate(self):
		"""Validate visitor record"""
		self.validate_visitor_type()
		self.validate_identification()
		self.check_blacklist()
	
	def validate_visitor_type(self):
		"""Validate visitor type specific fields"""
		if self.visitor_type == "Inter-Station Staff":
			if not self.company_name:
				frappe.throw("Company/Organization Name is required for Inter-Station Staff")
		
		if self.visitor_type == "Contractor":
			if not self.company_name:
				frappe.throw("Company/Organization Name is required for Contractors")
		
		if self.visitor_type == "Vendor":
			if not self.company_name:
				frappe.throw("Company/Organization Name is required for Vendors")
	
	def validate_identification(self):
		"""Validate identification details"""
		if self.identification_type and not self.identification_number:
			frappe.throw("Identification Number is required when Identification Type is specified")
	
	def check_blacklist(self):
		"""Check if visitor is blacklisted"""
		if self.is_blacklisted and not self.blacklist_reason:
			frappe.throw("Blacklist Reason is required when marking visitor as blacklisted")
	
	def before_insert(self):
		"""Set creation details"""
		if not self.created_by_guard:
			self.created_by_guard = frappe.session.user
		
		if not self.created_at_location:
			# Try to get location from user's current location context
			# This would be set by the guard app
			pass
	
	def on_update(self):
		"""Handle visitor updates"""
		# Log visitor updates for audit trail
		self.log_visitor_activity("Updated")
	
	def log_visitor_activity(self, activity_type):
		"""Log visitor activity for audit trail"""
		try:
			frappe.get_doc({
				"doctype": "Visitor Access Log",
				"visitor": self.name,
				"activity_type": activity_type,
				"timestamp": now_datetime(),
				"location": self.created_at_location,
				"guard": frappe.session.user
			}).insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error logging visitor activity: {str(e)}")
	
	def get_full_name(self):
		"""Get visitor's full name"""
		return f"{self.first_name} {self.last_name}".strip()
	
	def get_visitor_history(self, location=None):
		"""Get visitor's check-in/check-out history"""
		filters = {"visitor": self.name}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Check-In/Check-Out",
			filters=filters,
			fields=["name", "check_in_time", "check_out_time", "location", "guard", "status"],
			order_by="check_in_time desc"
		)
	
	def get_active_sessions(self):
		"""Get active check-in sessions for this visitor"""
		return frappe.get_all(
			"Visitor Check-In/Check-Out",
			filters={
				"visitor": self.name,
				"status": "Checked In",
				"docstatus": 1
			},
			fields=["name", "check_in_time", "location", "guard"]
		)
	
	def get_vms_events(self):
		"""Get VMS events linked to this visitor"""
		return frappe.get_all(
			"VMS Event",
			filters={"visitor": self.name},
			fields=["name", "event_type", "event_time", "location", "vms_platform", "camera_id"],
			order_by="event_time desc"
		)
	
	@staticmethod
	def get_visitors_by_type(visitor_type, location=None):
		"""Get all visitors of a specific type"""
		filters = {"visitor_type": visitor_type, "status": "Active"}
		if location:
			filters["created_at_location"] = location
		
		return frappe.get_all(
			"Visitor",
			filters=filters,
			fields=["name", "first_name", "last_name", "email", "phone", "company_name"],
			order_by="creation desc"
		)
	
	@staticmethod
	def get_blacklisted_visitors():
		"""Get all blacklisted visitors"""
		return frappe.get_all(
			"Visitor",
			filters={"is_blacklisted": 1},
			fields=["name", "first_name", "last_name", "blacklist_reason", "creation"],
			order_by="creation desc"
		)
	
	@staticmethod
	def search_visitor(search_term):
		"""Search for visitors by name, email, or phone"""
		return frappe.get_all(
			"Visitor",
			filters=[
				["first_name", "like", f"%{search_term}%"],
				["last_name", "like", f"%{search_term}%"],
				["email", "like", f"%{search_term}%"],
				["phone", "like", f"%{search_term}%"]
			],
			fields=["name", "first_name", "last_name", "email", "phone", "visitor_type"],
			limit_page_length=20
		)

