# -*- coding: utf-8 -*-
# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class VisitorType(Document):
	"""
	Visitor Type Master
	Defines visitor categories with access templates and compliance requirements
	ISO 27001 A.11 - Physical Access Control
	"""
	
	def validate(self):
		"""Validate visitor type configuration"""
		if self.risk_weight and (self.risk_weight < 1 or self.risk_weight > 5):
			frappe.throw("Risk Weight must be between 1 and 5")
	
	def before_save(self):
		"""Set default values"""
		if not self.risk_weight:
			self.risk_weight = 1

