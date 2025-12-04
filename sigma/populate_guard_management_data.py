#!/usr/bin/env python3
"""
Script to populate test data for Guard Management
Includes: Security Resources, Site Allocations, Guard Shifts, Guard Activities, Patrol Schedules
"""

import frappe
from datetime import datetime, timedelta
import random

# Test data for Guard Names (simple approach without Security Resource)
GUARD_NAMES = [
    "John Mwangi",
    "Peter Kipchoge",
    "Mary Ochieng",
    "James Kariuki",
    "David Kiplagat",
    "Sarah Mutua",
    "Michael Omondi",
    "Grace Wanjiru",
]

# Site Allocations (Guard assignments to locations)
SITE_ALLOCATIONS = [
    {"location": "Nairobi Main Office", "supplier": "Security Systems Inc"},
    {"location": "Westlands Branch", "supplier": "Security Systems Inc"},
    {"location": "Industrial Area Branch", "supplier": "Security Systems Inc"},
    {"location": "Kiambu Main Office", "supplier": "Security Systems Inc"},
    {"location": "Nakuru Main Office", "supplier": "Security Systems Inc"},
]

# Patrol Checkpoints
PATROL_CHECKPOINTS = [
    {"checkpoint_name": "Main Gate", "location": "Nairobi Main Office"},
    {"checkpoint_name": "Back Entrance", "location": "Nairobi Main Office"},
    {"checkpoint_name": "Parking Area", "location": "Westlands Branch"},
    {"checkpoint_name": "Server Room", "location": "Industrial Area Branch"},
    {"checkpoint_name": "Perimeter Fence", "location": "Kiambu Main Office"},
]

# Activity types for Guard Activity (valid options only)
ACTIVITY_TYPES = ["Check In", "Check Out", "Patrol", "Break", "Incident", "Other"]


def create_site_allocation(allocation_data):
    """Create a Site Allocation"""
    try:
        site_name = f"SA-{allocation_data['location'].replace(' ', '-')}"
        existing = frappe.db.exists('Site Allocation', site_name)
        if existing:
            print(f"  ✓ Site Allocation '{site_name}' already exists")
            return site_name

        allocation = frappe.new_doc('Site Allocation')
        allocation.location = allocation_data['location']
        allocation.supplier = allocation_data.get('supplier', 'Security Systems Inc')
        allocation.start_date = "2025-01-01"
        allocation.end_date = "2025-12-31"

        allocation.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  ✓ Created Site Allocation: {site_name}")
        return site_name
    except Exception as e:
        print(f"  ✗ Error creating Site Allocation: {str(e)}")
        return None


def create_patrol_checkpoint(checkpoint_data):
    """Create a Patrol Checkpoint"""
    try:
        existing = frappe.db.exists('Patrol Checkpoint', checkpoint_data['checkpoint_name'])
        if existing:
            print(f"  ✓ Patrol Checkpoint '{checkpoint_data['checkpoint_name']}' already exists")
            return checkpoint_data['checkpoint_name']
        
        checkpoint = frappe.new_doc('Patrol Checkpoint')
        checkpoint.checkpoint_name = checkpoint_data['checkpoint_name']
        checkpoint.location = checkpoint_data['location']
        checkpoint.status = "Active"
        
        checkpoint.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  ✓ Created Patrol Checkpoint: {checkpoint_data['checkpoint_name']}")
        return checkpoint_data['checkpoint_name']
    except Exception as e:
        print(f"  ✗ Error creating Patrol Checkpoint: {str(e)}")
        return None


def create_guard_shifts(num_shifts=20):
    """Create Guard Shifts"""
    locations = ["Nairobi Main Office", "Westlands Branch", "Industrial Area Branch", "Kiambu Main Office", "Nakuru Main Office"]

    created = 0
    for i in range(num_shifts):
        try:
            guard_name = random.choice(GUARD_NAMES)
            location = random.choice(locations)

            shift_name = f"GS-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            existing = frappe.db.exists('Guard Shift', shift_name)
            if existing:
                continue

            shift = frappe.new_doc('Guard Shift')
            shift.guard_name = guard_name
            shift.site_allocation = location

            # Random shift times
            base_time = datetime.now() - timedelta(days=random.randint(0, 7))
            shift.check_in_time = base_time.replace(hour=random.choice([6, 14, 22]))
            shift.check_out_time = shift.check_in_time + timedelta(hours=8)
            shift.status = random.choice(["Active", "Completed"])
            shift.shift_report = f"Shift report for {guard_name} at {location}"

            shift.insert(ignore_permissions=True)
            frappe.db.commit()
            created += 1
            print(f"  ✓ Created Guard Shift: {shift_name}")
        except Exception as e:
            print(f"  ✗ Error creating Guard Shift: {str(e)}")

    return created


def create_guard_activities(num_activities=30):
    """Create Guard Activities"""
    locations = ["Nairobi Main Office", "Westlands Branch", "Industrial Area Branch", "Kiambu Main Office", "Nakuru Main Office"]

    created = 0
    for i in range(num_activities):
        try:
            guard_id = random.choice(GUARD_NAMES)
            location = random.choice(locations)
            activity_type = random.choice(ACTIVITY_TYPES)

            activity_name = f"GA-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            existing = frappe.db.exists('Guard Activity', activity_name)
            if existing:
                continue

            activity = frappe.new_doc('Guard Activity')
            activity.guard_id = guard_id
            activity.activity_type = activity_type
            activity.location = location
            activity.timestamp = datetime.now() - timedelta(hours=random.randint(0, 168))
            activity.gps_latitude = round(random.uniform(-1.3, -1.2), 6)
            activity.gps_longitude = round(random.uniform(36.7, 36.9), 6)
            activity.notes = f"{activity_type} performed by {guard_id} at {location}"

            activity.insert(ignore_permissions=True)
            frappe.db.commit()
            created += 1
            print(f"  ✓ Created Guard Activity: {activity_name}")
        except Exception as e:
            print(f"  ✗ Error creating Guard Activity: {str(e)}")

    return created


def main():
    """Main function to populate guard management test data"""
    print("\n" + "=" * 70)
    print("POPULATING GUARD MANAGEMENT TEST DATA")
    print("=" * 70)

    total_created = 0

    # Create Site Allocations
    print("\n📍 Creating Site Allocations...")
    for allocation_data in SITE_ALLOCATIONS:
        if create_site_allocation(allocation_data):
            total_created += 1

    # Create Patrol Checkpoints
    print("\n🚩 Creating Patrol Checkpoints...")
    for checkpoint_data in PATROL_CHECKPOINTS:
        if create_patrol_checkpoint(checkpoint_data):
            total_created += 1

    # Create Guard Shifts
    print("\n⏰ Creating Guard Shifts...")
    shifts_created = create_guard_shifts(20)
    total_created += shifts_created

    # Create Guard Activities
    print("\n📋 Creating Guard Activities...")
    activities_created = create_guard_activities(30)
    total_created += activities_created

    print("\n" + "=" * 70)
    print(f"✅ COMPLETED - Total records created: {total_created}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

