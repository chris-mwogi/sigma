# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


class RiskCategory(NestedSet):
	"""Risk Category DocType for hierarchical risk classification"""
	
	nsm_parent_field = "parent_category"
	
	def validate(self):
		"""Validate risk category"""
		self.validate_category_code()
		self.validate_parent_category()
	
	def validate_category_code(self):
		"""Ensure category code is uppercase and alphanumeric"""
		if self.category_code:
			self.category_code = self.category_code.upper().replace(" ", "_")
	
	def validate_parent_category(self):
		"""Validate parent category is a group"""
		if self.parent_category:
			parent = frappe.get_doc("Risk Category", self.parent_category)
			if not parent.is_group:
				frappe.throw(f"Parent category '{self.parent_category}' must be a group category")
	
	def on_update(self):
		"""Update nested set after changes"""
		NestedSet.on_update(self)
	
	def on_trash(self):
		"""Prevent deletion if category has linked risks"""
		# Check if category is used in Risk Register
		linked_risks = frappe.db.count("Risk Register", {"risk_category": self.name})
		if linked_risks > 0:
			frappe.throw(f"Cannot delete category '{self.name}' as it is linked to {linked_risks} risk(s)")
		
		NestedSet.on_trash(self, allow_root_deletion=True)

