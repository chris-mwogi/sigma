# Copyright (c) 2025, Sigma and contributors
# Comprehensive test data for Access Control Module
# Aligned with Kenya Power (KPLC) operations and ISO 27001 compliance

import frappe
from frappe.utils import now_datetime, add_days, add_to_date, getdate, nowdate
import random
from datetime import datetime, timedelta

def create_test_data():
    """Create comprehensive test data for Access Control module"""
    frappe.flags.ignore_permissions = True
    
    print("\n" + "="*60)
    print("CREATING ACCESS CONTROL TEST DATA FOR KPLC")
    print("="*60)
    
    # Create in order of dependencies
    create_access_levels()
    create_access_schedules()
    create_access_zones()
    create_access_controllers()
    create_access_points()
    create_access_groups()
    create_access_credentials()
    create_biometric_templates()
    create_vehicle_access_profiles()
    create_access_events()
    create_access_incidents()
    create_door_alarms()
    create_device_health_logs()
    create_anpr_events()
    create_emergency_rules()
    configure_settings()
    
    frappe.db.commit()
    print("\n" + "="*60)
    print("TEST DATA CREATION COMPLETE!")
    print("="*60)


def create_access_levels():
    """Create 5 hierarchical access levels"""
    print("\n--- Creating Access Levels ---")

    levels = [
        {"name": "Public Access", "code": "L1", "priority": 1, "clearance": "None", "desc": "Access to public areas, lobbies, and reception"},
        {"name": "Employee Access", "code": "L2", "priority": 2, "clearance": "Low", "desc": "Standard employee access to office areas"},
        {"name": "Restricted Access", "code": "L3", "priority": 3, "clearance": "Medium", "desc": "Access to restricted departments and sensitive areas"},
        {"name": "High Security", "code": "L4", "priority": 4, "clearance": "High", "desc": "Access to server rooms, control rooms, and executive areas"},
        {"name": "Critical Infrastructure", "code": "L5", "priority": 5, "clearance": "Critical", "desc": "Access to substations, data centers, and critical systems"}
    ]

    for level in levels:
        if not frappe.db.exists("Access Level", {"level_name": level["name"]}):
            doc = frappe.get_doc({
                "doctype": "Access Level",
                "level_name": level["name"],
                "level_code": level["code"],
                "level_priority": level["priority"],
                "description": level["desc"],
                "clearance_required": level["clearance"],
                "background_check_required": 1 if level["priority"] >= 3 else 0,
                "training_required": 1 if level["priority"] >= 4 else 0,
                "escort_policy": "Escort Required" if level["priority"] >= 4 else "No Escort",
                "max_access_duration_minutes": 480 if level["priority"] <= 2 else 240,
                "requires_approval": 1 if level["priority"] >= 4 else 0,
                "risk_weight": level["priority"] * 0.5
            })
            doc.insert()
            print(f"  Created: {level['name']} (Level {level['priority']})")
        else:
            print(f"  Exists: {level['name']}")


def create_access_schedules():
    """Create access schedules"""
    print("\n--- Creating Access Schedules ---")

    schedules = [
        {"name": "Standard Business Hours", "code": "STD-BUS", "type": "Standard", "desc": "Mon-Fri 8:00 AM - 5:00 PM"},
        {"name": "24/7 Access", "code": "24-7", "type": "24/7 Access", "desc": "Round the clock access for essential personnel"},
        {"name": "Weekend Maintenance", "code": "WKD-MAINT", "type": "Temporary", "desc": "Saturday and Sunday for maintenance crews"},
        {"name": "Night Shift Operations", "code": "NIGHT-SHIFT", "type": "Standard", "desc": "Mon-Fri 6:00 PM - 6:00 AM"},
        {"name": "Holiday Skeleton Staff", "code": "HOL-SKEL", "type": "Holiday", "desc": "Limited access during public holidays"}
    ]

    for sched in schedules:
        if not frappe.db.exists("Access Schedule", {"schedule_name": sched["name"]}):
            doc = frappe.get_doc({
                "doctype": "Access Schedule",
                "schedule_name": sched["name"],
                "schedule_code": sched["code"],
                "schedule_type": sched["type"],
                "description": sched["desc"],
                "status": "Active",
                "effective_from": add_days(nowdate(), -30),
                "timezone": "Africa/Nairobi"
            })
            doc.insert()
            print(f"  Created: {sched['name']}")
        else:
            print(f"  Exists: {sched['name']}")


def create_access_zones():
    """Create security zones"""
    print("\n--- Creating Access Zones ---")

    zones = [
        {"name": "Public Lobby", "code": "ZONE-PUB", "type": "Public", "clearance": "None", "capacity": 100},
        {"name": "General Office Area", "code": "ZONE-OFF", "type": "Restricted", "clearance": "Low", "capacity": 200},
        {"name": "Finance Department", "code": "ZONE-FIN", "type": "Secure", "clearance": "Medium", "capacity": 30},
        {"name": "Data Center", "code": "ZONE-DC", "type": "Data Center", "clearance": "Critical", "capacity": 10},
        {"name": "Nairobi Control Room", "code": "ZONE-CTRL", "type": "Critical Infrastructure", "clearance": "Critical", "capacity": 15},
        {"name": "Executive Wing", "code": "ZONE-EXEC", "type": "Executive", "clearance": "High", "capacity": 20},
        {"name": "Westlands Substation Area", "code": "ZONE-WL", "type": "Hazardous", "clearance": "Critical", "capacity": 8}
    ]

    for zone in zones:
        if not frappe.db.exists("Access Zone", {"zone_name": zone["name"]}):
            doc = frappe.get_doc({
                "doctype": "Access Zone",
                "zone_name": zone["name"],
                "zone_code": zone["code"],
                "zone_type": zone["type"],
                "location": "Stima Plaza Head Office" if "Substation" not in zone["name"] else "Westlands Substation",
                "minimum_clearance": zone["clearance"],
                "max_occupancy": zone["capacity"],
                "current_occupancy": random.randint(0, zone["capacity"]//2),
                "occupancy_tracking_enabled": 1,
                "anti_passback_enabled": 1 if zone["clearance"] in ["Medium", "High", "Critical"] else 0,
                "dual_person_rule": 1 if zone["clearance"] == "Critical" else 0,
                "escort_required": 1 if zone["clearance"] == "Critical" else 0,
                "cctv_coverage": 1,
                "hazard_level": "High" if zone["type"] == "Hazardous" else "None",
                "status": "Normal"
            })
            doc.insert()
            print(f"  Created: {zone['name']} ({zone['type']})")
        else:
            print(f"  Exists: {zone['name']}")


def create_access_controllers():
    """Create hardware controllers"""
    print("\n--- Creating Access Controllers ---")

    controllers = [
        {"name": "HQ Controller 1", "code": "CTRL-HQ-001", "loc": "Stima Plaza Head Office", "model": "HID Mercury EP4502", "doors": 8},
        {"name": "HQ Controller 2", "code": "CTRL-HQ-002", "loc": "Stima Plaza Head Office", "model": "HID Mercury EP4502", "doors": 8},
        {"name": "Data Center Controller", "code": "CTRL-DC-001", "loc": "Stima Plaza Head Office", "model": "HID Mercury EP1502", "doors": 4},
        {"name": "Westlands Controller", "code": "CTRL-WL-001", "loc": "Westlands Substation", "model": "HID Mercury EP2500", "doors": 2},
        {"name": "Ruiru Controller", "code": "CTRL-RU-001", "loc": "Ruiru Substation", "model": "HID Mercury EP2500", "doors": 2}
    ]

    for ctrl in controllers:
        if not frappe.db.exists("Access Controller", {"controller_code": ctrl["code"]}):
            doc = frappe.get_doc({
                "doctype": "Access Controller",
                "controller_name": ctrl["name"],
                "controller_code": ctrl["code"],
                "location": ctrl["loc"],
                "model": ctrl["model"],
                "manufacturer": "HID Global",
                "serial_number": f"SN{random.randint(100000, 999999)}",
                "ip_address": f"192.168.1.{random.randint(100, 200)}",
                "communication_protocol": "TCP/IP",
                "encryption_enabled": 1,
                "max_access_points": ctrl["doors"],
                "max_credentials": 10000,
                "offline_mode_enabled": 1,
                "battery_backup": 1,
                "status": "Online",
                "last_heartbeat": now_datetime(),
                "firmware_version": "3.2.1"
            })
            doc.insert()
            print(f"  Created: {ctrl['code']} at {ctrl['loc']}")
        else:
            print(f"  Exists: {ctrl['code']}")


def create_access_points():
    """Create access points (doors, gates, turnstiles)"""
    print("\n--- Creating Access Points ---")

    points = [
        {"code": "AP-HQ-MAIN", "name": "Main Gate", "type": "Boom Barrier", "zone": "Public Lobby", "reader": "Card Only"},
        {"code": "AP-HQ-ENT1", "name": "Building A Main Entrance", "type": "Door", "zone": "Public Lobby", "reader": "Card Only"},
        {"code": "AP-HQ-TURN1", "name": "Reception Turnstile 1", "type": "Turnstile", "zone": "General Office Area", "reader": "Card Only"},
        {"code": "AP-HQ-TURN2", "name": "Reception Turnstile 2", "type": "Turnstile", "zone": "General Office Area", "reader": "Card Only"},
        {"code": "AP-HQ-FIN", "name": "Finance Department Door", "type": "Door", "zone": "Finance Department", "reader": "Card + PIN"},
        {"code": "AP-HQ-DC1", "name": "Data Center Entry", "type": "Man Trap", "zone": "Data Center", "reader": "Biometric"},
        {"code": "AP-HQ-DC2", "name": "Data Center Server Room", "type": "Door", "zone": "Data Center", "reader": "Biometric"},
        {"code": "AP-HQ-CTRL", "name": "Control Room Entry", "type": "Door", "zone": "Nairobi Control Room", "reader": "Card + PIN"},
        {"code": "AP-HQ-EXEC", "name": "Executive Floor Elevator", "type": "Elevator", "zone": "Executive Wing", "reader": "Card + PIN"},
        {"code": "AP-HQ-EXEC2", "name": "Executive Boardroom", "type": "Door", "zone": "Executive Wing", "reader": "Card Only"},
        {"code": "AP-HQ-PARK1", "name": "Parking Entry Gate", "type": "Boom Barrier", "zone": "Public Lobby", "reader": "Card Only"},
        {"code": "AP-HQ-PARK2", "name": "Parking Exit Gate", "type": "Boom Barrier", "zone": "Public Lobby", "reader": "Card Only"},
        {"code": "AP-WL-GATE", "name": "Westlands Substation Gate", "type": "Gate", "zone": "Westlands Substation Area", "reader": "Biometric"},
        {"code": "AP-WL-CTRL", "name": "Westlands Control Building", "type": "Door", "zone": "Westlands Substation Area", "reader": "Card + PIN"},
        {"code": "AP-RU-GATE", "name": "Ruiru Substation Gate", "type": "Gate", "zone": None, "reader": "Card + PIN"}
    ]

    # Get first controller and zones
    controller = frappe.db.get_value("Access Controller", {}, "name")
    zones = {z.zone_name: z.name for z in frappe.get_all("Access Zone", fields=["name", "zone_name"])}
    levels = {l.level_name: l.name for l in frappe.get_all("Access Level", fields=["name", "level_name"])}

    for pt in points:
        if not frappe.db.exists("Access Point", {"access_point_code": pt["code"]}):
            zone_name = zones.get(pt["zone"]) if pt["zone"] else None
            doc = frappe.get_doc({
                "doctype": "Access Point",
                "access_point_name": pt["name"],
                "access_point_code": pt["code"],
                "point_type": pt["type"],
                "location": "Stima Plaza Head Office" if "HQ" in pt["code"] else "Westlands Substation" if "WL" in pt["code"] else "Ruiru Substation",
                "zone": zone_name,
                "reader_type": pt["reader"],
                "controller": controller,
                "direction": "Entry" if "Entry" in pt["name"] or "Main" in pt["name"] else "Bidirectional",
                "unlock_duration_seconds": 5,
                "held_open_alarm_seconds": 30,
                "forced_open_alarm": 1,
                "door_contact_monitoring": 1,
                "anti_passback_enabled": 1 if pt["reader"] != "Card Only" else 0,
                "status": "Active"
            })
            doc.insert()
            print(f"  Created: {pt['code']} - {pt['name']}")
        else:
            print(f"  Exists: {pt['code']}")


def create_access_groups():
    """Create access groups"""
    print("\n--- Creating Access Groups ---")

    groups = [
        {"name": "General Staff", "code": "GRP-GEN", "type": "Department", "desc": "Access to general office areas"},
        {"name": "Finance Team", "code": "GRP-FIN", "type": "Department", "desc": "Access to finance department"},
        {"name": "IT Department", "code": "GRP-IT", "type": "Department", "desc": "Access to IT areas and data center"},
        {"name": "Executive Team", "code": "GRP-EXEC", "type": "VIP", "desc": "Access to executive wing"},
        {"name": "Infrastructure Team", "code": "GRP-INFRA", "type": "Department", "desc": "Access to substations and control rooms"}
    ]

    for grp in groups:
        if not frappe.db.exists("Access Group", {"group_name": grp["name"]}):
            doc = frappe.get_doc({
                "doctype": "Access Group",
                "group_name": grp["name"],
                "group_code": grp["code"],
                "group_type": grp["type"],
                "description": grp["desc"],
                "location": "Stima Plaza Head Office",
                "status": "Active"
            })
            doc.insert()
            print(f"  Created: {grp['name']}")
        else:
            print(f"  Exists: {grp['name']}")


def create_access_credentials():
    """Create access credentials for employees, visitors, contractors, vehicles"""
    print("\n--- Creating Access Credentials ---")

    # Get human profiles and access levels
    profiles = frappe.get_all("Human Profile", fields=["name", "full_name"])
    levels = {l.level_name: l.name for l in frappe.get_all("Access Level", fields=["name", "level_name"])}

    # Employee credentials (Card/Fob)
    for i, hp in enumerate(profiles[:5]):
        cred_id = f"CARD-EMP-{str(i+1).zfill(4)}"
        if not frappe.db.exists("Access Credential", {"credential_id": cred_id}):
            level_name = ["Employee Access", "Restricted Access", "High Security"][i % 3]
            doc = frappe.get_doc({
                "doctype": "Access Credential",
                "credential_id": cred_id,
                "credential_type": "Card/Fob",
                "holder_type": "Employee",
                "human_profile": hp.name,
                "card_number": f"FC{random.randint(100000, 999999)}",
                "facility_code": "KPLC-HQ",
                "status": "Active",
                "issue_date": add_days(nowdate(), -random.randint(30, 365)),
                "expiry_date": add_days(nowdate(), random.randint(180, 365)),
                "access_level": levels.get(level_name),
                "anti_passback_enabled": 1,
                "location": "Stima Plaza Head Office"
            })
            doc.insert()
            print(f"  Created Employee Card: {cred_id} for {hp.full_name}")

    # Biometric credentials for high-security
    for i, hp in enumerate(profiles[:3]):
        cred_id = f"BIO-EMP-{str(i+1).zfill(4)}"
        if not frappe.db.exists("Access Credential", {"credential_id": cred_id}):
            doc = frappe.get_doc({
                "doctype": "Access Credential",
                "credential_id": cred_id,
                "credential_type": "Biometric",
                "holder_type": "Employee",
                "human_profile": hp.name,
                "status": "Active",
                "issue_date": add_days(nowdate(), -random.randint(30, 180)),
                "expiry_date": add_days(nowdate(), 365),
                "access_level": levels.get("Critical Infrastructure"),
                "dual_authentication_required": 1,
                "location": "Stima Plaza Head Office"
            })
            doc.insert()
            print(f"  Created Biometric: {cred_id} for {hp.full_name}")

    # Visitor temporary credentials
    visitors = frappe.get_all("Visitor", fields=["name"], limit=3)
    for i, vis in enumerate(visitors):
        cred_id = f"TEMP-VIS-{str(i+1).zfill(4)}"
        if not frappe.db.exists("Access Credential", {"credential_id": cred_id}):
            doc = frappe.get_doc({
                "doctype": "Access Credential",
                "credential_id": cred_id,
                "credential_type": "QR Code",
                "holder_type": "Visitor",
                "visitor": vis.name,
                "status": "Active",
                "issue_date": nowdate(),
                "expiry_date": add_days(nowdate(), 1),  # Single day pass
                "access_level": levels.get("Public Access"),
                "escort_required": 1,
                "location": "Stima Plaza Head Office",
                "notes": f"Temporary visitor pass for {vis.name}"
            })
            doc.insert()
            print(f"  Created Visitor Pass: {cred_id}")

    # Contractor credentials - use existing Human Profiles
    contractor_profiles = frappe.get_all("Human Profile", fields=["name", "full_name"], limit=3)
    for i, hp in enumerate(contractor_profiles):
        cred_id = f"CONT-{str(i+1).zfill(4)}"
        if not frappe.db.exists("Access Credential", {"credential_id": cred_id}):
            doc = frappe.get_doc({
                "doctype": "Access Credential",
                "credential_id": cred_id,
                "credential_type": "Card/Fob",
                "holder_type": "Contractor",
                "human_profile": hp.name,
                "status": "Active",
                "issue_date": add_days(nowdate(), -30),
                "expiry_date": add_days(nowdate(), 60),
                "access_level": levels.get("Restricted Access"),
                "escort_required": 1,
                "location": "Stima Plaza Head Office",
                "notes": f"Contractor: {hp.full_name}"
            })
            doc.insert()
            print(f"  Created Contractor: {cred_id} - {hp.full_name}")

    # Vehicle tag credentials
    vehicles = frappe.get_all("Vehicle", fields=["name", "license_plate"], limit=5)
    for i, veh in enumerate(vehicles):
        cred_id = f"VTAG-{str(i+1).zfill(4)}"
        if not frappe.db.exists("Access Credential", {"credential_id": cred_id}):
            doc = frappe.get_doc({
                "doctype": "Access Credential",
                "credential_id": cred_id,
                "credential_type": "Vehicle Tag",
                "holder_type": "Vehicle",
                "vehicle": veh.name,
                "status": "Active",
                "issue_date": add_days(nowdate(), -90),
                "expiry_date": add_days(nowdate(), 275),
                "access_level": levels.get("Public Access"),
                "location": "Stima Plaza Head Office",
                "notes": f"Vehicle: {veh.license_plate}"
            })
            doc.insert()
            print(f"  Created Vehicle Tag: {cred_id} - {veh.license_plate}")


def create_biometric_templates():
    """Create biometric templates with GDPR consent"""
    print("\n--- Creating Biometric Templates ---")

    profiles = frappe.get_all("Human Profile", fields=["name", "full_name"], limit=5)

    templates = [
        {"type": "Fingerprint", "quality": 95},
        {"type": "Fingerprint", "quality": 92},
        {"type": "Face Recognition", "quality": 88},
        {"type": "Iris Scan", "quality": 96},
        {"type": "Palm Vein", "quality": 94},
    ]

    for i, hp in enumerate(profiles[:5]):
        tmpl = templates[i % len(templates)]

        if frappe.db.count("Biometric Template", {"human_profile": hp.name}) == 0:
            doc = frappe.get_doc({
                "doctype": "Biometric Template",
                "human_profile": hp.name,
                "template_type": tmpl["type"],
                "quality_score": tmpl["quality"],
                "enrollment_date": add_to_date(now_datetime(), days=-random.randint(30, 180)),
                "enrollment_location": "Stima Plaza Head Office",
                "consent_obtained": 1,
                "gdpr_compliant": 1,
                "status": "Active"
            })
            doc.insert()
            print(f"  Created: {tmpl['type']} template for {hp.full_name}")


def create_vehicle_access_profiles():
    """Create vehicle access profiles"""
    print("\n--- Creating Vehicle Access Profiles ---")

    vehicles = frappe.get_all("Vehicle", fields=["name", "license_plate"], limit=8)
    profiles = frappe.get_all("Human Profile", fields=["name", "full_name"], limit=3)
    levels = {l.level_name: l.name for l in frappe.get_all("Access Level", fields=["name", "level_name"])}
    groups = {g.group_name: g.name for g in frappe.get_all("Access Group", fields=["name", "group_name"])}

    owner_types = ["Company", "Employee", "Contractor", "Visitor"]
    vehicle_types = ["Sedan", "SUV", "Pickup", "Van", "Motorcycle"]

    for i, veh in enumerate(vehicles):
        if not frappe.db.exists("Vehicle Access Profile", {"vehicle": veh.name}):
            doc = frappe.get_doc({
                "doctype": "Vehicle Access Profile",
                "vehicle": veh.name,
                "license_plate": veh.license_plate,
                "vehicle_type": vehicle_types[i % len(vehicle_types)],
                "owner_type": owner_types[i % 4],
                "human_profile": profiles[i % len(profiles)].name if i < 5 else None,
                "access_level": levels.get("Employee Access"),
                "parking_zone": ["Zone A - Staff", "Zone B - Visitors", "Zone C - VIP", "Zone D - Contractors"][i % 4],
                "anpr_enabled": 1,
                "valid_from": add_days(nowdate(), -random.randint(30, 180)),
                "valid_until": add_days(nowdate(), random.randint(90, 365)),
                "status": "Active"
            })
            doc.insert()
            print(f"  Created: Profile for {veh.license_plate}")


def create_access_events():
    """Create realistic access events over the past 30 days"""
    print("\n--- Creating Access Events ---")

    # Get credentials and access points
    credentials = frappe.get_all("Access Credential", fields=["name", "credential_id", "credential_type", "holder_type", "human_profile"])
    access_points = frappe.get_all("Access Point", fields=["name", "access_point_code", "access_point_name", "zone"])
    zones = {z.name: z for z in frappe.get_all("Access Zone", fields=["name", "zone_name"])}

    if not credentials or not access_points:
        print("  No credentials or access points found, skipping events")
        return

    event_types = ["Access Granted", "Access Denied", "Door Forced Open", "Anti-Passback Violation", "Expired Credential", "Invalid Credential", "Door Held Open"]
    results = ["Granted", "Denied"]

    for day_offset in range(30, 0, -1):
        # 5-15 events per day
        num_events = random.randint(5, 15)
        base_date = add_days(nowdate(), -day_offset)

        for _ in range(num_events):
            cred = random.choice(credentials)
            ap = random.choice(access_points)

            # Weighted random event type (mostly granted)
            rand = random.randint(1, 100)
            if rand <= 70:
                event_type = "Access Granted"
                result = "Granted"
            elif rand <= 85:
                event_type = "Access Denied"
                result = "Denied"
            else:
                event_type = random.choice(event_types[2:])
                result = "Denied"

            # Random time during business hours (7am - 7pm)
            hour = random.randint(7, 19)
            minute = random.randint(0, 59)
            event_time = f"{base_date} {hour:02d}:{minute:02d}:00"

            # Map credential type to authentication method
            auth_method_map = {
                "Card/Fob": "Card",
                "PIN": "PIN",
                "Biometric": "Biometric",
                "Mobile": "Mobile",
                "QR Code": "QR Code",
                "Vehicle Tag": "Card"
            }
            auth_method = auth_method_map.get(cred.credential_type, "Card")

            doc = frappe.get_doc({
                "doctype": "Access Event",
                "event_time": event_time,
                "event_type": event_type,
                "result": result,
                "access_point": ap.name,
                "zone": ap.zone,
                "credential": cred.name,
                "credential_type": cred.credential_type,
                "holder_type": cred.holder_type,
                "human_profile": cred.human_profile,
                "direction": random.choice(["Entry", "Exit"]),
                "authentication_method": auth_method,
                "location": "Stima Plaza Head Office"
            })
            doc.insert()

    print(f"  Created ~{30*10} access events over 30 days")


def create_access_incidents():
    """Create access incidents"""
    print("\n--- Creating Access Incidents ---")

    incidents = [
        {"type": "Tailgating", "severity": "Medium", "status": "Investigating", "desc": "Tailgating incident detected at main entrance"},
        {"type": "Unauthorized Access", "severity": "High", "status": "Resolved", "desc": "Unauthorized access attempt at Data Center"},
        {"type": "Credential Misuse", "severity": "Medium", "status": "Open", "desc": "Credential sharing detected between employees"},
        {"type": "Anti-Passback Violation", "severity": "Low", "status": "Closed", "desc": "Multiple failed access attempts from single credential"},
        {"type": "Forced Entry", "severity": "High", "status": "Investigating", "desc": "Forced door detected at emergency exit"}
    ]

    ap = frappe.get_value("Access Point", {}, "name")
    zone = frappe.get_value("Access Zone", {}, "name")

    for i, inc in enumerate(incidents):
        if frappe.db.count("Access Incident") < 5:
            incident_time = add_to_date(now_datetime(), days=-random.randint(1, 30))
            doc = frappe.get_doc({
                "doctype": "Access Incident",
                "incident_type": inc["type"],
                "severity": inc["severity"],
                "status": inc["status"],
                "incident_time": incident_time,
                "detected_time": incident_time,
                "access_point": ap,
                "zone": zone,
                "location": "Stima Plaza Head Office",
                "description": inc["desc"],
                "response_action": "Security team notified and investigating" if inc["status"] != "Closed" else "Investigation completed"
            })
            doc.insert()
            print(f"  Created: {inc['type']} incident")


def create_door_alarms():
    """Create door alarm records"""
    print("\n--- Creating Door Alarms ---")

    alarms = [
        {"type": "Door Held Open", "duration": 45, "severity": "Low"},
        {"type": "Door Forced Open", "duration": 0, "severity": "High"},
        {"type": "Tamper", "duration": 0, "severity": "Medium"}
    ]

    ap = frappe.get_value("Access Point", {}, "name")
    zone = frappe.get_value("Access Zone", {}, "name")

    for i, alarm in enumerate(alarms):
        if frappe.db.count("Door Alarm") < 3:
            alarm_time = add_to_date(now_datetime(), days=-random.randint(1, 14))
            doc = frappe.get_doc({
                "doctype": "Door Alarm",
                "alarm_type": alarm["type"],
                "access_point": ap,
                "zone": zone,
                "alarm_time": alarm_time,
                "duration_seconds": alarm["duration"],
                "severity": alarm["severity"],
                "status": random.choice(["Active", "Acknowledged", "Cleared"]),
                "location": "Stima Plaza Head Office"
            })
            doc.insert()
            print(f"  Created: {alarm['type']} alarm")


def create_device_health_logs():
    """Create device health logs for controllers"""
    print("\n--- Creating Device Health Logs ---")

    controllers = frappe.get_all("Access Controller", fields=["name", "controller_code", "location"])

    for ctrl in controllers:
        for day in range(10, 0, -1):
            doc = frappe.get_doc({
                "doctype": "Device Health Log",
                "device_type": "Access Controller",
                "device_reference": ctrl.name,
                "location": ctrl.location,
                "log_time": add_to_date(now_datetime(), days=-day),
                "status": random.choice(["Healthy", "Healthy", "Healthy", "Degraded", "Offline"]),  # 60% healthy
                "cpu_usage_percent": random.randint(10, 85),
                "memory_usage_percent": random.randint(20, 70),
                "network_status": "Connected",
                "latency_ms": random.randint(1, 100)
            })
            doc.insert()

    print(f"  Created {len(controllers) * 10} health logs")


def create_anpr_events():
    """Create ANPR (Automatic Number Plate Recognition) events"""
    print("\n--- Creating ANPR Event Logs ---")

    vehicles = frappe.get_all("Vehicle", fields=["name", "license_plate"], limit=10)
    vehicle_profiles = {v.vehicle: v.name for v in frappe.get_all("Vehicle Access Profile", fields=["name", "vehicle"])}
    access_point = frappe.get_value("Access Point", {"point_type": "Boom Barrier"}, "name")

    if not vehicles:
        print("  No vehicles found, skipping ANPR events")
        return

    for day in range(15, 0, -1):
        # 2-5 ANPR events per day
        for _ in range(random.randint(2, 5)):
            veh = random.choice(vehicles)

            # Randomly simulate known/unknown plates
            is_known = random.random() > 0.2  # 80% known
            confidence = random.randint(70, 99)

            event_time = add_to_date(now_datetime(), days=-day, hours=-random.randint(0, 12))
            result = "Granted" if is_known and confidence > 85 else "Denied"

            doc = frappe.get_doc({
                "doctype": "ANPR Event Log",
                "event_time": event_time,
                "access_point": access_point,
                "location": "Stima Plaza Head Office",
                "direction": random.choice(["Entry", "Exit"]),
                "result": result,
                "detected_plate": veh.license_plate if is_known else f"K{random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')} {random.randint(100,999)}{random.choice('ABCDEFGH')}",
                "confidence_score": confidence,
                "matched_vehicle": veh.name if is_known and confidence > 85 else None,
                "vehicle_access_profile": vehicle_profiles.get(veh.name) if is_known and confidence > 85 else None,
                "match_status": "Matched" if is_known and confidence > 85 else "Unknown" if not is_known else "Low Confidence",
                "gate_action": "Opened" if is_known and confidence > 85 else "Remained Closed"
            })
            doc.insert()

    print(f"  Created ~{15*3} ANPR events")


def create_emergency_rules():
    """Create emergency access rules"""
    print("\n--- Creating Emergency Access Rules ---")

    # Get zones and access points for linking
    zones = frappe.get_all("Access Zone", fields=["name"], limit=5)
    access_points = frappe.get_all("Access Point", fields=["name"], limit=5)

    rules = [
        {"name": "Fire Evacuation Protocol", "type": "Fire Alarm", "action": "Unlock All", "priority": 1, "trigger": "Fire Panel"},
        {"name": "Security Lockdown", "type": "Security Lockdown", "action": "Lock All", "priority": 1, "trigger": "Manual"},
        {"name": "Medical Emergency Access", "type": "Medical Emergency", "action": "Unlock Entry Only", "priority": 2, "trigger": "Manual"},
        {"name": "Power Failure Protocol", "type": "Power Failure", "action": "Normal Operation", "priority": 2, "trigger": "BMS"}
    ]

    for rule in rules:
        if not frappe.db.exists("Emergency Access Rule", {"rule_name": rule["name"]}):
            doc = frappe.get_doc({
                "doctype": "Emergency Access Rule",
                "rule_name": rule["name"],
                "rule_type": rule["type"],
                "action": rule["action"],
                "trigger_source": rule["trigger"],
                "priority": rule["priority"],
                "duration_minutes": 30 if rule["type"] not in ["Fire Alarm", "Security Lockdown"] else 0,
                "requires_confirmation": 1 if rule["type"] == "Security Lockdown" else 0,
                "status": "Active",
                "affected_zones": [{"zone": z.name} for z in zones[:3]],
                "affected_access_points": [{"access_point": ap.name} for ap in access_points[:3]]
            })
            doc.insert()
            print(f"  Created: {rule['name']}")


def configure_settings():
    """Configure Access Control Settings"""
    print("\n--- Configuring Access Control Settings ---")

    try:
        settings = frappe.get_single("Access Control Settings")

        # Set available fields based on the DocType definition
        if hasattr(settings, 'default_credential_validity_days'):
            settings.default_credential_validity_days = 365
        if hasattr(settings, 'anti_passback_timeout_minutes'):
            settings.anti_passback_timeout_minutes = 5
        if hasattr(settings, 'max_failed_attempts'):
            settings.max_failed_attempts = 3
        if hasattr(settings, 'lockout_duration_minutes'):
            settings.lockout_duration_minutes = 30
        if hasattr(settings, 'anpr_confidence_threshold'):
            settings.anpr_confidence_threshold = 85
        if hasattr(settings, 'audit_retention_days'):
            settings.audit_retention_days = 2555  # 7 years for compliance
        if hasattr(settings, 'gdpr_compliance_mode'):
            settings.gdpr_compliance_mode = 1
        if hasattr(settings, 'anti_passback_global'):
            settings.anti_passback_global = 1
        if hasattr(settings, 'default_location'):
            settings.default_location = "Stima Plaza Head Office"
        if hasattr(settings, 'compliance_standard'):
            settings.compliance_standard = "ISO 27001"

        settings.save()
        print("  Access Control Settings configured")
    except Exception as e:
        print(f"  Warning: Could not configure settings - {e}")


# Entry point for bench execute
if __name__ == "__main__":
    create_test_data()
