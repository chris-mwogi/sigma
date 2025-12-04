# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BusinessProcessRegister(Document):
	def validate(self):
		"""Validate Business Process Register"""
		self.validate_process_owner()
		self.validate_parent_process()
	
	def validate_process_owner(self):
		"""Validate that process owner is a valid user"""
		if self.process_owner:
			if not frappe.db.exists("User", self.process_owner):
				frappe.throw(f"Process Owner '{self.process_owner}' is not a valid user")
	
	def validate_parent_process(self):
		"""Validate parent process logic"""
		if self.parent_process:
			if self.parent_process == self.name:
				frappe.throw("A process cannot be its own parent")
			
			# Check if parent is a group
			parent = frappe.get_doc("Business Process Register", self.parent_process)
			if not parent.is_group:
				frappe.throw(f"Parent process '{self.parent_process}' must be marked as a group")
	
	def on_update(self):
		"""Update linked information"""
		self.update_linked_risks()
		self.update_linked_controls()
		self.update_linked_compliance()
	
	def update_linked_risks(self):
		"""Update the list of linked risks"""
		# Find all Risk Registers that reference this business process
		linked_risks = frappe.db.sql("""
			SELECT name, risk_title
			FROM `tabRisk Register`
			WHERE notes LIKE %s
			AND docstatus < 2
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_risks:
			risk_list = [f"{r.name}: {r.risk_title}" for r in linked_risks]
			self.linked_risks = "\n".join(risk_list)
		else:
			self.linked_risks = ""
	
	def update_linked_controls(self):
		"""Update the list of linked controls"""
		# Find all Risk Controls that reference this business process
		linked_controls = frappe.db.sql("""
			SELECT name, control_name
			FROM `tabRisk Control`
			WHERE notes LIKE %s
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_controls:
			control_list = [f"{c.name}: {c.control_name}" for c in linked_controls]
			self.linked_controls = "\n".join(control_list)
		else:
			self.linked_controls = ""
	
	def update_linked_compliance(self):
		"""Update the list of linked compliance requirements"""
		# Find all Compliance Requirements that reference this business process
		linked_compliance = frappe.db.sql("""
			SELECT name, requirement_title
			FROM `tabCompliance Requirement`
			WHERE notes LIKE %s
		""", ('%' + self.name + '%',), as_dict=True)
		
		if linked_compliance:
			compliance_list = [f"{c.name}: {c.requirement_title}" for c in linked_compliance]
			self.linked_compliance = "\n".join(compliance_list)
		else:
			self.linked_compliance = ""
	
	def on_trash(self):
		"""Prevent deletion if process has children"""
		if self.is_group:
			children = frappe.db.count("Business Process Register", {"parent_process": self.name})
			if children > 0:
				frappe.throw(
					f"Cannot delete process '{self.name}' as it has {children} child process(es). "
					"Please delete or reassign the child processes first."
				)


@frappe.whitelist()
def get_process_summary(process_name):
	"""Get summary of business process"""
	process = frappe.get_doc("Business Process Register", process_name)
	
	# Count linked risks
	linked_risks_count = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabRisk Register`
		WHERE notes LIKE %s
		AND docstatus < 2
	""", ('%' + process_name + '%',), as_dict=True)
	
	# Count linked controls
	linked_controls_count = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabRisk Control`
		WHERE notes LIKE %s
	""", ('%' + process_name + '%',), as_dict=True)
	
	# Count child processes
	child_processes_count = frappe.db.count("Business Process Register", {"parent_process": process_name})
	
	return {
		"process_name": process.process_name,
		"process_category": process.process_category,
		"status": process.status,
		"criticality": process.criticality,
		"risk_exposure_level": process.risk_exposure_level,
		"linked_risks_count": linked_risks_count[0].count if linked_risks_count else 0,
		"linked_controls_count": linked_controls_count[0].count if linked_controls_count else 0,
		"child_processes_count": child_processes_count,
		"business_impact": process.business_impact,
		"customer_impact": process.customer_impact,
		"regulatory_impact": process.regulatory_impact
	}

