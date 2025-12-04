# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, nowdate, now_datetime


class ResourceRequisition(Document):
	"""
	Resource Requisition DocType - Manages department requests for security resources
	"""
	
	def validate(self):
		"""Validate resource requisition before save"""
		self.validate_dates()
		self.calculate_duration()
		self.validate_resources()
		self.update_status()
	
	def validate_dates(self):
		"""Validate start and end dates"""
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("Start Date cannot be after End Date")
			
			# Warn if start date is in the past
			if self.start_date < nowdate() and self.docstatus == 0:
				frappe.msgprint("Warning: Start Date is in the past", indicator="orange")
	
	def calculate_duration(self):
		"""Calculate duration in days"""
		if self.start_date and self.end_date:
			self.duration_days = date_diff(self.end_date, self.start_date) + 1
	
	def validate_resources(self):
		"""Validate resource requirements"""
		if not self.resources_table or len(self.resources_table) == 0:
			frappe.throw("At least one resource must be specified")
		
		# Validate resource counts
		for item in self.resources_table:
			if item.required_count <= 0:
				frappe.throw(f"Required count for {item.resource_type} must be greater than 0")
	
	def update_status(self):
		"""Update status based on approval status"""
		if self.approval_status == "Approved" and self.status == "Pending Approval":
			self.status = "Approved"
		elif self.approval_status == "Rejected":
			self.status = "Rejected"
	
	def on_submit(self):
		"""Actions on submit"""
		if self.status == "Draft":
			self.status = "Pending Approval"
			self.save()
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.status = "Cancelled"
		self.save()


@frappe.whitelist()
def approve_requisition(requisition_name):
	"""Approve a resource requisition"""
	doc = frappe.get_doc("Resource Requisition", requisition_name)
	
	# Check permissions
	if not frappe.has_permission("Resource Requisition", "write", doc):
		frappe.throw("You do not have permission to approve this requisition")
	
	doc.approval_status = "Approved"
	doc.approved_by = frappe.session.user
	doc.approval_date = now_datetime()
	doc.status = "Approved"
	doc.save()
	
	frappe.msgprint(f"Requisition {requisition_name} has been approved", indicator="green")
	return doc


@frappe.whitelist()
def reject_requisition(requisition_name, reason):
	"""Reject a resource requisition"""
	doc = frappe.get_doc("Resource Requisition", requisition_name)
	
	# Check permissions
	if not frappe.has_permission("Resource Requisition", "write", doc):
		frappe.throw("You do not have permission to reject this requisition")
	
	doc.approval_status = "Rejected"
	doc.approved_by = frappe.session.user
	doc.approval_date = now_datetime()
	doc.rejected_reason = reason
	doc.status = "Rejected"
	doc.save()
	
	frappe.msgprint(f"Requisition {requisition_name} has been rejected", indicator="red")
	return doc

