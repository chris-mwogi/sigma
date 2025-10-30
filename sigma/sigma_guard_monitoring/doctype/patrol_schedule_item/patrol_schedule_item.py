# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatrolScheduleItem(Document):
	"""Child table for Patrol Schedule - defines checkpoints to visit"""
	
	def validate(self):
		"""Validate patrol schedule item"""
		self.validate_checkpoint_exists()
		self.set_checkpoint_name()

	def validate_checkpoint_exists(self):
		"""Ensure checkpoint exists"""
		if not frappe.db.exists("Patrol Checkpoint", self.checkpoint):
			frappe.throw(f"Patrol Checkpoint {self.checkpoint} does not exist")

	def set_checkpoint_name(self):
		"""Auto-populate checkpoint name from Patrol Checkpoint"""
		if self.checkpoint:
			checkpoint_doc = frappe.get_doc("Patrol Checkpoint", self.checkpoint)
			self.checkpoint_name = checkpoint_doc.checkpoint_name

