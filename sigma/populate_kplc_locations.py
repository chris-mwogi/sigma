#!/usr/bin/env python3
"""
Script to populate KPLC locations in hierarchical structure:
Regions -> Counties -> Offices/Substations/Off-grid Stations
"""

import frappe
import json

# KPLC Locations Data Structure
KPLC_LOCATIONS = {
    "Central Region": {
        "Kiambu County": {
            "offices": ["Kiambu Main Office", "Thika Branch"],
            "substations": [
                {"name": "Kiambu Substation", "subtype": "66/11 kV"},
                {"name": "Thika Substation", "subtype": "33/11 kV"}
            ],
            "offgrid": ["Kiambu Off-grid Station"]
        },
        "Muranga County": {
            "offices": ["Muranga Main Office"],
            "substations": [
                {"name": "Muranga Substation", "subtype": "66/11 kV"}
            ],
            "offgrid": ["Muranga Off-grid Station"]
        },
        "Nyeri County": {
            "offices": ["Nyeri Main Office"],
            "substations": [
                {"name": "Nyeri Substation", "subtype": "33/11 kV"}
            ],
            "offgrid": ["Nyeri Off-grid Station"]
        }
    },
    "Eastern Region": {
        "Machakos County": {
            "offices": ["Machakos Main Office", "Athi River Branch"],
            "substations": [
                {"name": "Machakos Substation", "subtype": "66/11 kV"},
                {"name": "Athi River Substation", "subtype": "33/11 kV"}
            ],
            "offgrid": ["Machakos Off-grid Station"]
        },
        "Makueni County": {
            "offices": ["Makueni Main Office"],
            "substations": [
                {"name": "Makueni Substation", "subtype": "33/11 kV"}
            ],
            "offgrid": ["Makueni Off-grid Station"]
        }
    },
    "Western Region": {
        "Kisumu County": {
            "offices": ["Kisumu Main Office"],
            "substations": [
                {"name": "Kisumu Substation", "subtype": "66/11 kV"}
            ],
            "offgrid": ["Kisumu Off-grid Station"]
        },
        "Nakuru County": {
            "offices": ["Nakuru Main Office", "Naivasha Branch"],
            "substations": [
                {"name": "Nakuru Substation", "subtype": "132/33 kV"},
                {"name": "Naivasha Substation", "subtype": "66/11 kV"}
            ],
            "offgrid": ["Nakuru Off-grid Station"]
        }
    },
    "Nairobi Region": {
        "Nairobi County": {
            "offices": ["Nairobi Main Office", "Westlands Branch", "Industrial Area Branch"],
            "substations": [
                {"name": "Nairobi Central Substation", "subtype": "220/66 kV"},
                {"name": "Westlands Substation", "subtype": "132/33 kV"},
                {"name": "Industrial Area Substation", "subtype": "66/11 kV"}
            ],
            "offgrid": ["Nairobi Off-grid Station"]
        }
    }
}


def create_location(location_name, location_type, parent_location=None, location_subtype=None):
    """Create a location document"""
    try:
        # Check if location already exists
        existing = frappe.db.exists('Location', location_name)
        if existing:
            print(f"  ✓ Location '{location_name}' already exists")
            return location_name
        
        location = frappe.new_doc('Location')
        location.location_name = location_name
        location.location_type = location_type
        
        if parent_location:
            location.parent_location = parent_location
        
        if location_subtype:
            location.location_subtype = location_subtype
        
        location.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  ✓ Created location: {location_name} ({location_type})")
        return location_name
    except Exception as e:
        print(f"  ✗ Error creating location '{location_name}': {str(e)}")
        return None


def main():
    """Main function to populate KPLC locations"""
    print("\n" + "=" * 70)
    print("POPULATING KPLC LOCATIONS")
    print("=" * 70)
    
    total_created = 0
    
    # Iterate through regions
    for region_name, counties in KPLC_LOCATIONS.items():
        print(f"\n📍 Region: {region_name}")
        
        # Create region
        region_created = create_location(region_name, "Region")
        if region_created:
            total_created += 1
        
        # Iterate through counties
        for county_name, locations in counties.items():
            print(f"\n  📍 County: {county_name}")
            
            # Create county
            county_created = create_location(county_name, "County", parent_location=region_name)
            if county_created:
                total_created += 1
            
            # Create offices
            if locations.get("offices"):
                print(f"    📍 Offices:")
                for office_name in locations["offices"]:
                    office_created = create_location(office_name, "Office", parent_location=county_name)
                    if office_created:
                        total_created += 1
            
            # Create substations
            if locations.get("substations"):
                print(f"    📍 Substations:")
                for substation in locations["substations"]:
                    substation_created = create_location(
                        substation["name"],
                        "Substation",
                        parent_location=county_name,
                        location_subtype=substation.get("subtype")
                    )
                    if substation_created:
                        total_created += 1
            
            # Create off-grid stations
            if locations.get("offgrid"):
                print(f"    📍 Off-grid Stations:")
                for offgrid_name in locations["offgrid"]:
                    offgrid_created = create_location(offgrid_name, "Off-grid Station", parent_location=county_name)
                    if offgrid_created:
                        total_created += 1
    
    print("\n" + "=" * 70)
    print(f"✅ COMPLETED - Total locations created/verified: {total_created}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

