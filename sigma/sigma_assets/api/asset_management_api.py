# Copyright (c) 2025, Sigma Security Management System
# License: MIT

"""
Asset Management API
Provides comprehensive asset management functionality including:
- Serial number generation and bulk assignment
- Asset queries by IP, MAC, or serial number
- Asset hierarchy management
- Project linking
"""

import frappe
from frappe import _
from frappe.utils import now, getdate
from datetime import datetime
import re


@frappe.whitelist()
def generate_serial_numbers(asset_ids):
	"""
	Generate unique serial numbers for multiple assets.
	Format: ASSET-{YYYY}-{MM}-{NNNNN}
	
	Args:
		asset_ids: List of asset IDs or comma-separated string of asset IDs
	
	Returns:
		dict with success status and generated serials
	"""
	if isinstance(asset_ids, str):
		asset_ids = [id.strip() for id in asset_ids.split(',')]
	
	if not asset_ids:
		frappe.throw(_("No assets provided"))
	
	generated_serials = {}
	current_date = datetime.now()
	year = current_date.strftime("%Y")
	month = current_date.strftime("%m")
	
	# Get the highest serial number for this month
	existing_serials = frappe.db.sql(
		"""
		SELECT serial_number FROM tabAsset 
		WHERE serial_number LIKE %s
		ORDER BY serial_number DESC LIMIT 1
		""",
		(f"ASSET-{year}-{month}-%",),
		as_dict=True
	)
	
	if existing_serials:
		last_serial = existing_serials[0]['serial_number']
		last_number = int(last_serial.split('-')[-1])
		next_number = last_number + 1
	else:
		next_number = 1
	
	# Generate serials for each asset
	for asset_id in asset_ids:
		if not frappe.db.exists("Asset", asset_id):
			frappe.throw(_("Asset {0} does not exist").format(asset_id))
		
		serial_number = f"ASSET-{year}-{month}-{next_number:05d}"
		
		# Update asset with new serial number
		frappe.db.set_value("Asset", asset_id, "serial_number", serial_number)
		generated_serials[asset_id] = serial_number
		next_number += 1
	
	frappe.db.commit()
	
	return {
		"status": "success",
		"message": _("Serial numbers generated successfully"),
		"generated_serials": generated_serials,
		"count": len(generated_serials)
	}


@frappe.whitelist()
def get_asset_by_ip_address(ip_address):
	"""
	Query assets by IP address.
	
	Args:
		ip_address: IP address to search for
	
	Returns:
		List of assets with matching IP addresses
	"""
	if not ip_address:
		frappe.throw(_("IP address is required"))
	
	# Validate IP format
	if not _is_valid_ip(ip_address):
		frappe.throw(_("Invalid IP address format"))
	
	# Query using child table
	assets = frappe.db.sql(
		"""
		SELECT DISTINCT a.name, a.asset_name, a.asset_category
		FROM tabAsset a
		INNER JOIN `tabAsset IP Address` ip ON a.name = ip.parent
		WHERE ip.ip_address = %s AND a.docstatus != 2
		""",
		(ip_address,),
		as_dict=True
	)
	
	return {
		"status": "success",
		"ip_address": ip_address,
		"assets": assets,
		"count": len(assets)
	}


@frappe.whitelist()
def get_asset_by_mac_address(mac_address):
	"""
	Query assets by MAC address.
	
	Args:
		mac_address: MAC address to search for (supports both : and - separators)
	
	Returns:
		List of assets with matching MAC addresses
	"""
	if not mac_address:
		frappe.throw(_("MAC address is required"))
	
	# Normalize MAC address
	mac_address = mac_address.replace('-', ':').upper()
	
	# Validate MAC format
	if not _is_valid_mac(mac_address):
		frappe.throw(_("Invalid MAC address format"))
	
	# Query using child table
	assets = frappe.db.sql(
		"""
		SELECT DISTINCT a.name, a.asset_name, a.asset_category
		FROM tabAsset a
		INNER JOIN `tabAsset MAC Address` mac ON a.name = mac.parent
		WHERE mac.mac_address = %s AND a.docstatus != 2
		""",
		(mac_address,),
		as_dict=True
	)
	
	return {
		"status": "success",
		"mac_address": mac_address,
		"assets": assets,
		"count": len(assets)
	}


@frappe.whitelist()
def get_asset_by_serial_number(serial_number):
	"""
	Query asset by serial number.
	
	Args:
		serial_number: Serial number to search for
	
	Returns:
		Asset details if found
	"""
	if not serial_number:
		frappe.throw(_("Serial number is required"))
	
	asset = frappe.db.get_value(
		"Asset",
		{"serial_number": serial_number, "docstatus": ["!=", 2]},
		["name", "asset_name", "asset_category", "status"],
		as_dict=True
	)
	
	if not asset:
		frappe.throw(_("Asset with serial number {0} not found").format(serial_number))
	
	return {
		"status": "success",
		"asset": asset
	}


@frappe.whitelist()
def get_asset_hierarchy(asset_id):
	"""
	Get asset hierarchy - parent and all children.
	
	Args:
		asset_id: Asset ID to get hierarchy for
	
	Returns:
		Asset hierarchy tree
	"""
	if not frappe.db.exists("Asset", asset_id):
		frappe.throw(_("Asset {0} does not exist").format(asset_id))
	
	asset = frappe.get_doc("Asset", asset_id)
	
	# Get all child assets
	children = frappe.db.get_list(
		"Asset",
		filters={"parent_system": asset_id, "docstatus": ["!=", 2]},
		fields=["name", "asset_name", "asset_category", "status"]
	)
	
	hierarchy = {
		"asset": {
			"name": asset.name,
			"asset_name": asset.asset_name,
			"asset_category": asset.asset_category,
			"status": asset.status,
			"parent_system": asset.parent_system if hasattr(asset, 'parent_system') else None
		},
		"children": children,
		"child_count": len(children)
	}
	
	return {
		"status": "success",
		"hierarchy": hierarchy
	}


@frappe.whitelist()
def link_asset_to_project(asset_id, project_id, role_in_project=None, date_assigned=None):
	"""
	Link an asset to a project.
	
	Args:
		asset_id: Asset ID
		project_id: Project ID
		role_in_project: Role of asset in project (optional)
		date_assigned: Date assigned (optional, defaults to today)
	
	Returns:
		Success status
	"""
	if not frappe.db.exists("Asset", asset_id):
		frappe.throw(_("Asset {0} does not exist").format(asset_id))
	
	if not frappe.db.exists("Project", project_id):
		frappe.throw(_("Project {0} does not exist").format(project_id))
	
	asset = frappe.get_doc("Asset", asset_id)
	
	# Check if already linked
	for project_link in asset.asset_projects:
		if project_link.project == project_id and not project_link.date_removed:
			frappe.throw(_("Asset is already linked to this project"))
	
	# Add new project link
	asset.append("asset_projects", {
		"project": project_id,
		"role_in_project": role_in_project,
		"date_assigned": date_assigned or getdate()
	})
	
	asset.save()
	
	return {
		"status": "success",
		"message": _("Asset linked to project successfully"),
		"asset": asset_id,
		"project": project_id
	}


@frappe.whitelist()
def unlink_asset_from_project(asset_id, project_id, date_removed=None):
	"""
	Unlink an asset from a project by setting date_removed.
	
	Args:
		asset_id: Asset ID
		project_id: Project ID
		date_removed: Date removed (optional, defaults to today)
	
	Returns:
		Success status
	"""
	if not frappe.db.exists("Asset", asset_id):
		frappe.throw(_("Asset {0} does not exist").format(asset_id))
	
	asset = frappe.get_doc("Asset", asset_id)
	
	# Find and update project link
	found = False
	for project_link in asset.asset_projects:
		if project_link.project == project_id and not project_link.date_removed:
			project_link.date_removed = date_removed or getdate()
			found = True
			break
	
	if not found:
		frappe.throw(_("Asset is not linked to this project or already unlinked"))
	
	asset.save()
	
	return {
		"status": "success",
		"message": _("Asset unlinked from project successfully"),
		"asset": asset_id,
		"project": project_id
	}


def _is_valid_ip(ip_address):
	"""Validate IP address format (IPv4 or IPv6)"""
	ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
	ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
	
	if re.match(ipv4_pattern, ip_address):
		octets = ip_address.split('.')
		return all(0 <= int(octet) <= 255 for octet in octets)
	
	return bool(re.match(ipv6_pattern, ip_address))


def _is_valid_mac(mac_address):
	"""Validate MAC address format"""
	mac_pattern = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
	return bool(re.match(mac_pattern, mac_address))


@frappe.whitelist()
def get_iot_devices():
	"""
	Get all assets marked as IoT devices (is_iot_device=1).

	Returns:
		List of IoT devices
	"""
	devices = frappe.db.get_list(
		"Asset",
		filters={"is_iot_device": 1, "docstatus": ["!=", 2]},
		fields=["name", "asset_name", "iot_device_id", "iot_platform",
				"communication_status", "last_communication", "status"],
		order_by="asset_name asc"
	)

	return {
		"status": "success",
		"devices": devices,
		"count": len(devices)
	}


@frappe.whitelist()
def get_asset_events(asset_id, event_type=None, days=7):
	"""
	⚠️ DEPRECATED: Use get_device_monitoring_info() instead.

	This endpoint is deprecated and will be removed in a future version.
	Asset Event Log is being replaced by Telemetry Event and Monitoring Alert.

	Migration Guide:
	1. Find the Monitored Device linked to this Asset
	2. Call get_device_monitoring_info(monitored_device_id) instead
	3. Use Monitoring Alert and Telemetry Event DocTypes for new events

	See: sigma.sigma_asset_integrations.api.monitoring_ingestion.get_device_monitoring_info

	Args:
		asset_id: Asset ID
		event_type: Filter by event type (optional)
		days: Number of days to look back (default 7)

	Returns:
		List of asset events
	"""
	# Log deprecation warning
	frappe.log_error(
		f"DEPRECATED API CALL: get_asset_events() called for Asset {asset_id}. "
		f"Please migrate to get_device_monitoring_info().",
		"Deprecated API Usage"
	)

	if not frappe.db.exists("Asset", asset_id):
		frappe.throw(_("Asset {0} does not exist").format(asset_id))

	# Try to find linked Monitored Device
	monitored_device = frappe.db.get_value("Monitored Device", {"asset": asset_id}, "name")

	if monitored_device:
		# Redirect to new endpoint
		from sigma.sigma_asset_integrations.api.monitoring_ingestion import get_device_monitoring_info
		result = get_device_monitoring_info(monitored_device_id=monitored_device, days=days)

		# Transform to old format for backward compatibility
		events = []

		# Add alerts as events
		for alert in result.get("alerts", []):
			events.append({
				"name": alert["name"],
				"event_type": "Alert",
				"event_timestamp": alert["timestamp"],
				"source": "Monitoring Alert",
				"alert_type": alert.get("alert_type"),
				"severity": alert.get("severity")
			})

		# Add telemetry as events
		for telem in result.get("telemetry", []):
			events.append({
				"name": telem["name"],
				"event_type": "Telemetry",
				"event_timestamp": telem["timestamp"],
				"source": "Telemetry Event",
				"metric_name": telem.get("metric_name"),
				"metric_value": telem.get("metric_value")
			})

		# Sort by timestamp
		events.sort(key=lambda x: x["event_timestamp"], reverse=True)

		return {
			"status": "success",
			"asset": asset_id,
			"monitored_device": monitored_device,
			"events": events,
			"count": len(events),
			"deprecation_warning": "This endpoint is deprecated. Use get_device_monitoring_info() instead."
		}

	# Legacy behavior: Query Asset Event Log
	filters = {"asset": asset_id}

	if event_type:
		filters["event_type"] = event_type

	# Add date filter
	from datetime import timedelta
	start_date = datetime.now() - timedelta(days=int(days))
	filters["event_timestamp"] = [">", start_date.isoformat()]

	events = frappe.db.get_list(
		"Asset Event Log",
		filters=filters,
		fields=["name", "event_type", "event_timestamp", "source",
				"latitude", "longitude", "altitude", "speed", "heading"],
		order_by="event_timestamp desc"
	)

	return {
		"status": "success",
		"asset": asset_id,
		"events": events,
		"count": len(events),
		"deprecation_warning": "This endpoint is deprecated. Create a Monitored Device and use get_device_monitoring_info() instead.",
		"migration_note": "No Monitored Device found for this Asset. Please create one and link it."
	}


@frappe.whitelist()
def update_asset_location(asset_id, latitude, longitude, altitude=None, speed=None, heading=None):
	"""
	⚠️ DEPRECATED: Use update_device_location() instead.

	This endpoint is deprecated and will be removed in a future version.
	Location tracking should be done via Monitored Device, not Asset.

	Migration Guide:
	1. Find the Monitored Device linked to this Asset
	2. Call update_device_location(monitored_device_id, ...) instead
	3. Location will automatically sync to Asset if linked

	See: sigma.sigma_asset_integrations.api.monitoring_ingestion.update_device_location

	Args:
		asset_id: Asset ID
		latitude: GPS latitude
		longitude: GPS longitude
		altitude: GPS altitude (optional)
		speed: Current speed (optional)
		heading: Current heading (optional)

	Returns:
		Updated asset (via Monitored Device if found)
	"""
	# Log deprecation warning
	frappe.log_error(
		f"DEPRECATED API CALL: update_asset_location() called for Asset {asset_id}. "
		f"Please migrate to update_device_location().",
		"Deprecated API Usage"
	)

	if not frappe.db.exists("Asset", asset_id):
		frappe.throw(_("Asset {0} does not exist").format(asset_id))

	# Try to find linked Monitored Device
	monitored_device = frappe.db.get_value("Monitored Device", {"asset": asset_id}, "name")

	if monitored_device:
		# Redirect to new endpoint
		from sigma.sigma_asset_integrations.api.monitoring_ingestion import update_device_location
		result = update_device_location(
			monitored_device_id=monitored_device,
			latitude=latitude,
			longitude=longitude,
			altitude=altitude,
			speed=speed,
			heading=heading
		)

		# Return in old format for backward compatibility
		return {
			"status": "success",
			"message": _("Asset location updated successfully (via Monitored Device)"),
			"asset": asset_id,
			"monitored_device": monitored_device,
			"latitude": latitude,
			"longitude": longitude,
			"deprecation_warning": "This endpoint is deprecated. Use update_device_location() instead."
		}
	else:
		# No Monitored Device found - provide clear error message
		frappe.throw(
			_("""No Monitored Device found for Asset {0}.

			This endpoint is deprecated. Please:
			1. Create a Monitored Device record
			2. Link it to this Asset via the 'asset' field
			3. Use update_device_location(monitored_device_id, ...) instead

			Location tracking must be done via Monitored Device, not Asset directly.""").format(asset_id)
		)


@frappe.whitelist()
def get_tracked_assets():
	"""
	Get all assets marked as tracked (is_tracked_asset=1).

	Returns:
		List of tracked assets
	"""
	assets = frappe.db.get_list(
		"Asset",
		filters={"is_tracked_asset": 1, "docstatus": ["!=", 2]},
		fields=["name", "asset_name", "latitude", "longitude", "altitude",
				"asset_location", "status"],
		order_by="asset_name asc"
	)

	return {
		"status": "success",
		"assets": assets,
		"count": len(assets)
	}


@frappe.whitelist()
def get_networked_assets():
	"""
	Get all assets marked as networked (is_networked_asset=1).

	Returns:
		List of networked assets
	"""
	assets = frappe.db.get_list(
		"Asset",
		filters={"is_networked_asset": 1, "docstatus": ["!=", 2]},
		fields=["name", "asset_name", "firmware_version", "status"],
		order_by="asset_name asc"
	)

	return {
		"status": "success",
		"assets": assets,
		"count": len(assets)
	}


@frappe.whitelist()
def get_location_based_asset_tree(asset_id=None, location_id=None):
	"""
	Get asset tree with locations as root nodes.
	If asset_id is provided, returns tree for that asset's location.
	If location_id is provided, returns tree for that specific location.
	If neither is provided, returns trees for all locations with assets.

	Args:
		asset_id: Optional - Asset ID to get location-based tree for
		location_id: Optional - Location ID to get tree for

	Returns:
		Tree structure with locations as root nodes, containing asset hierarchies
	"""
	# Determine which location(s) to fetch
	location_ids = []

	if asset_id:
		if not frappe.db.exists("Asset", asset_id):
			frappe.throw(_("Asset {0} does not exist").format(asset_id))
		asset = frappe.get_doc("Asset", asset_id)
		location_id = asset.get("asset_location")
		if not location_id:
			frappe.throw(_("Asset {0} does not have an installation location set").format(asset_id))
		location_ids = [location_id]
	elif location_id:
		if not frappe.db.exists("Location", location_id):
			frappe.throw(_("Location {0} does not exist").format(location_id))
		location_ids = [location_id]
	else:
		# Get all locations that have assets
		location_ids = frappe.db.sql_list("""
			SELECT DISTINCT asset_location
			FROM `tabAsset`
			WHERE asset_location IS NOT NULL
			AND asset_location != ''
			AND docstatus != 2
			ORDER BY asset_location
		""")

	# Build tree for each location
	location_trees = []
	total_asset_count = 0

	for loc_id in location_ids:
		location_tree = _build_location_tree_node(loc_id)
		if location_tree:
			location_trees.append(location_tree)
			total_asset_count += location_tree.get("asset_count", 0)

	return {
		"status": "success",
		"tree": location_trees,
		"location_count": len(location_trees),
		"total_asset_count": total_asset_count,
		"view_mode": "location_hierarchy"
	}


def _build_location_tree_node(location_id):
	"""
	Build a location node with all its assets organized in hierarchy.

	Args:
		location_id: Location ID to build node for

	Returns:
		Tree node with location details and asset children
	"""
	try:
		location = frappe.get_doc("Location", location_id)
	except Exception:
		return None

	# Get all root assets at this location (no parent_system)
	root_assets = frappe.db.get_list(
		"Asset",
		filters={
			"asset_location": location_id,
			"parent_system": ["is", "not set"],
			"docstatus": ["!=", 2]
		},
		fields=["name", "asset_name", "asset_category", "status", "parent_system"]
	)

	# Build tree for each root asset
	asset_nodes = []
	for root_asset in root_assets:
		node = _build_asset_tree_node(root_asset["name"])
		asset_nodes.append(node)

	# Count total assets (including children)
	total_assets = _count_assets_recursive(asset_nodes)

	return {
		"id": location.name,
		"name": location.location_name,
		"type": "location",
		"location_type": location.get("location_type"),
		"parent_location": location.get("parent_location"),
		"children": asset_nodes,
		"child_count": len(asset_nodes),
		"asset_count": total_assets
	}


def _count_assets_recursive(nodes):
	"""Count total assets including all children recursively."""
	count = len(nodes)
	for node in nodes:
		if node.get("children"):
			count += _count_assets_recursive(node["children"])
	return count


@frappe.whitelist()
def get_locations_for_tree():
	"""
	Get all locations with asset counts for tree view root level.
	Returns locations as tree nodes.
	"""
	# Get all locations that have assets
	locations = frappe.db.sql("""
		SELECT
			l.name,
			l.location_name,
			l.location_type,
			COUNT(DISTINCT a.name) as asset_count
		FROM `tabLocation` l
		LEFT JOIN `tabAsset` a ON a.asset_location = l.name AND a.docstatus != 2
		GROUP BY l.name, l.location_name, l.location_type
		HAVING asset_count > 0
		ORDER BY l.location_name
	""", as_dict=True)

	return locations


@frappe.whitelist()
def get_assets_at_location(location_id, parent_asset=None):
	"""
	Get assets at a specific location, optionally filtered by parent.

	Args:
		location_id: Location ID
		parent_asset: Parent asset ID (None for root assets)

	Returns:
		List of assets with has_children flag
	"""
	filters = {
		"asset_location": location_id,
		"docstatus": ["!=", 2]
	}

	if parent_asset:
		filters["parent_asset"] = parent_asset
	else:
		# Get root assets (no parent)
		filters["parent_asset"] = ["is", "not set"]

	assets = frappe.db.get_list(
		"Asset",
		filters=filters,
		fields=["name", "asset_name", "asset_category", "status"],
		order_by="asset_name"
	)

	# Check if each asset has children
	for asset in assets:
		child_count = frappe.db.count(
			"Asset",
			filters={
				"parent_asset": asset["name"],
				"docstatus": ["!=", 2]
			}
		)
		asset["has_children"] = child_count > 0

	return assets


@frappe.whitelist()
def get_tree_nodes_with_location(doctype="Asset", parent="", is_root=False, **filters):
	"""
	Custom tree node fetcher that organizes assets by location.
	This method is called by Frappe's tree view to get child nodes.

	Args:
		doctype: Always "Asset" (default)
		parent: Parent node value (default: "")
		is_root: Whether this is the root level (default: False)
		**filters: Additional filters

	Returns:
		List of tree nodes in Frappe tree format
	"""
	# Convert string boolean to actual boolean if needed
	if isinstance(is_root, str):
		is_root = is_root.lower() in ('true', '1', 'yes')

	# Check if location hierarchy mode is enabled (stored in session or always on)
	location_mode = frappe.session.get("asset_tree_location_mode", True)

	if not location_mode:
		# Use standard tree view
		return frappe.desk.treeview.get_children(doctype, parent, is_root, **filters)

	# Location hierarchy mode
	if is_root or parent == "All Assets" or not parent or parent == "":
		# Root level - return all locations as nodes
		locations = get_locations_for_tree()
		return [
			{
				"value": f"location_{loc['name']}",
				"title": loc["location_name"],
				"expandable": True,
				"is_location": True,
				"location_type": loc.get("location_type"),
				"asset_count": loc.get("asset_count", 0)
			}
			for loc in locations
		]

	elif parent.startswith("location_"):
		# Location node - return root assets at this location
		location_id = parent.replace("location_", "")
		assets = get_assets_at_location(location_id)
		return [
			{
				"value": asset["name"],
				"title": asset["asset_name"],
				"expandable": asset.get("has_children", False),
				"is_location": False
			}
			for asset in assets
		]

	else:
		# Asset node - return child assets using standard method
		return frappe.desk.treeview.get_children(doctype, parent, False, **filters)


def _build_asset_tree_node(asset_id):
	"""
	Recursively build asset tree node with all children.

	Args:
		asset_id: Asset ID to build node for

	Returns:
		Tree node with asset details and children
	"""
	asset = frappe.get_doc("Asset", asset_id)

	# Get all child assets
	children = frappe.db.get_list(
		"Asset",
		filters={"parent_system": asset_id, "docstatus": ["!=", 2]},
		fields=["name", "asset_name", "asset_category", "status"]
	)

	# Recursively build child nodes
	child_nodes = []
	for child in children:
		child_node = _build_asset_tree_node(child["name"])
		child_nodes.append(child_node)

	return {
		"id": asset.name,
		"name": asset.asset_name,
		"category": asset.asset_category,
		"status": asset.status,
		"location": asset.get("asset_location"),
		"installation_point": asset.get("installation_point"),
		"parent_system": asset.get("parent_system"),
		"children": child_nodes,
		"child_count": len(child_nodes)
	}


@frappe.whitelist()
def get_asset_maintenance_info(asset_id):
	"""
	Get maintenance information for an asset

	Args:
		asset_id: Asset ID

	Returns:
		dict: Maintenance information including schedules, logs, and upcoming maintenance
	"""
	try:
		# Get Asset Maintenance records
		maintenance_records = frappe.get_all(
			"Asset Maintenance",
			filters={"asset_name": asset_id, "docstatus": 1},
			fields=["name", "maintenance_status", "maintenance_team", "company"]
		)

		maintenance_info = []
		upcoming_tasks = []
		maintenance_history = []

		for record in maintenance_records:
			# Get maintenance tasks for this record
			tasks = frappe.get_all(
				"Asset Maintenance Task",
				filters={"parent": record.name},
				fields=[
					"name", "maintenance_task", "maintenance_type",
					"periodicity", "start_date", "end_date", "next_due_date",
					"last_completion_date", "maintenance_status"
				],
				order_by="next_due_date ASC"
			)

			for task in tasks:
				task_info = {
					"maintenance_id": record.name,
					"task_name": task.maintenance_task,
					"task_type": task.maintenance_type,
					"periodicity": task.periodicity,
					"next_due_date": task.next_due_date,
					"last_completion": task.last_completion_date,
					"status": task.maintenance_status
				}

				# Categorize as upcoming if next_due_date is in the future
				if task.next_due_date:
					from frappe.utils import getdate, today
					if getdate(task.next_due_date) >= getdate(today()):
						upcoming_tasks.append(task_info)

				maintenance_info.append(task_info)

		# Get maintenance logs (history)
		logs = frappe.get_all(
			"Asset Maintenance Log",
			filters={"asset_name": asset_id},
			fields=[
				"name", "task", "maintenance_status", "completion_date",
				"actions_performed", "due_date"
			],
			order_by="completion_date DESC",
			limit=10
		)

		for log in logs:
			maintenance_history.append({
				"log_id": log.name,
				"task": log.task,
				"status": log.maintenance_status,
				"completion_date": log.completion_date,
				"due_date": log.due_date,
				"actions": log.actions_performed
			})

		return {
			"has_maintenance": len(maintenance_records) > 0,
			"maintenance_count": len(maintenance_records),
			"upcoming_tasks": upcoming_tasks,
			"upcoming_count": len(upcoming_tasks),
			"all_tasks": maintenance_info,
			"history": maintenance_history,
			"history_count": len(maintenance_history)
		}

	except Exception as e:
		frappe.log_error(f"Failed to get maintenance info for asset {asset_id}: {str(e)}")
		return {
			"has_maintenance": False,
			"maintenance_count": 0,
			"upcoming_tasks": [],
			"upcoming_count": 0,
			"all_tasks": [],
			"history": [],
			"history_count": 0,
			"error": str(e)
		}


@frappe.whitelist()
def get_asset_iot_info(asset_id):
	"""
	⚠️ DEPRECATED: Use get_device_monitoring_info() instead.

	This endpoint is deprecated and will be removed in a future version.
	Monitoring information should be retrieved via Monitored Device, not Asset.

	Migration Guide:
	1. Find the Monitored Device linked to this Asset
	2. Call get_device_monitoring_info(monitored_device_id) instead

	See: sigma.sigma_asset_integrations.api.monitoring_ingestion.get_device_monitoring_info

	Args:
		asset_id: Asset ID

	Returns:
		dict: IoT device info, status, and recent alerts
	"""
	# Log deprecation warning
	frappe.log_error(
		f"DEPRECATED API CALL: get_asset_iot_info() called for Asset {asset_id}. "
		f"Please migrate to get_device_monitoring_info().",
		"Deprecated API Usage"
	)

	try:
		# Try to find linked Monitored Device
		monitored_device = frappe.db.get_value("Monitored Device", {"asset": asset_id}, "name")

		if monitored_device:
			# Redirect to new endpoint
			from sigma.sigma_asset_integrations.api.monitoring_ingestion import get_device_monitoring_info
			result = get_device_monitoring_info(monitored_device_id=monitored_device)

			# Add deprecation warning to result
			result["deprecation_warning"] = "This endpoint is deprecated. Use get_device_monitoring_info() instead."
			result["monitored_device"] = monitored_device

			return result

		# No Monitored Device found - check if asset is marked as IoT device
		asset = frappe.get_doc("Asset", asset_id)

		if not asset.get("is_iot_device"):
			return {
				"is_iot_device": False,
				"device_id": None,
				"status": None,
				"alerts": [],
				"alert_count": 0,
				"deprecation_warning": "This endpoint is deprecated. Use get_device_monitoring_info() instead."
			}

		# Legacy behavior: Get recent Asset Event Logs for this asset
		# This is kept for backward compatibility but should not be used
		event_logs = frappe.get_all(
			"Asset Event Log",
			filters={"asset": asset_id, "event_type": "Alert"},
			fields=[
				"name", "event_timestamp", "source", "event_data",
				"latitude", "longitude", "processed"
			],
			order_by="event_timestamp DESC",
			limit=10
		)

		alerts = []
		for log in event_logs:
			alert_data = {}
			if log.event_data:
				import json
				try:
					alert_data = json.loads(log.event_data)
				except:
					pass

			alerts.append({
				"event_id": log.name,
				"timestamp": log.event_timestamp,
				"alert_type": alert_data.get("alert_type", "Unknown"),
				"severity": alert_data.get("severity", "Unknown"),
				"sensor_value": alert_data.get("sensor_value"),
				"latitude": log.latitude,
				"longitude": log.longitude,
				"processed": log.processed,
				"source": log.source
			})

		# Determine device status based on recent activity
		device_status = "Unknown"
		if event_logs:
			from frappe.utils import get_datetime, now_datetime
			last_event_time = get_datetime(event_logs[0].event_timestamp)
			time_diff = (now_datetime() - last_event_time).total_seconds() / 3600  # hours

			if time_diff < 1:
				device_status = "Online"
			elif time_diff < 24:
				device_status = "Active"
			else:
				device_status = "Offline"

		return {
			"is_iot_device": True,
			"device_id": asset.get("iot_device_id"),
			"status": device_status,
			"alerts": alerts,
			"alert_count": len(alerts),
			"unprocessed_count": sum(1 for a in alerts if not a["processed"]),
			"deprecation_warning": "This endpoint is deprecated. Create a Monitored Device and use get_device_monitoring_info() instead.",
			"migration_note": "No Monitored Device found for this Asset. Please create one and link it."
		}

	except Exception as e:
		frappe.log_error(f"Failed to get IoT info for asset {asset_id}: {str(e)}")
		return {
			"is_iot_device": False,
			"device_id": None,
			"status": "Error",
			"alerts": [],
			"alert_count": 0,
			"error": str(e)
		}


@frappe.whitelist()
def get_asset_case_info(asset_id):
	"""
	Get case/issue information for an asset

	Args:
		asset_id: Asset ID

	Returns:
		dict: Open cases, case history, and case statistics
	"""
	try:
		# Get cases linked to this asset (using custom field or description search)
		# Note: This assumes cases have a custom field 'asset' or mention asset in subject
		open_cases = frappe.get_all(
			"Case",
			filters={
				"status": ["in", ["Open", "In Progress", "Pending"]],
				"subject": ["like", f"%{asset_id}%"]
			},
			fields=[
				"name", "subject", "status", "priority", "creation",
				"modified", "owner"
			],
			order_by="creation DESC",
			limit=10
		)

		closed_cases = frappe.get_all(
			"Case",
			filters={
				"status": ["in", ["Closed", "Resolved"]],
				"subject": ["like", f"%{asset_id}%"]
			},
			fields=[
				"name", "subject", "status", "priority", "creation",
				"modified", "resolution_date"
			],
			order_by="modified DESC",
			limit=10
		)

		# Also check for Issues (Frappe's built-in Issue doctype)
		open_issues = frappe.get_all(
			"Issue",
			filters={
				"status": ["in", ["Open", "Replied", "Hold"]],
				"subject": ["like", f"%{asset_id}%"]
			},
			fields=[
				"name", "subject", "status", "priority", "creation",
				"modified", "owner"
			],
			order_by="creation DESC",
			limit=10
		)

		closed_issues = frappe.get_all(
			"Issue",
			filters={
				"status": ["in", ["Closed", "Resolved"]],
				"subject": ["like", f"%{asset_id}%"]
			},
			fields=[
				"name", "subject", "status", "priority", "creation",
				"modified", "resolution_date"
			],
			order_by="modified DESC",
			limit=10
		)

		# Combine cases and issues
		all_open = []
		for case in open_cases:
			all_open.append({
				"id": case.name,
				"type": "Case",
				"subject": case.subject,
				"status": case.status,
				"priority": case.priority,
				"created": case.creation,
				"modified": case.modified,
				"owner": case.owner
			})

		for issue in open_issues:
			all_open.append({
				"id": issue.name,
				"type": "Issue",
				"subject": issue.subject,
				"status": issue.status,
				"priority": issue.priority,
				"created": issue.creation,
				"modified": issue.modified,
				"owner": issue.owner
			})

		all_closed = []
		for case in closed_cases:
			all_closed.append({
				"id": case.name,
				"type": "Case",
				"subject": case.subject,
				"status": case.status,
				"priority": case.priority,
				"created": case.creation,
				"resolution_date": case.get("resolution_date")
			})

		for issue in closed_issues:
			all_closed.append({
				"id": issue.name,
				"type": "Issue",
				"subject": issue.subject,
				"status": issue.status,
				"priority": issue.priority,
				"created": issue.creation,
				"resolution_date": issue.get("resolution_date")
			})

		return {
			"has_cases": len(all_open) > 0 or len(all_closed) > 0,
			"open_cases": all_open,
			"open_count": len(all_open),
			"closed_cases": all_closed,
			"closed_count": len(all_closed),
			"total_count": len(all_open) + len(all_closed)
		}

	except Exception as e:
		frappe.log_error(f"Failed to get case info for asset {asset_id}: {str(e)}")
		return {
			"has_cases": False,
			"open_cases": [],
			"open_count": 0,
			"closed_cases": [],
			"closed_count": 0,
			"total_count": 0,
			"error": str(e)
		}

