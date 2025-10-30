# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
from datetime import datetime, timedelta


class VisitorCheckinCheckout(Document):
	"""
	Visitor Checkin Checkout DocType

	Tracks visitor entry and exit from locations
	Supports multiple check-in methods:
	- Guard-Initiated
	- Pre-Registration
	- Self-Service Kiosk
	- VMS Auto-Detection
	"""
	
	def validate(self):
		"""Validate check-in/check-out record"""
		self.validate_visitor()
		self.validate_times()
		self.validate_guard()
		self.check_blacklist()
	
	def validate_visitor(self):
		"""Validate visitor exists and is not blacklisted"""
		if not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
		
		visitor = frappe.get_doc("Visitor", self.visitor)
		if visitor.is_blacklisted:
			frappe.throw(f"Visitor {self.visitor} is blacklisted: {visitor.blacklist_reason}")
	
	def validate_times(self):
		"""Validate check-in and check-out times"""
		if self.check_out_time and self.check_in_time >= self.check_out_time:
			frappe.throw("Check-Out Time must be after Check-In Time")
		
		# Check-in time should not be in the future
		if self.check_in_time > now_datetime():
			frappe.throw("Check-In Time cannot be in the future")
	
	def validate_guard(self):
		"""Validate guard exists"""
		if not frappe.db.exists("Security Resource", self.guard):
			frappe.throw(f"Guard {self.guard} not found")
	
	def check_blacklist(self):
		"""Check if visitor is blacklisted"""
		visitor = frappe.get_doc("Visitor", self.visitor)
		if visitor.is_blacklisted:
			frappe.throw(f"Cannot check in blacklisted visitor: {visitor.blacklist_reason}")
	
	def before_insert(self):
		"""Set default values before insert"""
		if not self.check_in_time:
			self.check_in_time = now_datetime()
		
		if not self.check_in_method:
			self.check_in_method = "Guard-Initiated"
	
	def on_update(self):
		"""Handle check-in/check-out updates"""
		self.update_duration()
		self.create_access_log()
	
	def update_duration(self):
		"""Calculate duration in minutes"""
		if self.check_out_time:
			check_in = get_datetime(self.check_in_time)
			check_out = get_datetime(self.check_out_time)
			duration = (check_out - check_in).total_seconds() / 60
			self.duration_minutes = int(duration)
	
	def create_access_log(self):
		"""Create access log entry"""
		try:
			log_entry = frappe.get_doc({
				"doctype": "Visitor Access Log",
				"visitor": self.visitor,
				"location": self.location,
				"activity_type": "Check-In" if self.status == "Checked In" else "Check-Out",
				"timestamp": self.check_in_time if self.status == "Checked In" else self.check_out_time,
				"guard": self.guard,
				"check_in_checkout_record": self.name
			})
			log_entry.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error creating access log: {str(e)}")
	
	def mark_checked_out(self):
		"""Mark visitor as checked out"""
		self.check_out_time = now_datetime()
		self.status = "Checked Out"
		self.update_duration()
		self.save(ignore_permissions=True)
	
	def get_visitor_details(self):
		"""Get visitor details"""
		return frappe.get_doc("Visitor", self.visitor)
	
	def get_guard_details(self):
		"""Get guard details"""
		return frappe.get_doc("Security Resource", self.guard)
	
	@staticmethod
	def get_active_visitors(location=None):
		"""Get all currently checked-in visitors"""
		filters = {"status": "Checked In", "docstatus": 1}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Checkin Checkout",
			filters=filters,
			fields=["name", "visitor", "location", "check_in_time", "guard", "escort_guard"],
			order_by="check_in_time desc"
		)
	
	@staticmethod
	def get_visitor_sessions(visitor_id, location=None):
		"""Get all check-in/check-out sessions for a visitor"""
		filters = {"visitor": visitor_id}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Checkin Checkout",
			filters=filters,
			fields=["name", "check_in_time", "check_out_time", "location", "status", "duration_minutes"],
			order_by="check_in_time desc"
		)
	
	@staticmethod
	def get_location_visitors(location, date=None):
		"""Get all visitors at a location on a specific date"""
		filters = {"location": location}
		if date:
			filters["check_in_time"] = [">=", f"{date} 00:00:00"]
			filters["check_in_time"] = ["<=", f"{date} 23:59:59"]
		
		return frappe.get_all(
			"Visitor Checkin Checkout",
			filters=filters,
			fields=["name", "visitor", "check_in_time", "check_out_time", "status", "guard"],
			order_by="check_in_time desc"
		)
	
	@staticmethod
	def get_unchecked_out_visitors(location=None):
		"""Get visitors who haven't checked out"""
		filters = {"status": "Checked In"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Checkin Checkout",
			filters=filters,
			fields=["name", "visitor", "check_in_time", "location", "guard"],
			order_by="check_in_time asc"
		)

