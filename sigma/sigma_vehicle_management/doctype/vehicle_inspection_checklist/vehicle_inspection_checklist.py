# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleInspectionChecklist(Document):
	"""
	Vehicle Inspection Checklist
	Records vehicle inspection results
	OSHA 29 CFR 1910 - Occupational Safety and Health Standards
	"""
	
	def validate(self):
		"""Validate inspection checklist"""
		self.set_make_model()
		self.validate_inspection_results()
		self.calculate_overall_status()
	
	def set_make_model(self):
		"""Set make and model from vehicle"""
		if self.license_plate:
			vehicle = frappe.get_doc("Vehicle", self.license_plate)
			self.make_model = f"{vehicle.make or ''} {vehicle.model or ''}".strip()
	
	def validate_inspection_results(self):
		"""Validate inspection results"""
		if not self.inspection_results:
			frappe.msgprint("No inspection results recorded", indicator="orange", alert=True)
	
	def calculate_overall_status(self):
		"""Calculate overall inspection status based on results"""
		if not self.inspection_results:
			self.overall_status = "Pending"
			return
		
		# Check if any mandatory items failed
		failed_mandatory = False
		for item in self.inspection_results:
			if item.is_mandatory and item.result == "Fail":
				failed_mandatory = True
				break
		
		if failed_mandatory:
			self.inspection_result = "Fail"
			self.overall_status = "Failed"
		else:
			# Check if all items passed
			all_passed = all(item.result == "Pass" for item in self.inspection_results)
			if all_passed:
				self.inspection_result = "Pass"
				self.overall_status = "Completed"
			else:
				self.inspection_result = "Conditional Pass"
				self.overall_status = "Completed"
	
	def after_insert(self):
		"""Actions after inspection is created"""
		if self.inspection_result == "Fail":
			self.notify_security_failed_inspection()
	
	def on_update(self):
		"""Actions after inspection is updated"""
		# Check if inspection result changed to Fail
		if self.has_value_changed("inspection_result") and self.inspection_result == "Fail":
			self.notify_security_failed_inspection()
	
	def notify_security_failed_inspection(self):
		"""Notify security of failed inspection"""
		try:
			security_role = frappe.get_all("Has Role",
				filters={"role": "Security Manager"},
				fields=["parent"]
			)
			
			if security_role:
				recipients = [frappe.db.get_value("User", r.parent, "email") 
							 for r in security_role 
							 if frappe.db.get_value("User", r.parent, "email")]
				
				if recipients:
					frappe.sendmail(
						recipients=recipients,
						subject=f"⚠️ Vehicle Inspection Failed: {self.license_plate}",
						message=f"""
						<h3>Vehicle Inspection Failed</h3>
						<p><strong>License Plate:</strong> {self.license_plate}</p>
						<p><strong>Vehicle:</strong> {self.make_model}</p>
						<p><strong>Inspection Date:</strong> {self.inspection_date}</p>
						<p><strong>Inspector:</strong> {self.inspector}</p>
						<p><strong>Result:</strong> {self.inspection_result}</p>
						<p><strong>Dangerous Goods:</strong> {'Yes' if self.dangerous_goods_present else 'No'}</p>
						<p><strong>Action Required:</strong> {self.action_required or 'Not specified'}</p>
						<p><a href="{frappe.utils.get_url()}/app/vehicle-inspection-checklist/{self.name}">View Inspection Record</a></p>
						""",
						reference_doctype="Vehicle Inspection Checklist",
						reference_name=self.name
					)
		except Exception as e:
			# Log error but don't fail the transaction
			frappe.log_error(f"Failed to send failed inspection notification: {str(e)}", 
							"Failed Inspection Notification Error")


@frappe.whitelist()
def load_inspection_template(template_name):
	"""Load inspection items from template"""
	template = frappe.get_doc("Vehicle Inspection Template", template_name)
	items = []
	
	for item in template.inspection_items:
		items.append({
			"item_name": item.item_name,
			"description": item.description,
			"is_mandatory": item.is_mandatory,
			"inspection_type": item.inspection_type,
			"pass_criteria": item.pass_criteria,
			"result": "",
			"remarks": ""
		})
	
	return items

