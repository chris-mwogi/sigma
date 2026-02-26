# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class VisitorAccessLog(Document):
	"""
	Visitor Access Log DocType
	
	Comprehensive audit trail for all visitor movements and access events
	"""
	
	def validate(self):
		"""Validate access log entry"""
		self.validate_visitor()
		self.validate_timestamp()
	
	def validate_visitor(self):
		"""Validate visitor exists (using Human Profile)"""
		if not frappe.db.exists("Human Profile", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
	
	def validate_timestamp(self):
		"""Validate timestamp is not in future"""
		if self.timestamp > frappe.utils.now_datetime():
			frappe.throw("Timestamp cannot be in the future")
	
	@staticmethod
	def get_visitor_access_history(visitor_id, location=None, days=30):
		"""Get visitor's access history"""
		from frappe.utils import add_days, get_datetime
		
		filters = {"visitor": visitor_id}
		if location:
			filters["location"] = location
		
		# Add date filter for last N days
		start_date = add_days(get_datetime(), -days)
		filters["timestamp"] = [">=", start_date]
		
		return frappe.get_all(
			"Visitor Access Log",
			filters=filters,
			fields=["name", "activity_type", "timestamp", "location", "guard", "access_granted"],
			order_by="timestamp desc"
		)
	
	@staticmethod
	def get_location_access_log(location, date=None):
		"""Get access log for a location"""
		filters = {"location": location}
		if date:
			filters["timestamp"] = [">=", f"{date} 00:00:00"]
			filters["timestamp"] = ["<=", f"{date} 23:59:59"]
		
		return frappe.get_all(
			"Visitor Access Log",
			filters=filters,
			fields=["name", "visitor", "activity_type", "timestamp", "guard", "access_granted"],
			order_by="timestamp desc"
		)
	
	@staticmethod
	def get_denied_access_log(location=None, days=7):
		"""Get denied access attempts"""
		from frappe.utils import add_days, get_datetime
		
		filters = {"access_granted": 0}
		if location:
			filters["location"] = location
		
		start_date = add_days(get_datetime(), -days)
		filters["timestamp"] = [">=", start_date]
		
		return frappe.get_all(
			"Visitor Access Log",
			filters=filters,
			fields=["name", "visitor", "timestamp", "location", "access_reason"],
			order_by="timestamp desc"
		)
	
	@staticmethod
	def get_restricted_area_access(location=None):
		"""Get restricted area access attempts"""
		filters = {"activity_type": "Restricted Area Access"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Access Log",
			filters=filters,
			fields=["name", "visitor", "timestamp", "location", "guard", "access_granted"],
			order_by="timestamp desc"
		)

