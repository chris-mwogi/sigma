# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

"""
REST API endpoints for Personnel Tracking Module (PTM)
Provides IoT/Mobile integration for check-in, check-out, location tracking, and alerts
"""

import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=False)
def check_in(human, entry_gate, method, device_id=None, initial_zone=None, ppe_verification_status="Not Verified", purpose_of_visit=""):
	"""
	API endpoint for personnel check-in.
	
	Args:
		human: Human Profile ID
		entry_gate: Gate name
		method: Check-in method (RFID, Biometric, Mobile App, Manual)
		device_id: Tracking device ID (optional)
		initial_zone: Initial zone code (optional)
		ppe_verification_status: PPE verification status
		purpose_of_visit: Purpose of visit
	
	Returns:
		dict: Check-in document details
	"""
	try:
		# Validate human profile exists and is active
		human_doc = frappe.get_doc("Human Profile", human)
		if human_doc.docstatus != 1:
			frappe.throw(_("Human Profile {0} is not submitted").format(human))
		if human_doc.status != "Active":
			frappe.throw(_("Human Profile {0} is not active").format(human))
		
		# Check if already checked in
		existing_checkin = frappe.db.exists("Personnel Check-In", {
			"human": human,
			"docstatus": 1
		})
		
		if existing_checkin:
			# Check if there's a checkout
			existing_checkout = frappe.db.exists("Personnel Check-Out", {
				"related_check_in": existing_checkin,
				"docstatus": 1
			})
			if not existing_checkout:
				frappe.throw(_("Personnel {0} is already checked in").format(human_doc.full_name))
		
		# Create check-in
		checkin = frappe.get_doc({
			"doctype": "Personnel Check-In",
			"human": human,
			"timestamp_in": now_datetime(),
			"entry_gate": entry_gate,
			"method": method,
			"device_id": device_id or human_doc.primary_tracking_device,
			"initial_zone": initial_zone,
			"ppe_verification_status": ppe_verification_status,
			"purpose_of_visit": purpose_of_visit
		})
		
		checkin.insert(ignore_permissions=True)
		checkin.submit()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Check-in successful for {0}").format(human_doc.full_name),
			"checkin_id": checkin.name,
			"timestamp": checkin.timestamp_in,
			"zone": checkin.initial_zone
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Personnel Check-In API Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist(allow_guest=False)
def check_out(human, exit_gate, method, incident_note=""):
	"""
	API endpoint for personnel check-out.
	
	Args:
		human: Human Profile ID
		exit_gate: Gate name
		method: Check-out method (RFID, Biometric, Mobile App, Manual)
		incident_note: Any incident notes (optional)
	
	Returns:
		dict: Check-out document details
	"""
	try:
		# Find active check-in
		checkin = frappe.get_all("Personnel Check-In",
			filters={"human": human, "docstatus": 1},
			fields=["name", "timestamp_in"],
			order_by="timestamp_in desc",
			limit=1
		)
		
		if not checkin:
			frappe.throw(_("No active check-in found for {0}").format(human))
		
		checkin_name = checkin[0].name
		
		# Check if already checked out
		existing_checkout = frappe.db.exists("Personnel Check-Out", {
			"related_check_in": checkin_name,
			"docstatus": 1
		})
		
		if existing_checkout:
			frappe.throw(_("Personnel {0} is already checked out").format(human))
		
		# Create checkout
		checkout = frappe.get_doc({
			"doctype": "Personnel Check-Out",
			"human": human,
			"related_check_in": checkin_name,
			"timestamp_out": now_datetime(),
			"exit_gate": exit_gate,
			"method": method,
			"incident_note": incident_note
		})
		
		checkout.insert(ignore_permissions=True)
		checkout.submit()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Check-out successful"),
			"checkout_id": checkout.name,
			"timestamp": checkout.timestamp_out,
			"duration_onsite": checkout.duration_onsite
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Personnel Check-Out API Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist(allow_guest=False)
def log_location(human, zone, source_type, source_id, confidence=100.0, latitude=None, longitude=None):
	"""
	API endpoint for logging personnel location events.
	
	Args:
		human: Human Profile ID
		zone: Zone Configuration code
		source_type: Source type (RFID, BLE, GPS, CCTV, Manual)
		source_id: Source device/system ID
		confidence: Confidence level (0-100)
		latitude: GPS latitude (optional)
		longitude: GPS longitude (optional)
	
	Returns:
		dict: Location event details
	"""
	try:
		# Create location event
		location_event = frappe.get_doc({
			"doctype": "Human Location Event",
			"human": human,
			"timestamp": now_datetime(),
			"zone": zone,
			"source_type": source_type,
			"source_id": source_id,
			"confidence": float(confidence),
			"latitude": latitude,
			"longitude": longitude
		})
		
		location_event.insert(ignore_permissions=True)
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Location logged successfully"),
			"location_event_id": location_event.name,
			"timestamp": location_event.timestamp
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Location Logging API Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist(allow_guest=False)
def trigger_panic_button(human, device_id, zone=None, latitude=None, longitude=None):
	"""
	API endpoint for triggering panic button alert.

	Args:
		human: Human Profile ID
		device_id: Panic button device ID
		zone: Current zone (optional)
		latitude: GPS latitude (optional)
		longitude: GPS longitude (optional)

	Returns:
		dict: Alert details
	"""
	try:
		# Get current zone if not provided
		if not zone:
			presence = frappe.get_all("Zone Presence",
				filters={"human": human, "status": "Active"},
				fields=["zone"],
				limit=1
			)
			if presence:
				zone = presence[0].zone

		# Create lone worker alert
		alert = frappe.get_doc({
			"doctype": "Lone Worker Alert",
			"human": human,
			"alert_type": "Panic Button",
			"raised_at": now_datetime(),
			"zone": zone,
			"severity": "Critical",
			"resolution_status": "Open"
		})

		alert.insert(ignore_permissions=True)
		frappe.db.commit()

		# Log location event if coordinates provided
		if latitude and longitude:
			location_event = frappe.get_doc({
				"doctype": "Human Location Event",
				"human": human,
				"timestamp": now_datetime(),
				"zone": zone,
				"source_type": "Panic Button",
				"source_id": device_id,
				"confidence": 100.0,
				"latitude": latitude,
				"longitude": longitude
			})
			location_event.insert(ignore_permissions=True)
			frappe.db.commit()

		return {
			"success": True,
			"message": _("Panic alert triggered - Emergency response initiated"),
			"alert_id": alert.name,
			"severity": "Critical",
			"timestamp": alert.raised_at
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Panic Button API Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist(allow_guest=False)
def get_zone_occupancy(zone):
	"""
	API endpoint for getting current zone occupancy.

	Args:
		zone: Zone Configuration code

	Returns:
		dict: Zone occupancy details
	"""
	try:
		zone_doc = frappe.get_doc("Zone Configuration", zone)

		# Get current occupancy
		current_occupancy = frappe.db.count("Zone Presence", {
			"zone": zone,
			"status": "Active"
		})

		# Get list of personnel in zone
		personnel = frappe.get_all("Zone Presence",
			filters={"zone": zone, "status": "Active"},
			fields=["human", "time_entered", "last_seen"],
			order_by="time_entered"
		)

		personnel_list = []
		for p in personnel:
			human_doc = frappe.get_doc("Human Profile", p.human)
			personnel_list.append({
				"human_id": p.human,
				"full_name": human_doc.full_name,
				"clearance_level": human_doc.clearance_level,
				"time_entered": p.time_entered,
				"last_seen": p.last_seen
			})

		return {
			"success": True,
			"zone": zone,
			"zone_name": zone_doc.zone_name,
			"current_occupancy": current_occupancy,
			"max_occupancy": zone_doc.max_occupancy,
			"capacity_percentage": (current_occupancy / zone_doc.max_occupancy * 100) if zone_doc.max_occupancy > 0 else 0,
			"at_capacity": current_occupancy >= zone_doc.max_occupancy,
			"personnel": personnel_list
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Zone Occupancy API Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist(allow_guest=False)
def get_personnel_status(human):
	"""
	API endpoint for getting personnel current status.

	Args:
		human: Human Profile ID

	Returns:
		dict: Personnel status details
	"""
	try:
		human_doc = frappe.get_doc("Human Profile", human)

		# Check if checked in
		checkin = frappe.get_all("Personnel Check-In",
			filters={"human": human, "docstatus": 1},
			fields=["name", "timestamp_in", "entry_gate"],
			order_by="timestamp_in desc",
			limit=1
		)

		is_onsite = False
		checkin_time = None
		entry_gate = None

		if checkin:
			# Check if checked out
			checkout = frappe.db.exists("Personnel Check-Out", {
				"related_check_in": checkin[0].name,
				"docstatus": 1
			})
			if not checkout:
				is_onsite = True
				checkin_time = checkin[0].timestamp_in
				entry_gate = checkin[0].entry_gate

		# Get current location
		current_zone = None
		if is_onsite:
			presence = frappe.get_all("Zone Presence",
				filters={"human": human, "status": "Active"},
				fields=["zone", "time_entered", "last_seen"],
				limit=1
			)
			if presence:
				current_zone = presence[0].zone

		# Get active alerts
		active_alerts = frappe.get_all("Lone Worker Alert",
			filters={"human": human, "resolution_status": ["in", ["Open", "Acknowledged"]]},
			fields=["name", "alert_type", "severity", "raised_at"]
		)

		return {
			"success": True,
			"human_id": human,
			"full_name": human_doc.full_name,
			"status": human_doc.status,
			"clearance_level": human_doc.clearance_level,
			"is_onsite": is_onsite,
			"checkin_time": checkin_time,
			"entry_gate": entry_gate,
			"current_zone": current_zone,
			"active_alerts": active_alerts,
			"tracking_enabled": human_doc.tracking_enabled
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Personnel Status API Error")
		return {
			"success": False,
			"message": str(e)
		}

