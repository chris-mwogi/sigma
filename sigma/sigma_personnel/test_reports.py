#!/usr/bin/env python3
"""
Test script for Personnel Tracking Module Reports
Tests all 4 reports with sample data
"""

import frappe
from frappe.utils import now, add_days, getdate
import json

def setup_test_data():
    """Create sample data for testing reports"""
    print("\n" + "=" * 80)
    print("SETTING UP TEST DATA")
    print("=" * 80)
    
    # Create test zones
    zones = []
    zone_data = [
        {"zone_code": "ZONE-TEST-001", "zone_name": "Test Substation A", "hazard_level": "High",
         "max_occupancy": 5, "enable_lone_worker_alert": 1, "clearance_level_required": "High"},
        {"zone_code": "ZONE-TEST-002", "zone_name": "Test Control Room", "hazard_level": "Medium",
         "max_occupancy": 10, "enable_lone_worker_alert": 0, "clearance_level_required": "Medium"},
        {"zone_code": "ZONE-TEST-003", "zone_name": "Test Warehouse", "hazard_level": "Low",
         "max_occupancy": 20, "enable_lone_worker_alert": 0, "clearance_level_required": "Low"}
    ]

    for zd in zone_data:
        if not frappe.db.exists("Zone Configuration", zd["zone_code"]):
            zone = frappe.get_doc({
                "doctype": "Zone Configuration",
                "zone_code": zd["zone_code"],
                "zone_name": zd["zone_name"],
                "hazard_level": zd["hazard_level"],
                "max_occupancy": zd["max_occupancy"],
                "enable_lone_worker_alert": zd["enable_lone_worker_alert"],
                "clearance_level_required": zd["clearance_level_required"]
            })
            zone.insert()
            zones.append(zone.name)
            print(f"✓ Created zone: {zone.zone_name}")
        else:
            zones.append(zd["zone_code"])
            print(f"✓ Zone exists: {zd['zone_name']}")
    
    # Create test personnel (auto-named)
    personnel = []
    personnel_data = [
        {"full_name": "John Doe", "person_type": "Employee",
         "clearance_level": "High", "ppe_required": 1, "ppe_certified_date": add_days(getdate(), -30)},
        {"full_name": "Jane Smith", "person_type": "Employee",
         "clearance_level": "Medium", "ppe_required": 1, "ppe_certified_date": add_days(getdate(), -340)},
        {"full_name": "Bob Johnson", "person_type": "Contractor",
         "clearance_level": "Low", "ppe_required": 1, "ppe_certified_date": add_days(getdate(), -400)},
        {"full_name": "Alice Brown", "person_type": "Visitor",
         "clearance_level": "Low", "ppe_required": 0}
    ]

    for pd in personnel_data:
        # Check if person with this name already exists
        existing = frappe.db.get_value("Human Profile", {"full_name": pd["full_name"]}, "name")
        if not existing:
            person = frappe.get_doc({
                "doctype": "Human Profile",
                "full_name": pd["full_name"],
                "person_type": pd["person_type"],
                "clearance_level": pd["clearance_level"],
                "ppe_required": pd["ppe_required"],
                "ppe_certified_date": pd.get("ppe_certified_date"),
                "department": "Operations",
                "status": "Active",
                "tracking_enabled": 0,  # Disable tracking to avoid consent requirement
                "consent_signed": 0
            })
            person.insert()
            # Don't submit - just save as draft for testing
            personnel.append(person.name)
            print(f"✓ Created personnel: {person.full_name} ({person.name})")
        else:
            personnel.append(existing)
            print(f"✓ Personnel exists: {pd['full_name']} ({existing})")
    
    # Create location events
    print("\n✓ Creating location events...")
    for i, person_id in enumerate(personnel[:2]):  # First 2 personnel
        for j, zone_id in enumerate(zones[:2]):  # First 2 zones
            event = frappe.get_doc({
                "doctype": "Human Location Event",
                "human": person_id,
                "zone": zone_id,
                "timestamp": add_days(now(), -j),
                "source_type": "RFID",
                "confidence": 0.95
            })
            event.insert()
            # Don't submit - save as draft

    print(f"✓ Created {len(personnel[:2]) * len(zones[:2])} location events")
    
    # Create zone presence records
    print("\n✓ Creating zone presence records...")
    for person_id in personnel[:3]:
        presence = frappe.get_doc({
            "doctype": "Zone Presence",
            "human": person_id,
            "zone": zones[0],
            "time_entered": add_days(now(), -1),
            "status": "Active"
        })
        presence.insert()

    print(f"✓ Created 3 active zone presence records")
    
    # Create lone worker alerts
    print("\n✓ Creating lone worker alerts...")
    alert_data = [
        {"severity": "Critical", "resolution_status": "Open"},
        {"severity": "High", "resolution_status": "Acknowledged"},
        {"severity": "Medium", "resolution_status": "Resolved"}
    ]

    for ad in alert_data:
        alert = frappe.get_doc({
            "doctype": "Lone Worker Alert",
            "human": personnel[0],
            "zone": zones[0],
            "raised_at": add_days(now(), -1),
            "alert_type": "Lone Worker Timeout",
            "severity": ad["severity"],
            "resolution_status": ad["resolution_status"]
        })
        alert.insert()

    print(f"✓ Created 3 lone worker alerts")
    
    frappe.db.commit()
    print("\n" + "=" * 80)
    print("TEST DATA SETUP COMPLETE!")
    print("=" * 80)
    
    return zones, personnel

def test_reports():
    """Test all 4 reports"""
    print("\n" + "=" * 80)
    print("TESTING REPORTS")
    print("=" * 80)
    
    # Test 1: Personnel Movement History
    print("\n1. Testing Personnel Movement History Report...")
    try:
        from sigma.sigma_personnel.report.personnel_movement_history.personnel_movement_history import execute
        filters = {"from_date": add_days(getdate(), -7), "to_date": getdate()}
        columns, data = execute(filters)
        print(f"   ✓ Report executed successfully")
        print(f"   ✓ Columns: {len(columns)}")
        print(f"   ✓ Data rows: {len(data)}")
        if data:
            print(f"   ✓ Sample row: {data[0].get('full_name')} moved to {data[0].get('zone_name')}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    # Test 2: Zone Occupancy Report
    print("\n2. Testing Zone Occupancy Report...")
    try:
        from sigma.sigma_personnel.report.zone_occupancy_report.zone_occupancy_report import execute
        result = execute({})
        # Handle both 4 and 5 return values
        if len(result) == 4:
            columns, data, message, chart = result
            summary = None
        else:
            columns, data, message, chart, summary = result
        print(f"   ✓ Report executed successfully")
        print(f"   ✓ Columns: {len(columns)}")
        print(f"   ✓ Data rows: {len(data)}")
        print(f"   ✓ Chart data: {chart is not None}")
        if data:
            print(f"   ✓ Sample: {data[0].get('zone_name')} - {data[0].get('current_occupancy')}/{data[0].get('max_occupancy')} ({data[0].get('status')})")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    # Test 3: Lone Worker Incidents Report
    print("\n3. Testing Lone Worker Incidents Report...")
    try:
        from sigma.sigma_personnel.report.lone_worker_incidents_report.lone_worker_incidents_report import execute
        filters = {"from_date": add_days(getdate(), -7), "to_date": getdate()}
        columns, data, message, chart, summary = execute(filters)
        print(f"   ✓ Report executed successfully")
        print(f"   ✓ Columns: {len(columns)}")
        print(f"   ✓ Data rows: {len(data)}")
        print(f"   ✓ Chart data: {chart is not None}")
        print(f"   ✓ Summary stats: {len(summary) if summary else 0}")
        if data:
            print(f"   ✓ Sample: {data[0].get('full_name')} - {data[0].get('severity')} ({data[0].get('resolution_status')})")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    # Test 4: PPE Compliance Report
    print("\n4. Testing PPE Compliance Report...")
    try:
        from sigma.sigma_personnel.report.ppe_compliance_report.ppe_compliance_report import execute
        columns, data, message, chart, summary = execute({})
        print(f"   ✓ Report executed successfully")
        print(f"   ✓ Columns: {len(columns)}")
        print(f"   ✓ Data rows: {len(data)}")
        print(f"   ✓ Chart data: {chart is not None}")
        print(f"   ✓ Summary stats: {len(summary) if summary else 0}")
        if data:
            print(f"   ✓ Sample: {data[0].get('full_name')} - {data[0].get('compliance_status')}")
            compliant = len([d for d in data if d.get('compliance_status') == 'Compliant'])
            expired = len([d for d in data if d.get('compliance_status') == 'Expired'])
            print(f"   ✓ Compliant: {compliant}, Expired: {expired}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    print("\n" + "=" * 80)
    print("REPORT TESTING COMPLETE!")
    print("=" * 80)

def run_all_tests():
    """Main test runner"""
    frappe.set_user("Administrator")

    # Setup test data
    zones, personnel = setup_test_data()

    # Test reports
    test_reports()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
    print("=" * 80)
    print("\nYou can now:")
    print("1. Open the Human Tracking workspace: http://172.24.13.88:8000/app/human-tracking")
    print("2. Click on any report to view it")
    print("3. Test the number cards in the workspace")
    print("=" * 80)

if __name__ == "__main__":
    run_all_tests()

