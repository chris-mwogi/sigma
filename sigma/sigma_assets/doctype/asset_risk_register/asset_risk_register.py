# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, add_months, getdate

class AssetRiskRegister(Document):
	"""
	Asset Risk Register - ISO 31000 compliant risk management
	"""
	
	def validate(self):
		"""Validate risk register entry"""
		self.validate_scores()
		self.calculate_inherent_risk()
		self.calculate_residual_risk()
		self.determine_risk_levels()
		self.check_risk_appetite()
		self.update_audit_trail()
	
	def validate_scores(self):
		"""Validate likelihood and consequence scores"""
		if self.likelihood_score and (self.likelihood_score < 1 or self.likelihood_score > 5):
			frappe.throw("Likelihood Score must be between 1 and 5")
		
		if self.consequence_score and (self.consequence_score < 1 or self.consequence_score > 5):
			frappe.throw("Consequence Score must be between 1 and 5")
	
	def calculate_inherent_risk(self):
		"""Calculate inherent risk score (Likelihood × Consequence)"""
		if self.likelihood_score and self.consequence_score:
			self.inherent_risk_score = self.likelihood_score * self.consequence_score
	
	def calculate_residual_risk(self):
		"""Calculate residual risk after controls"""
		if self.inherent_risk_score and self.control_effectiveness:
			# Residual Risk = Inherent Risk × (1 - Control Effectiveness)
			self.residual_risk_score = self.inherent_risk_score * (1 - (self.control_effectiveness / 100))
		else:
			self.residual_risk_score = self.inherent_risk_score
	
	def determine_risk_levels(self):
		"""Determine risk levels based on scores"""
		# Inherent Risk Level
		if self.inherent_risk_score:
			if self.inherent_risk_score <= 5:
				self.inherent_risk_level = "Low (1-5)"
			elif self.inherent_risk_score <= 12:
				self.inherent_risk_level = "Medium (6-12)"
			elif self.inherent_risk_score <= 20:
				self.inherent_risk_level = "High (13-20)"
			else:
				self.inherent_risk_level = "Very High (21-25)"
		
		# Residual Risk Level
		if self.residual_risk_score:
			if self.residual_risk_score <= 5:
				self.residual_risk_level = "Low"
			elif self.residual_risk_score <= 12:
				self.residual_risk_level = "Medium"
			elif self.residual_risk_score <= 20:
				self.residual_risk_level = "High"
			else:
				self.residual_risk_level = "Very High"
	
	def check_risk_appetite(self):
		"""Check if residual risk exceeds appetite threshold"""
		if self.residual_risk_score and self.risk_appetite_threshold:
			if self.residual_risk_score > self.risk_appetite_threshold:
				self.escalation_required = 1
				frappe.msgprint(
					f"⚠️ Residual Risk ({self.residual_risk_score:.2f}) exceeds Risk Appetite Threshold ({self.risk_appetite_threshold}). Escalation required.",
					indicator="orange",
					alert=True
				)
	
	def update_audit_trail(self):
		"""Update audit trail with changes"""
		if self.is_new():
			self.audit_trail = f"<p><strong>{nowdate()}:</strong> Risk assessment created by {frappe.session.user}</p>"
		else:
			# Append to existing audit trail
			if not self.audit_trail:
				self.audit_trail = ""
			
			changes = []
			if self.has_value_changed("risk_status"):
				changes.append(f"Status changed to {self.risk_status}")
			if self.has_value_changed("treatment_status"):
				changes.append(f"Treatment status changed to {self.treatment_status}")
			if self.has_value_changed("residual_risk_score"):
				changes.append(f"Residual risk score updated to {self.residual_risk_score:.2f}")
			
			if changes:
				change_text = ", ".join(changes)
				self.audit_trail += f"<p><strong>{nowdate()}:</strong> {change_text} (by {frappe.session.user})</p>"
	
	def on_submit(self):
		"""Actions on submission"""
		# Update asset risk score if residual risk is higher
		if self.asset and self.residual_risk_score:
			asset = frappe.get_doc("Asset", self.asset)
			if not asset.risk_score or self.residual_risk_score > asset.risk_score:
				asset.risk_score = self.residual_risk_score
				asset.save(ignore_permissions=True)
				frappe.msgprint(f"✅ Asset risk score updated to {self.residual_risk_score:.2f}", indicator="green")


@frappe.whitelist()
def get_high_risk_assets():
	"""Get all assets with high or very high residual risk"""
	risks = frappe.get_all(
		"Asset Risk Register",
		filters={
			"docstatus": 1,
			"risk_status": ["in", ["Open", "Under Treatment"]],
			"residual_risk_level": ["in", ["High", "Very High"]]
		},
		fields=["name", "asset", "asset_name", "risk_type", "residual_risk_score", "residual_risk_level", "treatment_status"],
		order_by="residual_risk_score desc"
	)
	return risks


@frappe.whitelist()
def get_overdue_treatments():
	"""Get all risk treatments that are overdue"""
	today = getdate(nowdate())
	risks = frappe.get_all(
		"Asset Risk Register",
		filters={
			"docstatus": 1,
			"treatment_status": ["in", ["Not Started", "In Progress"]],
			"treatment_deadline": ["<", today]
		},
		fields=["name", "asset", "asset_name", "risk_type", "treatment_strategy", "treatment_deadline", "treatment_owner"],
		order_by="treatment_deadline asc"
	)
	return risks


@frappe.whitelist()
def escalate_risk(risk_name, escalate_to):
	"""Escalate a risk to a higher authority"""
	risk = frappe.get_doc("Asset Risk Register", risk_name)
	risk.escalation_required = 1
	risk.escalation_to = escalate_to
	risk.save(ignore_permissions=True)
	
	# Send notification
	frappe.sendmail(
		recipients=[escalate_to],
		subject=f"Risk Escalation: {risk.asset_name} - {risk.risk_type}",
		message=f"""
		<p>A risk has been escalated to you for review:</p>
		<ul>
			<li><strong>Asset:</strong> {risk.asset_name}</li>
			<li><strong>Risk Type:</strong> {risk.risk_type}</li>
			<li><strong>Residual Risk Score:</strong> {risk.residual_risk_score:.2f} ({risk.residual_risk_level})</li>
			<li><strong>Risk Description:</strong> {risk.risk_description}</li>
		</ul>
		<p><a href="{frappe.utils.get_url()}/app/asset-risk-register/{risk.name}">View Risk Register</a></p>
		"""
	)
	
	frappe.msgprint(f"✅ Risk escalated to {escalate_to}", indicator="green")
	return risk

