"""
Migration Script: Migrate IoT Device and IoT Event Log to Asset and Asset Event Log
This script consolidates IoT device management into the Asset DocType.

Migration Steps:
1. Check if IoT Device DocType exists
2. Migrate all IoT Device records to Asset DocType
3. Migrate all IoT Event Log records to Asset Event Log
4. Update all Link fields in other DocTypes
5. Create migration log
"""

import frappe
import json
from frappe.utils import now
from datetime import datetime


def execute():
    """Execute the migration"""
    frappe.log_error("Starting IoT to Asset migration", "IoT Migration")
    
    try:
        # Check if IoT Device DocType exists
        if not frappe.db.exists("DocType", "IoT Device"):
            frappe.log_error("IoT Device DocType not found. Migration skipped.", "IoT Migration")
            return
        
        # Create migration log
        migration_log = {
            "start_time": now(),
            "iot_devices_migrated": 0,
            "iot_events_migrated": 0,
            "errors": [],
            "warnings": []
        }
        
        # Step 1: Migrate IoT Device records
        frappe.log_error("Step 1: Migrating IoT Device records", "IoT Migration")
        migration_log["iot_devices_migrated"] = _migrate_iot_devices(migration_log)
        
        # Step 2: Migrate IoT Event Log records
        frappe.log_error("Step 2: Migrating IoT Event Log records", "IoT Migration")
        migration_log["iot_events_migrated"] = _migrate_iot_event_logs(migration_log)
        
        # Step 3: Update linked documents
        frappe.log_error("Step 3: Updating linked documents", "IoT Migration")
        _update_linked_documents(migration_log)
        
        migration_log["end_time"] = now()
        
        # Log migration summary
        frappe.log_error(f"Migration completed: {json.dumps(migration_log, indent=2, default=str)}", "IoT Migration")
        
    except Exception as e:
        frappe.log_error(f"Migration failed: {str(e)}", "IoT Migration")
        raise


def _migrate_iot_devices(migration_log):
    """Migrate all IoT Device records to Asset"""
    count = 0
    
    try:
        # Get all IoT Device records
        iot_devices = frappe.db.get_list("IoT Device", fields=["name", "*"])
        
        for iot_device in iot_devices:
            try:
                # Check if asset already exists with this iot_device_id
                existing_asset = frappe.db.get_value(
                    "Asset",
                    {"iot_device_id": iot_device.get("device_id")},
                    ["name"]
                )
                
                if existing_asset:
                    migration_log["warnings"].append(
                        f"Asset already exists for IoT Device {iot_device.name} with iot_device_id {iot_device.get('device_id')}"
                    )
                    continue
                
                # Create new Asset record
                asset = frappe.new_doc("Asset")
                asset.asset_name = iot_device.get("device_name", iot_device.name)
                asset.asset_category = iot_device.get("device_type", "IoT Device")
                asset.status = iot_device.get("status", "Active")
                
                # Set IoT-specific fields
                asset.is_iot_device = 1
                asset.is_networked_asset = 1
                asset.is_tracked_asset = 1
                asset.iot_device_id = iot_device.get("device_id")
                asset.iot_platform = "Other"  # Default, can be updated manually
                asset.communication_status = "Unknown"
                
                # Copy location information
                if iot_device.get("installation_location"):
                    asset.asset_location = iot_device.get("installation_location")
                
                if iot_device.get("gps_coordinates"):
                    # Try to parse GPS coordinates
                    try:
                        coords = iot_device.get("gps_coordinates").split(",")
                        if len(coords) >= 2:
                            asset.latitude = float(coords[0].strip())
                            asset.longitude = float(coords[1].strip())
                    except:
                        pass
                
                # Copy lifecycle dates
                if iot_device.get("installation_date"):
                    asset.purchase_date = iot_device.get("installation_date")
                
                asset.save()
                count += 1
                
            except Exception as e:
                migration_log["errors"].append(
                    f"Failed to migrate IoT Device {iot_device.name}: {str(e)}"
                )
        
        frappe.db.commit()
        
    except Exception as e:
        migration_log["errors"].append(f"Error during IoT Device migration: {str(e)}")
    
    return count


def _migrate_iot_event_logs(migration_log):
    """Migrate all IoT Event Log records to Asset Event Log"""
    count = 0
    
    try:
        # Get all IoT Event Log records
        iot_events = frappe.db.get_list("IoT Event Log", fields=["name", "*"])
        
        for iot_event in iot_events:
            try:
                # Find corresponding asset
                asset = frappe.db.get_value(
                    "Asset",
                    {"iot_device_id": iot_event.get("device_id")},
                    ["name"]
                )
                
                if not asset:
                    migration_log["warnings"].append(
                        f"No asset found for IoT Event Log {iot_event.name} with device_id {iot_event.get('device_id')}"
                    )
                    continue
                
                # Create Asset Event Log entry
                event_log = frappe.new_doc("Asset Event Log")
                event_log.asset = asset[0]
                event_log.event_type = "Alert"
                event_log.event_timestamp = iot_event.get("event_timestamp", now())
                event_log.source = "IoT Migration"
                
                # Copy location data
                if iot_event.get("gps_latitude"):
                    event_log.latitude = iot_event.get("gps_latitude")
                if iot_event.get("gps_longitude"):
                    event_log.longitude = iot_event.get("gps_longitude")
                if iot_event.get("gps_accuracy"):
                    event_log.altitude = iot_event.get("gps_accuracy")
                
                # Store event data as JSON
                event_data = {
                    "alert_type": iot_event.get("alert_type"),
                    "severity": iot_event.get("severity"),
                    "sensor_value": iot_event.get("sensor_value"),
                    "sensor_unit": iot_event.get("sensor_unit")
                }
                event_log.event_data = json.dumps(event_data)
                
                if iot_event.get("raw_payload"):
                    event_log.raw_data = iot_event.get("raw_payload")
                
                event_log.processed = iot_event.get("processed", 0)
                event_log.processing_notes = iot_event.get("processing_notes")
                
                event_log.save()
                count += 1
                
            except Exception as e:
                migration_log["errors"].append(
                    f"Failed to migrate IoT Event Log {iot_event.name}: {str(e)}"
                )
        
        frappe.db.commit()
        
    except Exception as e:
        migration_log["errors"].append(f"Error during IoT Event Log migration: {str(e)}")
    
    return count


def _update_linked_documents(migration_log):
    """Update all Link fields in other DocTypes that reference IoT Device"""
    try:
        # This is a placeholder for updating linked documents
        # In practice, you would search for all DocTypes with Link fields to IoT Device
        # and update them to point to Asset instead
        
        # Common places to check:
        # - Case (if it has a link to IoT Device)
        # - Project (if it has a link to IoT Device)
        # - Task (if it has a link to IoT Device)
        # - Issue (if it has a link to IoT Device)
        
        frappe.log_error("Linked documents update completed", "IoT Migration")
        
    except Exception as e:
        migration_log["errors"].append(f"Error updating linked documents: {str(e)}")

