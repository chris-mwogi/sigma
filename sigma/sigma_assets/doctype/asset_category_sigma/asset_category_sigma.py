# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetCategorySigma(Document):
	"""
	Asset Category with ISO 55000/55001 compliance fields.
	
	This DocType extends the basic asset categorization with:
	- Maintenance strategies (TBM, CBM, Predictive)
	- IoT and network asset flags
	- Risk classification (ISO 31000)
	- Compliance standards (ISO 55000, ISO 14224, NIST, IEC 61850)
	- Lifecycle and depreciation templates
	"""
	
	def validate(self):
		"""Validate asset category configuration."""
		self.validate_risk_scores()
		self.validate_maintenance_strategy()
		self.validate_lifecycle_settings()
		self.validate_compliance_requirements()
	
	def validate_risk_scores(self):
		"""Validate risk scores are within acceptable range (1-10)."""
		if self.failure_impact_score:
			if self.failure_impact_score < 1 or self.failure_impact_score > 10:
				frappe.throw("Failure Impact Score must be between 1 and 10")
		
		if self.environmental_impact_score:
			if self.environmental_impact_score < 1 or self.environmental_impact_score > 10:
				frappe.throw("Environmental Impact Score must be between 1 and 10")
	
	def validate_maintenance_strategy(self):
		"""Validate maintenance strategy configuration."""
		if self.enable_predictive_maintenance and not self.is_iot_enabled:
			frappe.msgprint(
				"Predictive Maintenance typically requires IoT-enabled assets. "
				"Consider enabling 'IoT Enabled' flag.",
				indicator="orange",
				alert=True
			)
		
		if self.enable_condition_based_maintenance and not self.is_iot_enabled:
			frappe.msgprint(
				"Condition-Based Maintenance typically requires IoT-enabled assets. "
				"Consider enabling 'IoT Enabled' flag.",
				indicator="orange",
				alert=True
			)
		
		# Validate MTBF and MTTR
		if self.mtbf_hours and self.mttr_hours:
			if self.mttr_hours > self.mtbf_hours:
				frappe.throw("MTTR (Mean Time To Repair) cannot be greater than MTBF (Mean Time Between Failures)")
	
	def validate_lifecycle_settings(self):
		"""Validate lifecycle and depreciation settings."""
		if self.residual_value_percentage:
			if self.residual_value_percentage < 0 or self.residual_value_percentage > 100:
				frappe.throw("Residual Value Percentage must be between 0 and 100")
		
		if self.calibration_required and not self.calibration_frequency_months:
			frappe.throw("Calibration Frequency is required when Calibration Required is checked")
	
	def validate_compliance_requirements(self):
		"""Validate compliance requirements."""
		if self.requires_cybersecurity_compliance and not self.nist_cybersecurity_required:
			frappe.msgprint(
				"Assets requiring cybersecurity compliance should typically follow NIST SP 800-53. "
				"Consider enabling 'NIST SP 800-53 Cybersecurity Required'.",
				indicator="orange",
				alert=True
			)
		
		if self.is_network_asset and not self.requires_cybersecurity_compliance:
			frappe.msgprint(
				"Network assets typically require cybersecurity compliance. "
				"Consider enabling 'Requires Cybersecurity Compliance'.",
				indicator="orange",
				alert=True
			)
	
	def get_maintenance_schedule_template(self):
		"""
		Get maintenance schedule template based on category settings.
		
		Returns:
			dict: Maintenance schedule configuration
		"""
		return {
			"maintenance_strategy": self.maintenance_strategy,
			"frequency": self.default_maintenance_frequency,
			"duration_hours": self.default_maintenance_duration,
			"predictive_enabled": self.enable_predictive_maintenance,
			"condition_based_enabled": self.enable_condition_based_maintenance,
			"mtbf_hours": self.mtbf_hours,
			"mttr_hours": self.mttr_hours
		}
	
	def get_risk_profile(self):
		"""
		Get risk profile for assets in this category.
		
		Returns:
			dict: Risk profile configuration
		"""
		return {
			"risk_classification": self.default_risk_classification,
			"failure_impact_score": self.failure_impact_score or 0,
			"environmental_impact_score": self.environmental_impact_score or 0,
			"safety_critical": self.safety_critical,
			"criticality_level": self.criticality_level
		}
	
	def get_compliance_requirements(self):
		"""
		Get compliance requirements for assets in this category.
		
		Returns:
			list: List of compliance standards
		"""
		requirements = []
		
		if self.iso_55000_compliant:
			requirements.append("ISO 55000/55001 - Asset Management")
		
		if self.iso_14224_failure_codes:
			requirements.append("ISO 14224 - Failure Codes and Maintenance Taxonomy")
		
		if self.nist_cybersecurity_required:
			requirements.append("NIST SP 800-53 - Cybersecurity Controls")
		
		if self.iec_61850_compliant:
			requirements.append("IEC 61850 - Utility Asset Communication")
		
		if self.itil_configuration_item:
			requirements.append("ITIL4 - Configuration Management")
		
		if self.regulatory_compliance_required and self.compliance_standards:
			requirements.append(self.compliance_standards)
		
		if self.custom_compliance_requirements:
			requirements.append(self.custom_compliance_requirements)
		
		return requirements


@frappe.whitelist()
def get_category_defaults(category_name):
	"""
	Get default values from asset category for new assets.
	
	Args:
		category_name (str): Name of the asset category
	
	Returns:
		dict: Default values for asset creation
	"""
	if not category_name:
		return {}
	
	category = frappe.get_doc("Asset Category Sigma", category_name)
	
	return {
		"maintenance_strategy": category.maintenance_strategy,
		"maintenance_frequency": category.default_maintenance_frequency,
		"expected_useful_life_years": category.expected_useful_life_years,
		"depreciation_method": category.depreciation_method,
		"residual_value_percentage": category.residual_value_percentage,
		"warranty_period_months": category.warranty_period_months,
		"risk_classification": category.default_risk_classification,
		"criticality_level": category.criticality_level,
		"is_iot_enabled": category.is_iot_enabled,
		"is_network_asset": category.is_network_asset,
		"requires_gps_tracking": category.requires_gps_tracking,
		"safety_critical": category.safety_critical,
		"calibration_required": category.calibration_required,
		"calibration_frequency_months": category.calibration_frequency_months
	}

