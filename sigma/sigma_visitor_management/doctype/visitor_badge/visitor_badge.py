# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class VisitorBadge(Document):
	"""
	Visitor Badge DocType
	
	Tracks physical badges issued to visitors
	"""
	
	def validate(self):
		"""Validate badge"""
		self.validate_badge_number()
		self.validate_visitor()
		self.validate_guard()
	
	def validate_badge_number(self):
		"""Validate badge number is unique"""
		existing = frappe.db.exists("Visitor Badge", {"badge_number": self.badge_number})
		if existing and existing != self.name:
			frappe.throw(f"Badge Number {self.badge_number} already exists")
	
	def validate_visitor(self):
		"""Validate visitor exists (using Human Profile)"""
		if not frappe.db.exists("Human Profile", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
	
	def validate_guard(self):
		"""Validate guard exists"""
		if not frappe.db.exists("Security Resource", self.issued_by_guard):
			frappe.throw(f"Guard {self.issued_by_guard} not found")
	
	def mark_returned(self, returned_by_guard, return_notes=""):
		"""Mark badge as returned"""
		self.status = "Returned"
		self.return_date = now_datetime()
		self.returned_by_guard = returned_by_guard
		self.return_notes = return_notes
		self.save(ignore_permissions=True)
	
	def mark_lost(self):
		"""Mark badge as lost"""
		self.status = "Lost"
		self.save(ignore_permissions=True)
	
	def mark_damaged(self):
		"""Mark badge as damaged"""
		self.status = "Damaged"
		self.save(ignore_permissions=True)
	
	@staticmethod
	def get_issued_badges(location=None):
		"""Get all issued badges"""
		filters = {"status": "Issued"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Badge",
			filters=filters,
			fields=["name", "badge_number", "visitor", "issue_date", "badge_type"],
			order_by="issue_date desc"
		)
	
	@staticmethod
	def get_unreturned_badges(location=None):
		"""Get unreturned badges"""
		filters = {"status": ["in", ["Issued", "Lost", "Damaged"]]}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Badge",
			filters=filters,
			fields=["name", "badge_number", "visitor", "issue_date", "status"],
			order_by="issue_date asc"
		)
	
	@staticmethod
	def get_lost_badges():
		"""Get lost badges"""
		return frappe.get_all(
			"Visitor Badge",
			filters={"status": "Lost"},
			fields=["name", "badge_number", "visitor", "location", "issue_date"],
			order_by="issue_date desc"
		)

