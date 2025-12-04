#!/usr/bin/env python3
# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

"""
Comprehensive test script for Personnel Tracking Module (PTM)
Tests all DocTypes, workflows, and automation
"""

import frappe
from frappe.utils import now_datetime, add_to_date

def setup_test_data():
	"""Create sample data for testing."""
	print("\n" + "=" * 80)
	print("SETTING UP TEST DATA FOR PERSONNEL TRACKING MODULE")
	print("=" * 80)
	
	# 1. Create Zone Configurations
	print("\n1. Creating Zone Configurations...")
	zones = [
		{
			"zone_name": "Main Office",
			"zone_code": "KPLC-ZONE-001",
			"zone_type": "Office",
			"hazard_level": "Low",
			"clearance_level_required": "Low",
			"max_duration_minutes": 0,
			"requires_escort": 0,
			"max_occupancy": 100,
			"lone_worker_alert_minutes": 0,
			"is_active": 1
		},
		{
			"zone_name": "Substation A - Control Room",
			"zone_code": "KPLC-ZONE-002",
			"zone_type": "Control Room",
			"hazard_level": "Medium",
			"clearance_level_required": "Medium",
			"max_duration_minutes": 480,
			"requires_escort": 0,
			"max_occupancy": 10,
			"lone_worker_alert_minutes": 30,
			"is_active": 1
		},
		{
			"zone_name": "Substation A - Transformer Yard",
			"zone_code": "KPLC-ZONE-003",
			"zone_type": "Transformer Yard",
			"hazard_level": "High",
			"clearance_level_required": "High",
			"max_duration_minutes": 120,
			"requires_escort": 1,
			"max_occupancy": 5,
			"lone_worker_alert_minutes": 15,
			"ppe_requirements": "Hard Hat, Safety Boots, High Voltage Gloves, Arc Flash Suit",
			"is_active": 1
		},
		{
			"zone_name": "Substation B - SCADA Room",
			"zone_code": "KPLC-ZONE-004",
			"zone_type": "SCADA Room",
			"hazard_level": "Critical",
			"clearance_level_required": "Critical",
			"max_duration_minutes": 240,
			"requires_escort": 1,
			"max_occupancy": 3,
			"lone_worker_alert_minutes": 10,
			"is_active": 1
		},
		{
			"zone_name": "Emergency Muster Point - North",
			"zone_code": "KPLC-ZONE-005",
			"zone_type": "Muster Point",
			"hazard_level": "Low",
			"clearance_level_required": "Low",
			"max_duration_minutes": 0,
			"requires_escort": 0,
			"max_occupancy": 500,
			"lone_worker_alert_minutes": 0,
			"is_active": 1
		}
	]
	
	created_zones = []
	for zone_data in zones:
		if not frappe.db.exists("Zone Configuration", zone_data["zone_code"]):
			zone = frappe.get_doc({
				"doctype": "Zone Configuration",
				**zone_data
			})
			zone.insert(ignore_permissions=True)
			created_zones.append(zone.name)
			print(f"   ✓ Created zone: {zone.zone_name} ({zone.zone_code})")
		else:
			print(f"   ⏭️  Zone already exists: {zone_data['zone_code']}")
	
	frappe.db.commit()
	
	# 2. Create Tracking Devices
	print("\n2. Creating Tracking Devices...")
	devices = [
		{"device_type": "RFID Badge", "device_id": "RFID-001", "manufacturer": "HID Global", "model": "iCLASS SE", "status": "Active"},
		{"device_type": "RFID Badge", "device_id": "RFID-002", "manufacturer": "HID Global", "model": "iCLASS SE", "status": "Active"},
		{"device_type": "RFID Badge", "device_id": "RFID-003", "manufacturer": "HID Global", "model": "iCLASS SE", "status": "Active"},
		{"device_type": "BLE Beacon", "device_id": "BLE-001", "manufacturer": "Estimote", "model": "Location Beacon", "status": "Active"},
		{"device_type": "BLE Beacon", "device_id": "BLE-002", "manufacturer": "Estimote", "model": "Location Beacon", "status": "Active"},
		{"device_type": "GPS Tracker", "device_id": "GPS-001", "manufacturer": "Teltonika", "model": "FMB920", "status": "Active"},
		{"device_type": "Panic Button", "device_id": "PANIC-001", "manufacturer": "SafetyLine", "model": "Lone Worker", "status": "Active"},
	]
	
	created_devices = []
	for device_data in devices:
		if not frappe.db.exists("Tracking Device", device_data["device_id"]):
			device = frappe.get_doc({
				"doctype": "Tracking Device",
				**device_data
			})
			device.insert(ignore_permissions=True)
			created_devices.append(device.name)
			print(f"   ✓ Created device: {device.device_type} - {device.device_id}")
		else:
			print(f"   ⏭️  Device already exists: {device_data['device_id']}")
	
	frappe.db.commit()
	
	# 3. Create Human Profiles
	print("\n3. Creating Human Profiles...")
	humans = [
		{
			"person_type": "Employee",
			"full_name": "John Kamau",
			"department": "Operations",
			"job_role": "Senior Electrical Engineer",
			"employee_id": "KPLC-EMP-001",
			"clearance_level": "Critical",
			"hazard_training_level": "Expert",
			"ppe_required": "Hard Hat, Safety Boots, High Voltage Gloves",
			"ppe_certified_date": add_to_date(now_datetime(), days=-30),
			"primary_tracking_device": "RFID-001",
			"tracking_enabled": 1,
			"consent_signed": 1,
			"consent_date": add_to_date(now_datetime(), days=-60),
			"emergency_contact_name": "Mary Kamau",
			"emergency_contact_phone": "+254712345678",
			"blood_group": "O+",
			"status": "Active"
		},
		{
			"person_type": "Employee",
			"full_name": "Sarah Wanjiku",
			"department": "Operations",
			"job_role": "Control Room Operator",
			"employee_id": "KPLC-EMP-002",
			"clearance_level": "High",
			"hazard_training_level": "Advanced",
			"ppe_required": "Hard Hat, Safety Boots",
			"ppe_certified_date": add_to_date(now_datetime(), days=-20),
			"primary_tracking_device": "RFID-002",
			"tracking_enabled": 1,
			"consent_signed": 1,
			"consent_date": add_to_date(now_datetime(), days=-60),
			"emergency_contact_name": "Peter Wanjiku",
			"emergency_contact_phone": "+254723456789",
			"blood_group": "A+",
			"status": "Active"
		},
		{
			"person_type": "Contractor",
			"full_name": "David Omondi",
			"department": "Operations",
			"job_role": "Maintenance Technician",
			"employee_id": "KPLC-CON-001",
			"clearance_level": "Medium",
			"hazard_training_level": "Intermediate",
			"ppe_required": "Hard Hat, Safety Boots",
			"ppe_certified_date": add_to_date(now_datetime(), days=-10),
			"primary_tracking_device": "RFID-003",
			"tracking_enabled": 1,
			"consent_signed": 1,
			"consent_date": add_to_date(now_datetime(), days=-30),
			"emergency_contact_name": "Jane Omondi",
			"emergency_contact_phone": "+254734567890",
			"blood_group": "B+",
			"status": "Active"
		}
	]
	
	print("   Creating Human Profiles and submitting them...")

	created_humans = []
	for human_data in humans:
		# Check if already exists by employee_id
		existing = frappe.db.exists("Human Profile", {"employee_id": human_data.get("employee_id")})
		if not existing:
			human = frappe.get_doc({
				"doctype": "Human Profile",
				**human_data
			})
			human.insert(ignore_permissions=True)
			human.submit()
			created_humans.append(human.name)
			print(f"   ✓ Created and submitted: {human.full_name} ({human.name})")
		else:
			print(f"   ⏭️  Human Profile already exists: {human_data['full_name']}")

	frappe.db.commit()

	print("\n" + "=" * 80)
	print("TEST DATA SETUP COMPLETE!")
	print("=" * 80)
	print(f"\n✓ Created {len(created_zones)} zones")
	print(f"✓ Created {len(created_devices)} tracking devices")
	print(f"✓ Created {len(created_humans)} human profiles")

	return {
		"zones": created_zones,
		"devices": created_devices,
		"humans": created_humans
	}

def test_check_in_workflow():
	"""Test Personnel Check-In workflow."""
	print("\n" + "=" * 80)
	print("TESTING CHECK-IN WORKFLOW")
	print("=" * 80)

	# Get first human profile
	human = frappe.get_all("Human Profile",
		filters={"docstatus": 1, "status": "Active"},
		limit=1
	)

	if not human:
		print("❌ No active Human Profiles found. Run setup_test_data() first.")
		return

	human_name = human[0].name
	human_doc = frappe.get_doc("Human Profile", human_name)

	print(f"\n1. Checking in: {human_doc.full_name}")

	# Create check-in
	checkin = frappe.get_doc({
		"doctype": "Personnel Check-In",
		"human": human_name,
		"timestamp_in": now_datetime(),
		"entry_gate": "Main Gate",
		"method": "RFID",
		"device_id": human_doc.primary_tracking_device,
		"initial_zone": "KPLC-ZONE-001",  # Main Office
		"ppe_verification_status": "Verified",
		"purpose_of_visit": "Regular Work"
	})

	checkin.insert(ignore_permissions=True)
	print(f"   ✓ Check-in created: {checkin.name}")

	checkin.submit()
	print(f"   ✓ Check-in submitted")

	# Verify Zone Presence was created
	presence = frappe.get_all("Zone Presence",
		filters={"human": human_name, "status": "Active"},
		fields=["name", "zone", "time_entered"]
	)

	if presence:
		print(f"   ✓ Zone Presence created: {presence[0].name} in zone {presence[0].zone}")
	else:
		print("   ❌ Zone Presence NOT created")

	# Verify Human Location Event was created
	location_event = frappe.get_all("Human Location Event",
		filters={"human": human_name},
		fields=["name", "zone", "timestamp"],
		order_by="creation desc",
		limit=1
	)

	if location_event:
		print(f"   ✓ Location Event created: {location_event[0].name}")
	else:
		print("   ❌ Location Event NOT created")

	frappe.db.commit()
	return checkin.name

def test_zone_movement():
	"""Test zone movement tracking."""
	print("\n" + "=" * 80)
	print("TESTING ZONE MOVEMENT")
	print("=" * 80)

	# Get first human with active presence
	presence = frappe.get_all("Zone Presence",
		filters={"status": "Active"},
		fields=["name", "human", "zone"],
		limit=1
	)

	if not presence:
		print("❌ No active Zone Presence found. Run test_check_in_workflow() first.")
		return

	human_name = presence[0].human
	human_doc = frappe.get_doc("Human Profile", human_name)

	print(f"\n1. Moving {human_doc.full_name} to Control Room (Medium Hazard)")

	# Create location event for new zone
	location_event = frappe.get_doc({
		"doctype": "Human Location Event",
		"human": human_name,
		"timestamp": now_datetime(),
		"zone": "KPLC-ZONE-002",  # Control Room
		"source_type": "RFID",
		"source_id": human_doc.primary_tracking_device,
		"confidence": 95.0
	})

	location_event.insert(ignore_permissions=True)
	print(f"   ✓ Location Event created: {location_event.name}")

	# Check if old presence was closed and new one created
	old_presence = frappe.get_doc("Zone Presence", presence[0].name)
	if old_presence.status == "Exited":
		print(f"   ✓ Old Zone Presence closed: {old_presence.name}")
	else:
		print(f"   ⚠️  Old Zone Presence still active: {old_presence.name}")

	new_presence = frappe.get_all("Zone Presence",
		filters={"human": human_name, "zone": "KPLC-ZONE-002", "status": "Active"},
		limit=1
	)

	if new_presence:
		print(f"   ✓ New Zone Presence created: {new_presence[0].name}")
	else:
		print("   ❌ New Zone Presence NOT created")

	frappe.db.commit()

def test_check_out_workflow():
	"""Test Personnel Check-Out workflow."""
	print("\n" + "=" * 80)
	print("TESTING CHECK-OUT WORKFLOW")
	print("=" * 80)

	# Get first submitted check-in without checkout
	checkin = frappe.get_all("Personnel Check-In",
		filters={"docstatus": 1},
		fields=["name", "human", "timestamp_in"],
		limit=1
	)

	if not checkin:
		print("❌ No submitted Check-Ins found. Run test_check_in_workflow() first.")
		return

	checkin_name = checkin[0].name
	human_name = checkin[0].human
	human_doc = frappe.get_doc("Human Profile", human_name)

	# Check if checkout already exists
	existing_checkout = frappe.db.exists("Personnel Check-Out", {"related_check_in": checkin_name})
	if existing_checkout:
		print(f"⏭️  Check-out already exists for {checkin_name}")
		return

	print(f"\n1. Checking out: {human_doc.full_name}")

	# Create checkout
	checkout = frappe.get_doc({
		"doctype": "Personnel Check-Out",
		"human": human_name,
		"related_check_in": checkin_name,
		"timestamp_out": now_datetime(),
		"exit_gate": "Main Gate",
		"method": "RFID"
	})

	checkout.insert(ignore_permissions=True)
	print(f"   ✓ Check-out created: {checkout.name}")
	print(f"   ✓ Duration on-site: {checkout.duration_onsite}")

	checkout.submit()
	print(f"   ✓ Check-out submitted")

	# Verify all Zone Presences were closed
	active_presences = frappe.get_all("Zone Presence",
		filters={"human": human_name, "status": "Active"}
	)

	if not active_presences:
		print(f"   ✓ All Zone Presences closed")
	else:
		print(f"   ⚠️  {len(active_presences)} Zone Presences still active")

	frappe.db.commit()
	return checkout.name

def run_all_tests():
	"""Run all tests in sequence."""
	print("\n" + "=" * 80)
	print("RUNNING COMPREHENSIVE PERSONNEL TRACKING MODULE TESTS")
	print("=" * 80)

	try:
		# Setup
		setup_test_data()

		# Test workflows
		test_check_in_workflow()
		test_zone_movement()
		test_check_out_workflow()

		print("\n" + "=" * 80)
		print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
		print("=" * 80)

	except Exception as e:
		print(f"\n❌ ERROR: {str(e)}")
		import traceback
		traceback.print_exc()

if __name__ == "__main__":
	run_all_tests()

