# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class Asset(Document):
	"""
	Asset DocType for Sigma Asset Integrations module.
	Manages physical and digital assets with support for composite assets (assets with components).
	"""

	def validate(self):
		"""Validate asset data"""
		self.validate_item()
		self.validate_dates()
		self.validate_amounts()
		self.validate_composite_asset()
		self.validate_iso_55000_fields()
		self.validate_monitoring_integration()
		self.validate_maintenance_settings()
		self.validate_depreciation_settings()
		self.sync_from_category()
		self.calculate_risk_score()
		self.set_status()

	def validate_item(self):
		"""Validate item code and fetch item details"""
		if self.item_code:
			item = frappe.get_doc("Item", self.item_code)
			if not self.item_name:
				self.item_name = item.item_name

	def validate_dates(self):
		"""Validate purchase and availability dates"""
		if self.purchase_date and self.available_for_use_date:
			if getdate(self.available_for_use_date) < getdate(self.purchase_date):
				frappe.throw(_("Available for Use Date cannot be before Purchase Date"))

	def validate_amounts(self):
		"""Validate purchase amounts"""
		if self.purchase_amount and self.purchase_amount < 0:
			frappe.throw(_("Purchase Amount cannot be negative"))
		
		if self.gross_purchase_amount and self.gross_purchase_amount < 0:
			frappe.throw(_("Gross Purchase Amount cannot be negative"))
		
		# If gross purchase amount is provided, it should be >= purchase amount
		if self.gross_purchase_amount and self.purchase_amount:
			if self.gross_purchase_amount < self.purchase_amount:
				frappe.throw(_("Gross Purchase Amount cannot be less than Purchase Amount"))

	def validate_composite_asset(self):
		"""Validate composite asset and components"""
		if self.is_composite_asset:
			if not self.components or len(self.components) == 0:
				frappe.msgprint(
					_("Warning: This is marked as a Composite Asset but has no components. "
					  "Consider adding components or unchecking 'Is Composite Asset'."),
					alert=True
				)
		else:
			# If not composite but has components, warn user
			if self.components and len(self.components) > 0:
				frappe.msgprint(
					_("Warning: This asset has components but is not marked as a Composite Asset. "
					  "Consider checking 'Is Composite Asset'."),
					alert=True
				)

	def set_status(self):
		"""Set asset status based on document state"""
		if self.docstatus == 0:
			self.status = "Draft"
		elif self.docstatus == 1:
			if not self.status or self.status == "Draft":
				self.status = "Submitted"
		elif self.docstatus == 2:
			self.status = "Cancelled"

	def on_submit(self):
		"""Actions to perform on submit"""
		self.validate_required_fields_for_submit()
		self.set_status()

	def validate_required_fields_for_submit(self):
		"""Validate required fields before submission"""
		if not self.asset_name:
			frappe.throw(_("Asset Name is required for submission"))
		
		if not self.item_code:
			frappe.throw(_("Item Code is required for submission"))
		
		if not self.company:
			frappe.throw(_("Company is required for submission"))

	def on_cancel(self):
		"""Actions to perform on cancel"""
		self.set_status()

	def before_save(self):
		"""Actions to perform before saving"""
		# Calculate total component cost if composite asset
		if self.is_composite_asset and self.components:
			total_component_cost = sum([flt(comp.component_cost) for comp in self.components])
			if total_component_cost > 0 and not self.purchase_amount:
				self.purchase_amount = total_component_cost

	def get_total_component_cost(self):
		"""Calculate total cost of all components"""
		if not self.is_composite_asset or not self.components:
			return 0
		return sum([flt(comp.component_cost) for comp in self.components])

	def get_active_components(self):
		"""Get list of active components"""
		if not self.is_composite_asset or not self.components:
			return []
		return [comp for comp in self.components if comp.status == "Active"]

	def get_networked_components(self):
		"""Get list of networked components"""
		if not self.is_composite_asset or not self.components:
			return []
		return [comp for comp in self.components if comp.is_networked_component]

	def get_iot_components(self):
		"""Get list of IoT components"""
		if not self.is_composite_asset or not self.components:
			return []
		return [comp for comp in self.components if comp.is_iot_component]

	def get_tracked_components(self):
		"""Get list of GPS tracked components"""
		if not self.is_composite_asset or not self.components:
			return []
		return [comp for comp in self.components if comp.is_tracked_component]

	def validate_iso_55000_fields(self):
		"""Validate ISO 55000 compliance fields."""
		# Validate risk score range
		if self.risk_score:
			if self.risk_score < 1 or self.risk_score > 100:
				frappe.throw(_("Risk Score must be between 1 and 100"))

		# Validate failure probability
		if self.failure_probability:
			if self.failure_probability < 0 or self.failure_probability > 100:
				frappe.throw(_("Failure Probability must be between 0 and 100"))

		# Validate criticality alignment
		if self.criticality_rating == "Critical" and self.risk_classification not in ["High Risk", "Very High Risk"]:
			frappe.msgprint(
				_("Critical assets typically have High or Very High risk classification. "
				  "Please review the risk classification."),
				indicator="orange",
				alert=True
			)

	def validate_monitoring_integration(self):
		"""Validate monitoring and IoT integration."""
		if self.monitored_device:
			# Verify monitored device exists and link it to this asset
			if frappe.db.exists("Monitored Device", self.monitored_device):
				device = frappe.get_doc("Monitored Device", self.monitored_device)
				if device.asset != self.name:
					# Update monitored device to link to this asset
					frappe.db.set_value("Monitored Device", self.monitored_device, "asset", self.name)
			else:
				frappe.throw(_("Monitored Device {0} does not exist").format(self.monitored_device))

		# If IoT enabled, recommend linking a monitored device
		if self.is_iot_enabled and not self.monitored_device:
			frappe.msgprint(
				_("This asset is marked as IoT Enabled but has no Monitored Device linked. "
				  "Consider linking a Monitored Device for telemetry tracking."),
				indicator="orange",
				alert=True
			)

	def validate_maintenance_settings(self):
		"""Validate maintenance configuration."""
		if self.requires_maintenance:
			if not self.maintenance_frequency:
				frappe.throw(_("Maintenance Frequency is required when Requires Maintenance is checked"))

			if not self.maintenance_strategy:
				frappe.msgprint(
					_("Consider setting a Maintenance Strategy for better maintenance planning."),
					indicator="blue",
					alert=True
				)

		# Validate MTBF and MTTR
		if self.mtbf_hours and self.mttr_hours:
			if self.mttr_hours > self.mtbf_hours:
				frappe.throw(_("MTTR (Mean Time To Repair) cannot be greater than MTBF (Mean Time Between Failures)"))

		# Validate maintenance dates
		if self.last_maintenance_date and self.next_maintenance_date:
			if getdate(self.next_maintenance_date) < getdate(self.last_maintenance_date):
				frappe.throw(_("Next Maintenance Date cannot be before Last Maintenance Date"))

	def validate_depreciation_settings(self):
		"""Validate depreciation and valuation settings."""
		if self.residual_value_percentage:
			if self.residual_value_percentage < 0 or self.residual_value_percentage > 100:
				frappe.throw(_("Residual Value Percentage must be between 0 and 100"))

		if self.expected_useful_life_years and self.expected_useful_life_years < 0:
			frappe.throw(_("Expected Useful Life cannot be negative"))

		# Validate warranty expiry
		if self.warranty_expiry_date and self.purchase_date:
			if getdate(self.warranty_expiry_date) < getdate(self.purchase_date):
				frappe.throw(_("Warranty Expiry Date cannot be before Purchase Date"))

	def sync_from_category(self):
		"""Sync default values from Asset Category Sigma."""
		if self.asset_category_sigma and not self.get("__islocal"):
			# Only sync on new documents or when category changes
			return

		if self.asset_category_sigma:
			category = frappe.get_doc("Asset Category Sigma", self.asset_category_sigma)

			# Sync maintenance settings if not already set
			if not self.maintenance_strategy:
				self.maintenance_strategy = category.maintenance_strategy
			if not self.maintenance_frequency:
				self.maintenance_frequency = category.default_maintenance_frequency

			# Sync lifecycle settings
			if not self.expected_useful_life_years:
				self.expected_useful_life_years = category.expected_useful_life_years
			if not self.depreciation_method:
				self.depreciation_method = category.depreciation_method
			if not self.residual_value_percentage:
				self.residual_value_percentage = category.residual_value_percentage

			# Sync risk settings
			if not self.risk_classification:
				self.risk_classification = category.default_risk_classification
			if not self.criticality_rating:
				self.criticality_rating = category.criticality_level

			# Sync IoT/monitoring flags
			if not self.is_iot_enabled:
				self.is_iot_enabled = category.is_iot_enabled
			if not self.is_network_asset:
				self.is_network_asset = category.is_network_asset
			if not self.requires_gps_tracking:
				self.requires_gps_tracking = category.requires_gps_tracking

			# Sync MTBF/MTTR
			if not self.mtbf_hours:
				self.mtbf_hours = category.mtbf_hours
			if not self.mttr_hours:
				self.mttr_hours = category.mttr_hours

	def calculate_risk_score(self):
		"""Calculate risk score based on failure probability and criticality."""
		if not self.failure_probability or not self.criticality_rating:
			return

		# Map criticality to impact score (1-10)
		criticality_map = {
			"Low": 2,
			"Medium": 5,
			"High": 8,
			"Critical": 10
		}

		impact_score = criticality_map.get(self.criticality_rating, 5)

		# Calculate risk score: (Failure Probability / 10) * Impact Score * 10
		# This gives a score from 1-100
		self.risk_score = int((self.failure_probability / 10) * impact_score * 10)

		# Set risk classification based on score
		if self.risk_score >= 75:
			self.risk_classification = "Very High Risk"
		elif self.risk_score >= 50:
			self.risk_classification = "High Risk"
		elif self.risk_score >= 25:
			self.risk_classification = "Medium Risk"
		else:
			self.risk_classification = "Low Risk"


@frappe.whitelist()
def update_from_telemetry(asset_name, telemetry_data):
	"""
	Update asset health status and environmental conditions from telemetry data.

	Args:
		asset_name (str): Name of the asset
		telemetry_data (dict): Telemetry data from monitoring system

	Returns:
		dict: Updated asset status
	"""
	import json
	if isinstance(telemetry_data, str):
		telemetry_data = json.loads(telemetry_data)

	asset = frappe.get_doc("Asset", asset_name)

	# Update environmental conditions
	if "temperature" in telemetry_data:
		asset.operating_temperature = telemetry_data["temperature"]
	if "humidity" in telemetry_data:
		asset.operating_humidity = telemetry_data["humidity"]
	if "pressure" in telemetry_data:
		asset.operating_pressure = telemetry_data["pressure"]

	# Update health status
	if "health_status" in telemetry_data:
		asset.health_status = telemetry_data["health_status"]

	# Update last telemetry timestamp
	asset.last_telemetry_update = frappe.utils.now_datetime()

	asset.save(ignore_permissions=True)

	return {
		"status": "success",
		"asset": asset.name,
		"health_status": asset.health_status,
		"last_update": asset.last_telemetry_update
	}


@frappe.whitelist()
def get_asset_health_summary(asset_name):
	"""
	Get comprehensive health summary for an asset.

	Args:
		asset_name (str): Name of the asset

	Returns:
		dict: Asset health summary
	"""
	asset = frappe.get_doc("Asset", asset_name)

	# Get recent telemetry events
	telemetry_events = frappe.get_all(
		"Telemetry Event",
		filters={"asset": asset_name},
		fields=["metric_name", "metric_value", "metric_unit", "timestamp", "status"],
		order_by="timestamp desc",
		limit=10
	)

	# Get recent monitoring alerts
	monitoring_alerts = frappe.get_all(
		"Monitoring Alert",
		filters={"asset": asset_name},
		fields=["alert_type", "severity", "message", "timestamp", "workflow_state"],
		order_by="timestamp desc",
		limit=10
	)

	return {
		"asset_name": asset.asset_name,
		"health_status": asset.health_status,
		"condition_index": asset.condition_index,
		"risk_score": asset.risk_score,
		"risk_classification": asset.risk_classification,
		"last_telemetry_update": asset.last_telemetry_update,
		"environmental_conditions": {
			"temperature": asset.operating_temperature,
			"humidity": asset.operating_humidity,
			"pressure": asset.operating_pressure,
			"conditions_met": asset.environmental_conditions_met
		},
		"maintenance": {
			"requires_maintenance": asset.requires_maintenance,
			"last_maintenance_date": asset.last_maintenance_date,
			"next_maintenance_date": asset.next_maintenance_date,
			"maintenance_strategy": asset.maintenance_strategy
		},
		"recent_telemetry": telemetry_events,
		"recent_alerts": monitoring_alerts
	}


@frappe.whitelist()
def get_assets_by_criticality(criticality_rating=None, company=None):
	"""
	Get assets filtered by criticality rating.

	Args:
		criticality_rating (str): Criticality rating (Low, Medium, High, Critical)
		company (str): Company filter

	Returns:
		list: List of assets
	"""
	filters = {}
	if criticality_rating:
		filters["criticality_rating"] = criticality_rating
	if company:
		filters["company"] = company

	assets = frappe.get_all(
		"Asset",
		filters=filters,
		fields=[
			"name", "asset_name", "asset_category_sigma", "criticality_rating",
			"risk_score", "risk_classification", "health_status", "lifecycle_status",
			"location", "company"
		],
		order_by="risk_score desc"
	)

	return assets

