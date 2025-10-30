# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EvacuationAssignmentItem(Document):
	"""Child table for Emergency Evacuation Tracking - tracks individual visitor evacuations"""
	
	def validate(self):
		"""Validate evacuation assignment item"""
		self.validate_visitor_exists()
		self.validate_guard_exists()
		self.set_visitor_name()
		self.set_guard_name()

	def validate_visitor_exists(self):
		"""Ensure visitor exists"""
		if not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} does not exist")

	def validate_guard_exists(self):
		"""Ensure guard exists"""
		if not frappe.db.exists("Security Resource", self.guard):
			frappe.throw(f"Security Resource {self.guard} does not exist")

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

