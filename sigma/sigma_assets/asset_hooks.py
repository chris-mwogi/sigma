# Copyright (c) 2025, Sigma Security Management System
# License: MIT

"""
Asset DocType Hooks
Handles automatic serial number generation and other Asset-related operations.
"""

import frappe
from datetime import datetime


def auto_generate_serial_number(doc, method):
	"""
	Auto-generate serial number if not provided.
	Format: ASSET-{YYYY}-{MM}-{NNNNN}
	
	Called on Asset before_insert and before_save hooks.
	"""
	if doc.docstatus == 0 and not doc.serial_number:
		doc.serial_number = _generate_unique_serial_number()


def validate_gps_coordinates(doc, method):
	"""
	Validate GPS coordinates are within valid ranges.
	Latitude: -90 to 90
	Longitude: -180 to 180
	"""
	if hasattr(doc, 'latitude') and doc.latitude:
		if not (-90 <= doc.latitude <= 90):
			frappe.throw("Latitude must be between -90 and 90")
	
	if hasattr(doc, 'longitude') and doc.longitude:
		if not (-180 <= doc.longitude <= 180):
			frappe.throw("Longitude must be between -180 and 180")


def validate_parent_system(doc, method):
	"""
	Validate that parent_system is not the same as the asset itself.
	Prevent circular references.
	"""
	if hasattr(doc, 'parent_system') and doc.parent_system:
		if doc.parent_system == doc.name:
			frappe.throw("An asset cannot be its own parent system")
		
		# Check for circular references
		if _has_circular_reference(doc.name, doc.parent_system):
			frappe.throw("Circular reference detected in parent system hierarchy")


def _generate_unique_serial_number():
	"""Generate a unique serial number in format ASSET-{YYYY}-{MM}-{NNNNN}"""
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
	
	return f"ASSET-{year}-{month}-{next_number:05d}"


def _has_circular_reference(asset_id, parent_id, visited=None):
	"""
	Check if there's a circular reference in the parent system hierarchy.
	"""
	if visited is None:
		visited = set()
	
	if parent_id in visited:
		return True
	
	visited.add(parent_id)
	
	# Get parent's parent
	parent_asset = frappe.db.get_value(
		"Asset",
		parent_id,
		"parent_system"
	)
	
	if not parent_asset:
		return False
	
	if parent_asset == asset_id:
		return True
	
	return _has_circular_reference(asset_id, parent_asset, visited)

