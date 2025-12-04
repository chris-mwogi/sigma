# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_months, add_years, getdate

class AssetAudit(Document):
	"""
	Asset Audit - ISO 55000 compliant audit and verification
	"""
	
	def validate(self):
		"""Validate audit entry"""
		self.calculate_audit_summary()
		self.determine_next_audit_date()
	
	def calculate_audit_summary(self):
		"""Calculate audit summary statistics from findings"""
		if not self.audit_findings:
			return
		
		# Initialize counters
		total_checks = 0
		passed_checks = 0
		failed_checks = 0
		critical_findings = 0
		major_findings = 0
		minor_findings = 0
		observations = 0
		
		# Count findings
		for finding in self.audit_findings:
			total_checks += 1
			
			if finding.check_result == "Pass":
				passed_checks += 1
			elif finding.check_result == "Fail":
				failed_checks += 1
				
				# Count by severity
				if finding.severity == "Critical":
					critical_findings += 1
				elif finding.severity == "Major":
					major_findings += 1
				elif finding.severity == "Minor":
					minor_findings += 1
			elif finding.check_result == "Observation":
				observations += 1
		
		# Update summary fields
		self.total_checks = total_checks
		self.passed_checks = passed_checks
		self.failed_checks = failed_checks
		self.critical_findings = critical_findings
		self.major_findings = major_findings
		self.minor_findings = minor_findings
		self.observations = observations
		
		# Calculate compliance percentage
		if total_checks > 0:
			self.compliance_percentage = (passed_checks / total_checks) * 100
		else:
			self.compliance_percentage = 0
		
		# Set corrective actions required if there are critical or major findings
		if critical_findings > 0 or major_findings > 0:
			self.corrective_actions_required = 1
	
	def determine_next_audit_date(self):
		"""Determine next audit date based on audit type and criticality"""
		if not self.next_audit_date and self.audit_status == "Completed":
			# Default audit frequencies based on criticality
			if self.criticality_rating == "Critical":
				# Critical assets: quarterly audits
				self.next_audit_date = add_months(self.audit_date, 3)
			elif self.criticality_rating == "High":
				# High criticality: semi-annual audits
				self.next_audit_date = add_months(self.audit_date, 6)
			else:
				# Medium/Low criticality: annual audits
				self.next_audit_date = add_years(self.audit_date, 1)
	
	def on_submit(self):
		"""Actions on submission"""
		# Update asset last audit date
		if self.asset:
			asset = frappe.get_doc("Asset", self.asset)
			asset.last_audit_date = self.audit_date
			asset.save(ignore_permissions=True)
			frappe.msgprint(f"✅ Asset last audit date updated to {self.audit_date}", indicator="green")
		
		# Create work order for corrective actions if required
		if self.corrective_actions_required and self.critical_findings > 0:
			self.create_corrective_action_work_order()
	
	def create_corrective_action_work_order(self):
		"""Create work order for critical corrective actions"""
		work_order = frappe.new_doc("Asset Work Order")
		work_order.asset = self.asset
		work_order.work_order_type = "Corrective Maintenance"
		work_order.priority = "Critical" if self.critical_findings > 0 else "High"
		work_order.work_description = f"""
		<p><strong>Corrective Actions Required from Audit: {self.name}</strong></p>
		<p><strong>Audit Date:</strong> {self.audit_date}</p>
		<p><strong>Findings Summary:</strong></p>
		<ul>
			<li>Critical Findings: {self.critical_findings}</li>
			<li>Major Findings: {self.major_findings}</li>
			<li>Minor Findings: {self.minor_findings}</li>
		</ul>
		<p><strong>Recommendations:</strong></p>
		{self.recommendations or '<p>See audit findings for details</p>'}
		"""
		work_order.scheduled_start_date = nowdate()
		work_order.scheduled_end_date = self.corrective_action_deadline
		work_order.assigned_to = self.corrective_action_owner
		work_order.workflow_state = "Scheduled"
		work_order.insert(ignore_permissions=True)
		
		frappe.msgprint(
			f"✅ Work Order {work_order.name} created for corrective actions",
			indicator="green",
			alert=True
		)


@frappe.whitelist()
def get_overdue_audits():
	"""Get all assets with overdue audits"""
	today = getdate(nowdate())
	
	# Get all assets with next audit date in the past
	audits = frappe.db.sql("""
		SELECT 
			a.name as asset,
			a.asset_name,
			a.asset_category_sigma,
			a.criticality_rating,
			MAX(aa.audit_date) as last_audit_date,
			MAX(aa.next_audit_date) as next_audit_date
		FROM `tabAsset` a
		LEFT JOIN `tabAsset Audit` aa ON aa.asset = a.name AND aa.docstatus = 1
		WHERE a.docstatus < 2
		GROUP BY a.name
		HAVING next_audit_date < %s OR next_audit_date IS NULL
		ORDER BY a.criticality_rating DESC, next_audit_date ASC
	""", (today,), as_dict=1)
	
	return audits


@frappe.whitelist()
def get_non_compliant_assets(compliance_threshold=80):
	"""Get all assets with compliance percentage below threshold"""
	audits = frappe.get_all(
		"Asset Audit",
		filters={
			"docstatus": 1,
			"audit_status": "Completed",
			"compliance_percentage": ["<", compliance_threshold]
		},
		fields=["name", "asset", "asset_name", "audit_date", "compliance_percentage", "critical_findings", "major_findings"],
		order_by="compliance_percentage asc"
	)
	return audits

