# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class ResourceCertification(Document):
	"""
	Resource Certification DocType - Tracks certifications for resources
	"""
	
	def validate(self):
		"""Validate resource certification"""
		self.validate_dates()
		self.validate_resource_exists()
		self.update_status()
	
	def validate_dates(self):
		"""Validate certification dates"""
		if self.issue_date > self.expiry_date:
			frappe.throw("Issue Date must be before Expiry Date")
	
	def validate_resource_exists(self):
		"""Verify resource exists"""
		if not frappe.db.exists("Security Resource", self.resource):
			frappe.throw(f"Resource {self.resource} does not exist")
	
	def update_status(self):
		"""Update certification status based on expiry date"""
		today = datetime.now().date()
		expiry = self.expiry_date
		
		if expiry < today:
			self.status = "Expired"
		elif expiry <= today + timedelta(days=30):
			self.status = "Expiring Soon"
		else:
			self.status = "Valid"
	
	def on_submit(self):
		"""Actions on submit"""
		frappe.msgprint(
			f"Resource Certification {self.name} submitted. "
			f"{self.certification_name} for {self.resource} expires on {self.expiry_date}"
		)
	
	def on_cancel(self):
		"""Actions on cancel"""
		frappe.msgprint(f"Resource Certification {self.name} cancelled")

