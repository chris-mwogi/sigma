#!/usr/bin/env python3
"""
Script to populate comprehensive test data for composite assets at KPLC locations
Includes: CCTV Systems, Fire Alarm Systems, GPS Tracker, and Ultrasonic Level Sensor
"""

import frappe
from datetime import datetime

# Asset Categories to create
ASSET_CATEGORIES = [
    "Security Equipment",
    "Safety Equipment",
    "Tracking Equipment",
    "Monitoring Equipment",
]

# Item definitions for assets
ITEMS_TO_CREATE = [
    {"name": "CCTV System", "item_name": "CCTV System", "category": "Security Equipment"},
    {"name": "Fire Alarm System", "item_name": "Fire Alarm System", "category": "Safety Equipment"},
    {"name": "LL303PRO GPS Tracker", "item_name": "LL303PRO GPS Tracker", "category": "Tracking Equipment"},
    {"name": "UE3001 Ultrasonic Level Sensor", "item_name": "UE3001 Ultrasonic Level Sensor", "category": "Monitoring Equipment"},
]

# Composite Asset Definitions
COMPOSITE_ASSETS = {
    "CCTV System": {
        "category": "Security Equipment",
        "components": [
            {"name": "Main Camera Unit", "type": "Camera", "serial": "CAM-CCTV-001", "manufacturer": "Hikvision", "model": "DS-2CD2143G0-I"},
            {"name": "PTZ Camera", "type": "Camera", "serial": "CAM-CCTV-002", "manufacturer": "Hikvision", "model": "DS-2DE4425IW-DE"},
            {"name": "NVR Recorder", "type": "Recorder", "serial": "NVR-CCTV-001", "manufacturer": "Hikvision", "model": "DS-7732NI-K4"},
            {"name": "Network Switch", "type": "Network", "serial": "SW-CCTV-001", "manufacturer": "Cisco", "model": "SG250-26P"},
            {"name": "Power Supply Unit", "type": "Power", "serial": "PSU-CCTV-001", "manufacturer": "Mean Well", "model": "RSP-500-24"},
        ]
    },
    "Fire Alarm System": {
        "category": "Safety Equipment",
        "components": [
            {"name": "Control Panel", "type": "Control", "serial": "FA-CTRL-001", "manufacturer": "Honeywell", "model": "XLS500"},
            {"name": "Smoke Detector 1", "type": "Detector", "serial": "FA-SMOKE-001", "manufacturer": "Honeywell", "model": "5139T"},
            {"name": "Smoke Detector 2", "type": "Detector", "serial": "FA-SMOKE-002", "manufacturer": "Honeywell", "model": "5139T"},
            {"name": "Heat Detector", "type": "Detector", "serial": "FA-HEAT-001", "manufacturer": "Honeywell", "model": "5139H"},
            {"name": "Manual Pull Station", "type": "Activation", "serial": "FA-PULL-001", "manufacturer": "Honeywell", "model": "M4014C"},
            {"name": "Alarm Bell", "type": "Notification", "serial": "FA-BELL-001", "manufacturer": "Honeywell", "model": "5139T-BELL"},
        ]
    }
}

# Specialized Equipment
SPECIALIZED_EQUIPMENT = {
    "LL303PRO GPS Tracker": {
        "location": "Nairobi Central Substation",  # Will be assigned to a substation
        "serial": "GPS-LL303PRO-001",
        "manufacturer": "JimiIoT",
        "model": "LL303PRO",
        "purpose": "Anti-vandalism monitoring",
        "category": "Tracking Equipment"
    },
    "UE3001 Ultrasonic Level Sensor": {
        "location": "Kisumu Off-grid Station",
        "serial": "SENSOR-UE3001-001",
        "manufacturer": "Pepperl+Fuchs",
        "model": "UE3001",
        "purpose": "Water level monitoring",
        "category": "Monitoring Equipment"
    }
}

# Locations for composite assets
LOCATIONS = {
    "Electricity House Nairobi": ["CCTV System", "Fire Alarm System"],
    "Electricity House Kisumu": ["CCTV System", "Fire Alarm System"],
}


def create_asset_category(category_name):
    """Create an Asset Category with accounts"""
    try:
        existing = frappe.db.exists('Asset Category', category_name)
        if existing:
            return category_name

        category = frappe.new_doc('Asset Category')
        category.asset_category_name = category_name

        # Add account entry (required field) - using Electronic Equipment account
        category.append('accounts', {
            'company': 'Kenya Power and Lighting Company PLC',
            'fixed_asset_account': '1720 - Electronic Equipment - KPLC',
            'accumulated_depreciation_account': '1720 - Electronic Equipment - KPLC',
            'depreciation_expense_account': '1720 - Electronic Equipment - KPLC'
        })

        category.insert(ignore_permissions=True)
        frappe.db.commit()
        return category_name
    except Exception as e:
        print(f"  ✗ Error creating asset category '{category_name}': {str(e)}")
        return None


def create_item(item_code, item_name, asset_category=None):
    """Create an Item for the asset"""
    try:
        existing = frappe.db.exists('Item', item_code)
        if existing:
            return item_code

        item = frappe.new_doc('Item')
        item.item_code = item_code
        item.item_name = item_name
        item.item_group = "All Item Groups"
        item.is_stock_item = 0
        item.is_fixed_asset = 1  # Mark as fixed asset

        # Set asset category
        if asset_category:
            item.asset_category = asset_category

        item.insert(ignore_permissions=True)
        frappe.db.commit()
        return item_code
    except Exception as e:
        print(f"  ✗ Error creating item '{item_code}': {str(e)}")
        return None


def create_composite_asset(asset_name, item_code, location, components_data):
    """Create a composite asset with components"""
    try:
        # Check if asset already exists
        existing = frappe.db.exists('Asset', asset_name)
        if existing:
            print(f"  ✓ Asset '{asset_name}' already exists")
            return asset_name

        asset = frappe.new_doc('Asset')
        asset.asset_name = asset_name
        asset.item_code = item_code
        asset.location = location
        asset.is_composite_asset = 1
        asset.status = "Active"
        asset.purchase_date = datetime.now().date()
        asset.net_purchase_amount = 50000  # Default amount
        asset.company = "Kenya Power and Lighting Company PLC"

        # Add components
        for comp in components_data:
            asset.append('asset_components', {
                'component_name': comp['name'],
                'component_type': comp['type'],
                'serial_number': comp['serial'],
                'manufacturer': comp['manufacturer'],
                'model': comp['model'],
                'date_installed': datetime.now().date(),
                'status': 'Active',
                'notes': f"Component of {asset_name}"
            })

        asset.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  ✓ Created composite asset: {asset_name} at {location}")
        print(f"    Components: {len(components_data)}")
        for comp in components_data:
            print(f"      - {comp['name']} (Serial: {comp['serial']})")
        return asset_name
    except Exception as e:
        print(f"  ✗ Error creating asset '{asset_name}': {str(e)}")
        return None


def create_specialized_equipment(equipment_name, item_code, equipment_data):
    """Create specialized equipment (GPS Tracker or Level Sensor)"""
    try:
        existing = frappe.db.exists('Asset', equipment_name)
        if existing:
            print(f"  ✓ Asset '{equipment_name}' already exists")
            return equipment_name

        asset = frappe.new_doc('Asset')
        asset.asset_name = equipment_name
        asset.item_code = item_code
        asset.location = equipment_data['location']
        asset.is_composite_asset = 0
        asset.status = "Active"
        asset.purchase_date = datetime.now().date()
        asset.net_purchase_amount = 25000  # Default amount
        asset.company = "Kenya Power and Lighting Company PLC"

        # Add as a single component asset
        asset.append('asset_components', {
            'component_name': equipment_name,
            'component_type': 'Specialized Equipment',
            'serial_number': equipment_data['serial'],
            'manufacturer': equipment_data['manufacturer'],
            'model': equipment_data['model'],
            'date_installed': datetime.now().date(),
            'status': 'Active',
            'notes': f"{equipment_data['purpose']} - {equipment_name}"
        })

        asset.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  ✓ Created specialized equipment: {equipment_name}")
        print(f"    Location: {equipment_data['location']}")
        print(f"    Serial: {equipment_data['serial']}")
        print(f"    Manufacturer: {equipment_data['manufacturer']}")
        print(f"    Purpose: {equipment_data['purpose']}")
        return equipment_name
    except Exception as e:
        print(f"  ✗ Error creating equipment '{equipment_name}': {str(e)}")
        return None


def main():
    """Main function to populate composite assets"""
    print("\n" + "=" * 80)
    print("POPULATING COMPOSITE ASSETS TEST DATA")
    print("=" * 80)

    total_created = 0

    # Create asset categories first
    print("\n📂 Creating Asset Categories...")
    for category in ASSET_CATEGORIES:
        create_asset_category(category)

    # Create items
    print("\n📦 Creating Items...")
    for item_data in ITEMS_TO_CREATE:
        create_item(item_data['name'], item_data['item_name'], item_data['category'])

    # Create composite assets at each location
    print("\n🏢 Creating Composite Assets at KPLC Locations...")
    for location, asset_types in LOCATIONS.items():
        print(f"\n  Location: {location}")
        for asset_type in asset_types:
            asset_def = COMPOSITE_ASSETS[asset_type]
            asset_name = f"{asset_type} - {location}"
            if create_composite_asset(asset_name, asset_type, location, asset_def['components']):
                total_created += 1

    # Create specialized equipment
    print("\n\n🔧 Creating Specialized Equipment...")
    for equipment_name, equipment_data in SPECIALIZED_EQUIPMENT.items():
        if create_specialized_equipment(equipment_name, equipment_name, equipment_data):
            total_created += 1

    print("\n" + "=" * 80)
    print(f"✅ COMPLETED - Total assets created: {total_created}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

