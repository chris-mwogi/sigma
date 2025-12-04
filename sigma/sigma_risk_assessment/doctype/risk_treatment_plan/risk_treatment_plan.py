# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, flt


class RiskTreatmentPlan(Document):
	def validate(self):
		"""Validate Risk Treatment Plan"""
		self.validate_linked_risk()
		self.validate_dates()
		self.calculate_actual_cost()
		self.calculate_budget_variance()
		self.update_progress()
		self.update_action_status()
	
	def validate_linked_risk(self):
		"""Validate that linked risk exists and is submitted"""
		if self.linked_risk:
			if not frappe.db.exists("Risk Register", self.linked_risk):
				frappe.throw(f"Risk Register '{self.linked_risk}' does not exist")
			
			risk = frappe.get_doc("Risk Register", self.linked_risk)
			if risk.docstatus != 1:
				frappe.throw(f"Risk Register '{self.linked_risk}' must be submitted before creating a treatment plan")
	
	def validate_dates(self):
		"""Validate date logic"""
		if self.start_date and self.target_completion_date:
			if getdate(self.target_completion_date) < getdate(self.start_date):
				frappe.throw("Target Completion Date cannot be before Start Date")
		
		if self.actual_completion_date and self.start_date:
			if getdate(self.actual_completion_date) < getdate(self.start_date):
				frappe.throw("Actual Completion Date cannot be before Start Date")
	
	def calculate_actual_cost(self):
		"""Calculate total actual cost from treatment actions"""
		total_cost = 0
		for action in self.treatment_actions:
			if action.actual_cost:
				total_cost += flt(action.actual_cost)
		self.actual_cost = total_cost
	
	def calculate_budget_variance(self):
		"""Calculate budget variance"""
		if self.estimated_budget and self.actual_cost:
			self.budget_variance = flt(self.actual_cost) - flt(self.estimated_budget)
			if self.estimated_budget > 0:
				self.budget_variance_percentage = (self.budget_variance / self.estimated_budget) * 100
		else:
			self.budget_variance = 0
			self.budget_variance_percentage = 0
	
	def update_progress(self):
		"""Update progress based on completed actions"""
		if not self.treatment_actions:
			self.progress_percentage = 0
			return
		
		total_actions = len(self.treatment_actions)
		completed_actions = sum(1 for action in self.treatment_actions if action.status == "Completed")
		
		if total_actions > 0:
			self.progress_percentage = (completed_actions / total_actions) * 100
	
	def update_action_status(self):
		"""Update action status based on due dates"""
		today = getdate()
		for action in self.treatment_actions:
			if action.status not in ["Completed", "Cancelled"]:
				if action.due_date and getdate(action.due_date) < today:
					action.status = "Overdue"
	
	def on_submit(self):
		"""Actions on submit"""
		self.plan_status = "Approved"
		self.create_notifications()
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.plan_status = "Cancelled"
	
	def before_save(self):
		"""Update status based on progress"""
		if self.progress_percentage == 100 and self.plan_status != "Completed":
			self.plan_status = "Completed"
			self.actual_completion_date = getdate()
		elif self.progress_percentage > 0 and self.progress_percentage < 100:
			if self.plan_status not in ["In Progress", "On Hold"]:
				self.plan_status = "In Progress"
	
	def create_notifications(self):
		"""Create notifications for assigned users"""
		for action in self.treatment_actions:
			if action.assigned_to:
				# Create a notification for the assigned user
				notification = frappe.new_doc("Notification Log")
				notification.subject = f"Risk Treatment Action Assigned: {self.plan_title}"
				notification.for_user = action.assigned_to
				notification.type = "Alert"
				notification.document_type = "Risk Treatment Plan"
				notification.document_name = self.name
				notification.email_content = f"""
					<p>You have been assigned a risk treatment action:</p>
					<p><strong>Plan:</strong> {self.plan_title}</p>
					<p><strong>Action:</strong> {action.action_description}</p>
					<p><strong>Due Date:</strong> {action.due_date}</p>
					<p><strong>Priority:</strong> {self.priority}</p>
				"""
				notification.insert(ignore_permissions=True)


@frappe.whitelist()
def get_treatment_plan_summary(plan_name):
	"""Get summary of treatment plan"""
	plan = frappe.get_doc("Risk Treatment Plan", plan_name)
	
	total_actions = len(plan.treatment_actions)
	completed_actions = sum(1 for action in plan.treatment_actions if action.status == "Completed")
	overdue_actions = sum(1 for action in plan.treatment_actions if action.status == "Overdue")
	
	return {
		"plan_title": plan.plan_title,
		"plan_status": plan.plan_status,
		"progress_percentage": plan.progress_percentage,
		"total_actions": total_actions,
		"completed_actions": completed_actions,
		"overdue_actions": overdue_actions,
		"estimated_budget": plan.estimated_budget,
		"actual_cost": plan.actual_cost,
		"budget_variance": plan.budget_variance,
		"budget_variance_percentage": plan.budget_variance_percentage,
		"effectiveness_rating": plan.effectiveness_rating
	}

