# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_url


class MonitoringPlatform(Document):
	"""Registry for monitoring platform configurations."""
	
	def validate(self):
		"""Validate platform configuration."""
		# Generate webhook URL if not set
		if not self.webhook_url:
			self.webhook_url = self.generate_webhook_url()
		
		# Validate authentication settings
		if self.auth_type == "API Key" and not self.api_key:
			frappe.msgprint("API Key is required for API Key authentication", indicator="orange")
		elif self.auth_type == "Basic Auth" and (not self.username or not self.password):
			frappe.msgprint("Username and Password are required for Basic Auth", indicator="orange")
		elif self.auth_type == "Bearer Token" and not self.auth_token:
			frappe.msgprint("Auth Token is required for Bearer Token authentication", indicator="orange")
		elif self.auth_type == "OAuth 2.0" and (not self.client_id or not self.client_secret):
			frappe.msgprint("Client ID and Client Secret are required for OAuth 2.0", indicator="orange")
		
		# Validate webhook signature settings
		if self.signature_validation_enabled and not self.webhook_secret:
			frappe.throw("Webhook Secret is required when signature validation is enabled")
	
	def on_update(self):
		"""Update statistics after save."""
		self.update_statistics()
	
	def generate_webhook_url(self):
		"""Generate the webhook URL for this platform."""
		site_url = get_url()
		platform_slug = frappe.scrub(self.platform_name)
		webhook_path = f"/api/method/sigma.sigma_asset_integrations.api.monitoring_ingestion.receive_webhook"
		return f"{site_url}{webhook_path}?platform={self.name}"
	
	def update_statistics(self):
		"""Update device and alert statistics for this platform."""
		# Count total devices from this platform
		total_devices = frappe.db.count("Monitored Device", {
			"source_system": self.platform_type,
			"monitoring_platform": self.name
		})
		
		# Count active devices
		active_devices = frappe.db.count("Monitored Device", {
			"source_system": self.platform_type,
			"monitoring_platform": self.name,
			"status": "Active",
			"enabled": 1
		})
		
		# Count alerts today
		from frappe.utils import today
		total_alerts_today = frappe.db.count("Monitoring Alert", {
			"source_system": self.platform_type,
			"timestamp": [">=", today()]
		})
		
		# Update fields without triggering another save
		frappe.db.set_value(self.doctype, self.name, {
			"total_devices": total_devices,
			"active_devices": active_devices,
			"total_alerts_today": total_alerts_today
		}, update_modified=False)
	
	def test_connection(self):
		"""Test connection to the monitoring platform."""
		import requests
		
		if not self.api_endpoint_url:
			frappe.throw("API Endpoint URL is required to test connection")
		
		try:
			headers = self.get_auth_headers()
			timeout = self.timeout_seconds or 30
			verify_ssl = self.verify_ssl if self.use_ssl else False
			
			response = requests.get(
				self.api_endpoint_url,
				headers=headers,
				timeout=timeout,
				verify=verify_ssl
			)
			
			if response.status_code == 200:
				frappe.msgprint(f"✓ Connection successful to {self.platform_name}", indicator="green")
				self.status = "Active"
				self.save()
				return True
			else:
				error_msg = f"Connection failed: HTTP {response.status_code}"
				frappe.msgprint(error_msg, indicator="red")
				self.log_error(error_msg)
				return False
				
		except Exception as e:
			error_msg = f"Connection error: {str(e)}"
			frappe.msgprint(error_msg, indicator="red")
			self.log_error(error_msg)
			return False
	
	def get_auth_headers(self):
		"""Get authentication headers based on auth type."""
		headers = {}
		
		# Add custom headers if provided
		if self.custom_headers:
			import json
			try:
				custom = json.loads(self.custom_headers) if isinstance(self.custom_headers, str) else self.custom_headers
				headers.update(custom)
			except:
				pass
		
		# Add authentication headers
		if self.auth_type == "API Key":
			headers["X-API-Key"] = self.get_password("api_key")
		elif self.auth_type == "Bearer Token":
			headers["Authorization"] = f"Bearer {self.get_password('auth_token')}"
		elif self.auth_type == "Basic Auth":
			import base64
			credentials = f"{self.username}:{self.get_password('password')}"
			encoded = base64.b64encode(credentials.encode()).decode()
			headers["Authorization"] = f"Basic {encoded}"
		
		return headers
	
	def log_error(self, error_message):
		"""Log error to the platform record."""
		frappe.db.set_value(self.doctype, self.name, {
			"last_error": error_message,
			"last_error_time": now(),
			"status": "Error"
		}, update_modified=False)


@frappe.whitelist()
def test_platform_connection(platform_name):
	"""Test connection to a monitoring platform."""
	platform = frappe.get_doc("Monitoring Platform", platform_name)
	return platform.test_connection()

