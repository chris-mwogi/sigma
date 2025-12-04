# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

"""
Monitoring Ingestion API

This module handles webhook ingestion from various monitoring platforms
(OpManager, Zabbix, PRTG, IoT Gateways, SCADA, etc.)

Features:
- Webhook signature validation (HMAC-SHA256/SHA512)
- Rate limiting per platform
- Device identity resolution (MAC, IMEI, Serial, UUID, IP)
- Auto-create/update Monitored Device records
- Create Telemetry Event or Monitoring Alert records
- Link devices to specific Monitoring Platform instances
"""

import frappe
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from frappe import _


@frappe.whitelist(allow_guest=True, methods=["POST"])
def receive_webhook():
	"""
	Receive webhook data from monitoring platforms.
	
	Query Parameters:
		platform: Name of the Monitoring Platform (required)
	
	Request Body (JSON):
		{
			"device": {
				"name": "Device Name",
				"mac_address": "00:11:22:33:44:55",
				"ip_address": "192.168.1.100",
				"serial_number": "SN123456",
				"imei": "123456789012345",
				"uuid": "550e8400-e29b-41d4-a716-446655440000",
				"device_type": "Router/Switch/Server/Sensor/Camera/etc",
				"manufacturer": "Cisco",
				"model": "ISR4331",
				"location": "Data Center A"
			},
			"event_type": "telemetry" or "alert",
			"telemetry": {
				"metric_name": "cpu_usage",
				"metric_value": 85.5,
				"metric_unit": "%",
				"timestamp": "2025-11-15T09:00:00Z"
			},
			"alert": {
				"alert_type": "Performance",
				"severity": "Critical",
				"message": "CPU usage exceeded 80%",
				"timestamp": "2025-11-15T09:00:00Z"
			}
		}
	
	Returns:
		{
			"success": true,
			"message": "Data ingested successfully",
			"device_id": "MD-00001",
			"event_id": "TE-00001" or "MA-00001"
		}
	"""
	try:
		# Get platform name from query parameter
		# Try multiple methods to get the platform parameter
		platform_name = frappe.form_dict.get("platform") or frappe.request.args.get("platform")
		if not platform_name:
			frappe.throw(_("Platform parameter is required"), frappe.ValidationError)
		
		# Get Monitoring Platform record
		platform = frappe.get_doc("Monitoring Platform", platform_name)
		
		# Check if platform is enabled
		if not platform.enabled:
			frappe.throw(_("Monitoring Platform '{0}' is disabled").format(platform_name), frappe.PermissionError)
		
		# Validate webhook signature if enabled
		if platform.signature_validation_enabled:
			validate_webhook_signature(platform)
		
		# Check rate limits
		check_rate_limits(platform)
		
		# Parse request body
		try:
			data = json.loads(frappe.request.data)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid JSON payload"), frappe.ValidationError)
		
		# Validate required fields
		if "device" not in data:
			frappe.throw(_("Device information is required"), frappe.ValidationError)
		
		if "event_type" not in data:
			frappe.throw(_("Event type is required (telemetry or alert)"), frappe.ValidationError)
		
		# Get or create Monitored Device
		device_doc = get_or_create_monitored_device(data["device"], platform)
		
		# Create event based on type
		event_doc = None
		if data["event_type"] == "telemetry" and "telemetry" in data:
			event_doc = create_telemetry_event(device_doc, data["telemetry"], platform)
		elif data["event_type"] == "alert" and "alert" in data:
			event_doc = create_monitoring_alert(device_doc, data["alert"], platform)
		else:
			frappe.throw(_("Invalid event type or missing event data"), frappe.ValidationError)
		
		# Update platform statistics
		platform.update_statistics()
		
		# Commit the transaction
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Data ingested successfully"),
			"device_id": device_doc.name,
			"event_id": event_doc.name if event_doc else None
		}
	
	except frappe.DoesNotExistError:
		frappe.log_error(f"Monitoring Platform '{platform_name}' not found", "Webhook Ingestion Error")
		return {
			"success": False,
			"error": _("Monitoring Platform not found")
		}, 404
	
	except frappe.ValidationError as e:
		frappe.log_error(str(e), "Webhook Validation Error")
		return {
			"success": False,
			"error": str(e)
		}, 400
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Webhook Ingestion Error")
		return {
			"success": False,
			"error": _("Internal server error")
		}, 500


def validate_webhook_signature(platform):
	"""
	Validate webhook signature using HMAC.

	Expected header: X-Webhook-Signature or X-Hub-Signature
	Format: sha256=<signature> or sha512=<signature>
	"""
	signature_header = frappe.request.headers.get("X-Webhook-Signature") or frappe.request.headers.get("X-Hub-Signature")

	if not signature_header:
		frappe.throw(_("Webhook signature is missing"), frappe.ValidationError)

	# Parse signature format (e.g., "sha256=abc123...")
	try:
		algorithm, signature = signature_header.split("=", 1)
	except ValueError:
		frappe.throw(_("Invalid signature format"), frappe.ValidationError)

	# Get webhook secret
	webhook_secret = platform.get_password("webhook_secret")
	if not webhook_secret:
		frappe.throw(_("Webhook secret not configured for platform '{0}'").format(platform.name), frappe.ValidationError)

	# Calculate expected signature
	payload = frappe.request.data

	if algorithm == "sha256" or platform.signature_algorithm == "HMAC-SHA256":
		expected_signature = hmac.new(
			webhook_secret.encode(),
			payload,
			hashlib.sha256
		).hexdigest()
	elif algorithm == "sha512" or platform.signature_algorithm == "HMAC-SHA512":
		expected_signature = hmac.new(
			webhook_secret.encode(),
			payload,
			hashlib.sha512
		).hexdigest()
	else:
		frappe.throw(_("Unsupported signature algorithm: {0}").format(algorithm), frappe.ValidationError)

	# Compare signatures (constant-time comparison)
	if not hmac.compare_digest(signature, expected_signature):
		frappe.throw(_("Invalid webhook signature"), frappe.PermissionError)


def check_rate_limits(platform):
	"""
	Check if the platform has exceeded rate limits.
	"""
	if not platform.enable_rate_limiting:
		return

	now = datetime.now()
	cache_key_prefix = f"monitoring_platform_rate_limit:{platform.name}"

	# Check per-minute limit
	if platform.rate_limit_per_minute:
		minute_key = f"{cache_key_prefix}:minute:{now.strftime('%Y%m%d%H%M')}"
		minute_count = frappe.cache().get(minute_key) or 0

		if minute_count >= platform.rate_limit_per_minute:
			frappe.throw(_("Rate limit exceeded: {0} requests per minute").format(platform.rate_limit_per_minute), frappe.RateLimitExceededError)

		frappe.cache().setex(minute_key, 60, minute_count + 1)

	# Check per-hour limit
	if platform.rate_limit_per_hour:
		hour_key = f"{cache_key_prefix}:hour:{now.strftime('%Y%m%d%H')}"
		hour_count = frappe.cache().get(hour_key) or 0

		if hour_count >= platform.rate_limit_per_hour:
			frappe.throw(_("Rate limit exceeded: {0} requests per hour").format(platform.rate_limit_per_hour), frappe.RateLimitExceededError)

		frappe.cache().setex(hour_key, 3600, hour_count + 1)

	# Check per-day limit
	if platform.rate_limit_per_day:
		day_key = f"{cache_key_prefix}:day:{now.strftime('%Y%m%d')}"
		day_count = frappe.cache().get(day_key) or 0

		if day_count >= platform.rate_limit_per_day:
			frappe.throw(_("Rate limit exceeded: {0} requests per day").format(platform.rate_limit_per_day), frappe.RateLimitExceededError)

		frappe.cache().setex(day_key, 86400, day_count + 1)


def get_or_create_monitored_device(device_data, platform):
	"""
	Get existing or create new Monitored Device.

	Device identity resolution priority:
	1. MAC Address (highest priority)
	2. IMEI
	3. Serial Number
	4. UUID
	5. IP Address (lowest priority)
	"""
	# Try to find existing device by identity fields
	filters = {"monitoring_platform": platform.name}

	# Priority 1: MAC Address
	if device_data.get("mac_address"):
		existing = frappe.db.get_value("Monitored Device", {
			"mac_address": device_data["mac_address"],
			"monitoring_platform": platform.name
		})
		if existing:
			doc = frappe.get_doc("Monitored Device", existing)
			update_device_fields(doc, device_data)
			doc.save(ignore_permissions=True)
			return doc

	# Priority 2: IMEI
	if device_data.get("imei"):
		existing = frappe.db.get_value("Monitored Device", {
			"imei": device_data["imei"],
			"monitoring_platform": platform.name
		})
		if existing:
			doc = frappe.get_doc("Monitored Device", existing)
			update_device_fields(doc, device_data)
			doc.save(ignore_permissions=True)
			return doc

	# Priority 3: Serial Number
	if device_data.get("serial_number"):
		existing = frappe.db.get_value("Monitored Device", {
			"serial_number": device_data["serial_number"],
			"monitoring_platform": platform.name
		})
		if existing:
			doc = frappe.get_doc("Monitored Device", existing)
			update_device_fields(doc, device_data)
			doc.save(ignore_permissions=True)
			return doc

	# Priority 4: UUID
	if device_data.get("uuid"):
		existing = frappe.db.get_value("Monitored Device", {
			"uuid": device_data["uuid"],
			"monitoring_platform": platform.name
		})
		if existing:
			doc = frappe.get_doc("Monitored Device", existing)
			update_device_fields(doc, device_data)
			doc.save(ignore_permissions=True)
			return doc

	# Priority 5: IP Address (least reliable)
	if device_data.get("ip_address"):
		existing = frappe.db.get_value("Monitored Device", {
			"ip_address": device_data["ip_address"],
			"monitoring_platform": platform.name
		})
		if existing:
			doc = frappe.get_doc("Monitored Device", existing)
			update_device_fields(doc, device_data)
			doc.save(ignore_permissions=True)
			return doc

	# Create new device if not found
	doc = frappe.new_doc("Monitored Device")
	doc.monitoring_platform = platform.name
	doc.source_system = platform.platform_type
	update_device_fields(doc, device_data)
	doc.insert(ignore_permissions=True)
	return doc


def update_device_fields(doc, device_data):
	"""Update device fields from webhook data."""
	# device_uid is required - use MAC, IMEI, Serial, or IP as fallback
	if not doc.device_uid:
		doc.device_uid = (
			device_data.get("mac_address") or
			device_data.get("imei") or
			device_data.get("serial_number") or
			device_data.get("uuid") or
			device_data.get("ip_address") or
			device_data.get("name")
		)

	if device_data.get("mac_address"):
		doc.mac_address = device_data["mac_address"]

	if device_data.get("ip_address"):
		doc.ip_address = device_data["ip_address"]

	if device_data.get("serial_number"):
		doc.serial_number = device_data["serial_number"]

	if device_data.get("imei"):
		doc.imei = device_data["imei"]

	# source_device_id is required - use the device ID from the source system
	if not doc.source_device_id:
		doc.source_device_id = device_data.get("source_id") or device_data.get("id") or doc.device_uid

	# Set status to Active if not set
	if not doc.status:
		doc.status = "Active"

	# Set enabled flag
	if not hasattr(doc, 'enabled') or doc.enabled is None:
		doc.enabled = 1

	# Update last_seen timestamp
	doc.last_seen = datetime.now()

	# Store additional metadata as JSON
	metadata = {}
	if device_data.get("name"):
		metadata["name"] = device_data["name"]
	if device_data.get("device_type"):
		metadata["device_type"] = device_data["device_type"]
	if device_data.get("manufacturer"):
		metadata["manufacturer"] = device_data["manufacturer"]
	if device_data.get("model"):
		metadata["model"] = device_data["model"]
	if device_data.get("location"):
		metadata["location"] = device_data["location"]

	if metadata:
		doc.metadata = json.dumps(metadata)

	# Location tracking integration - update GPS coordinates if provided
	if device_data.get("latitude") and device_data.get("longitude"):
		# Enable location tracking if not already enabled
		if not doc.enable_location_tracking:
			doc.enable_location_tracking = 1

		# Update location using the Monitored Device method
		# This automatically creates location history and checks geofence
		doc.update_location(
			latitude=device_data["latitude"],
			longitude=device_data["longitude"],
			altitude=device_data.get("altitude"),
			accuracy=device_data.get("location_accuracy"),
			speed=device_data.get("speed"),
			heading=device_data.get("heading"),
			location_source=device_data.get("location_source", "GPS"),
			address=device_data.get("address")
		)


def create_telemetry_event(device_doc, telemetry_data, platform):
	"""Create a Telemetry Event record."""
	doc = frappe.new_doc("Telemetry Event")
	doc.monitored_device = device_doc.name
	doc.source_system = platform.platform_type

	if telemetry_data.get("metric_name"):
		doc.metric_name = telemetry_data["metric_name"]

	if telemetry_data.get("metric_value"):
		doc.metric_value = telemetry_data["metric_value"]

	if telemetry_data.get("metric_unit"):
		doc.metric_unit = telemetry_data["metric_unit"]

	if telemetry_data.get("timestamp"):
		try:
			doc.timestamp = telemetry_data["timestamp"]
		except:
			doc.timestamp = datetime.now()
	else:
		doc.timestamp = datetime.now()

	doc.insert(ignore_permissions=True)
	return doc


def create_monitoring_alert(device_doc, alert_data, platform):
	"""Create a Monitoring Alert record."""
	doc = frappe.new_doc("Monitoring Alert")
	doc.monitored_device = device_doc.name
	doc.source_system = platform.platform_type

	if alert_data.get("alert_type"):
		doc.alert_type = alert_data["alert_type"]

	if alert_data.get("severity"):
		doc.severity = alert_data["severity"]

	if alert_data.get("message"):
		doc.message = alert_data["message"]

	if alert_data.get("timestamp"):
		try:
			doc.timestamp = alert_data["timestamp"]
		except:
			doc.timestamp = datetime.now()
	else:
		doc.timestamp = datetime.now()

	# Set status to Open
	doc.status = "Open"

	doc.insert(ignore_permissions=True)

	# Auto-create Issue for Critical alerts if configured
	if doc.severity == "Critical" and platform.get("auto_create_issues"):
		create_issue_from_alert(doc, device_doc)

	return doc


def create_issue_from_alert(alert_doc, device_doc):
	"""Auto-create Issue from Critical alert."""
	try:
		issue = frappe.new_doc("Issue")
		issue.subject = f"Critical Alert: {alert_doc.message}"
		issue.description = f"""
		<p><strong>Monitoring Alert Details:</strong></p>
		<ul>
			<li><strong>Device:</strong> {device_doc.device_name}</li>
			<li><strong>Alert Type:</strong> {alert_doc.alert_type}</li>
			<li><strong>Severity:</strong> {alert_doc.severity}</li>
			<li><strong>Message:</strong> {alert_doc.message}</li>
			<li><strong>Timestamp:</strong> {alert_doc.timestamp}</li>
		</ul>
		"""
		issue.priority = "High"
		issue.status = "Open"
		issue.insert(ignore_permissions=True)

		# Link alert to issue
		alert_doc.db_set("linked_issue", issue.name)

	except Exception as e:
		frappe.log_error(f"Failed to create issue from alert: {str(e)}", "Auto-Create Issue Error")


@frappe.whitelist()
def link_monitoring_alert_to_case(alert_name, case_name):
	"""
	Link Monitoring Alert to a case (Support Ticket, Issue, or custom Case DocType).

	This replaces the deprecated link_asset_event_to_case() function.

	Args:
		alert_name: Monitoring Alert name
		case_name: Case/Issue/Support Ticket name

	Returns:
		Updated alert document
	"""
	try:
		if not frappe.db.exists("Monitoring Alert", alert_name):
			frappe.throw(_("Monitoring Alert {0} does not exist").format(alert_name))

		alert = frappe.get_doc("Monitoring Alert", alert_name)

		# Check if case exists (try multiple doctypes)
		case_doctype = None
		for doctype in ["Issue", "Support Ticket", "Case"]:
			if frappe.db.exists(doctype, case_name):
				case_doctype = doctype
				break

		if not case_doctype:
			frappe.throw(_("Case {0} not found in Issue, Support Ticket, or Case doctypes").format(case_name))

		# Link alert to case via linked_issue field (works for Issue doctype)
		if case_doctype == "Issue":
			alert.linked_issue = case_name

		# Store case link in notes for other doctypes
		case_link_note = f"Linked to {case_doctype}: {case_name}"
		if alert.notes:
			alert.notes += f"\n{case_link_note}"
		else:
			alert.notes = case_link_note

		# Update workflow state to indicate it's being handled
		if alert.workflow_state == "Open":
			alert.workflow_state = "In Progress"

		alert.save(ignore_permissions=True)

		return {
			"status": "success",
			"message": _("Monitoring Alert linked to {0} successfully").format(case_doctype),
			"alert": alert_name,
			"case": case_name,
			"case_doctype": case_doctype
		}

	except Exception as e:
		frappe.log_error(f"Failed to link Monitoring Alert to case: {str(e)}")
		frappe.throw(f"Failed to link Monitoring Alert to case: {str(e)}")


@frappe.whitelist()
def update_device_location(monitored_device_id, latitude, longitude,
                          altitude=None, accuracy=None, speed=None,
                          heading=None, location_source=None, address=None):
	"""
	Update GPS coordinates for a monitored device.

	This is the correct endpoint for location tracking.
	Replaces the deprecated update_asset_location() endpoint.

	Args:
		monitored_device_id: Monitored Device ID
		latitude: GPS latitude (-90 to 90)
		longitude: GPS longitude (-180 to 180)
		altitude: Altitude in meters (optional)
		accuracy: GPS accuracy in meters (optional)
		speed: Speed in km/h (optional)
		heading: Direction in degrees 0-360 (optional)
		location_source: GPS/Cell Tower/Wi-Fi/Manual/IP Geolocation (optional)
		address: Physical address (optional)

	Returns:
		Success status with updated location
	"""
	if not frappe.db.exists("Monitored Device", monitored_device_id):
		frappe.throw(_("Monitored Device {0} does not exist").format(monitored_device_id))

	device = frappe.get_doc("Monitored Device", monitored_device_id)

	# Enable location tracking if not already enabled
	if not device.enable_location_tracking:
		device.enable_location_tracking = 1

	# Update location (this also creates location history and checks geofence)
	device.update_location(
		latitude=latitude,
		longitude=longitude,
		altitude=altitude,
		accuracy=accuracy,
		speed=speed,
		heading=heading,
		location_source=location_source or "GPS",
		address=address
	)

	# Optionally sync to linked Asset for reporting
	if device.asset:
		try:
			asset = frappe.get_doc("Asset", device.asset)
			asset.latitude = latitude
			asset.longitude = longitude
			if altitude:
				asset.altitude = altitude
			asset.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Failed to sync location to Asset: {str(e)}")

	return {
		"status": "success",
		"message": _("Device location updated successfully"),
		"monitored_device": monitored_device_id,
		"latitude": latitude,
		"longitude": longitude,
		"location_history_count": len(device.location_history) if device.location_history else 0
	}


@frappe.whitelist()
def get_device_monitoring_info(monitored_device_id, days=7):
	"""
	Get comprehensive monitoring information for a device.

	Replaces get_asset_iot_info() with device-centric approach.

	Args:
		monitored_device_id: Monitored Device ID
		days: Number of days to look back (default 7)

	Returns:
		Device info, alerts, telemetry, and location history
	"""
	if not frappe.db.exists("Monitored Device", monitored_device_id):
		frappe.throw(_("Monitored Device {0} does not exist").format(monitored_device_id))

	device = frappe.get_doc("Monitored Device", monitored_device_id)

	# Get recent alerts
	from datetime import timedelta
	start_date = datetime.now() - timedelta(days=int(days))

	alerts = frappe.get_all(
		"Monitoring Alert",
		filters={
			"monitored_device": monitored_device_id,
			"timestamp": [">", start_date.isoformat()]
		},
		fields=["name", "alert_type", "severity", "message", "timestamp",
		        "workflow_state"],
		order_by="timestamp desc"
	)

	# Get recent telemetry
	telemetry = frappe.get_all(
		"Telemetry Event",
		filters={
			"monitored_device": monitored_device_id,
			"timestamp": [">", start_date.isoformat()]
		},
		fields=["name", "metric_name", "metric_value", "metric_unit", "timestamp"],
		order_by="timestamp desc",
		limit=100
	)

	# Get location history
	location_history = device.get_location_history(limit=50) if hasattr(device, 'get_location_history') else []

	return {
		"status": "success",
		"device": {
			"id": device.name,
			"device_uid": device.device_uid,
			"status": device.status,
			"last_seen": device.last_seen,
			"monitoring_platform": device.monitoring_platform,
			"linked_asset": device.asset
		},
		"alerts": alerts,
		"alert_count": len(alerts),
		"telemetry": telemetry,
		"telemetry_count": len(telemetry),
		"location_history": location_history,
		"location_count": len(location_history),
		"current_location": {
			"latitude": device.current_latitude,
			"longitude": device.current_longitude,
			"altitude": device.current_altitude,
			"last_update": device.last_location_update
		} if device.enable_location_tracking else None
	}

