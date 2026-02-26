# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ResourceDeployment(Document):
	"""
	Resource Deployment DocType - Tracks deployment of resources to locations
	"""
	
	def validate(self):
		"""Validate resource deployment"""
		self.validate_no_double_booking()
		self.validate_resources_active()
	
	def validate_no_double_booking(self):
		"""Check for double-booking of resources"""
		for item in self.resources_table:
			if not item.resource:
				continue
			
			# Check for overlapping deployments
			existing = frappe.db.count(
				"Resource Deployment Item",
				filters={
					"parent": ["!=", self.name],
					"resource": item.resource,
					"parenttype": "Resource Deployment"
				}
			)
			
			if existing > 0:
				# Get the parent deployment to check dates
				parent_deployments = frappe.db.get_list(
					"Resource Deployment Item",
					filters={
						"resource": item.resource,
						"parenttype": "Resource Deployment"
					},
					fields=["parent"]
				)
				
				for parent_dep in parent_deployments:
					dep_doc = frappe.get_doc("Resource Deployment", parent_dep.parent)
					if dep_doc.deployment_date == self.deployment_date:
						frappe.throw(
							f"Resource {item.resource} is already deployed on {self.deployment_date}"
						)
	
	def validate_resources_active(self):
		"""Verify resources exist and are active"""
		for item in self.resources_table:
			if not item.resource:
				continue
			
			try:
				resource = frappe.get_doc("Security Resource", item.resource)
				if resource.status != "Active":
					frappe.throw(f"Resource {item.resource} is not active (Status: {resource.status})")
			except frappe.DoesNotExistError:
				frappe.throw(f"Resource {item.resource} does not exist")
	
	def on_submit(self):
		"""Actions on submit"""
		frappe.msgprint(
			f"Resource Deployment {self.name} submitted successfully. "
			f"{len(self.resources_table)} resources deployed to {self.location}"
		)
	
	def on_cancel(self):
		"""Actions on cancel"""
		frappe.msgprint(f"Resource Deployment {self.name} cancelled")

