"""
IoT Integration API - IoT device and alert handling
Refactored to use Asset DocType as the single source of truth for IoT devices
"""
import frappe
from frappe.utils import now, today
import json


@frappe.whitelist(allow_guest=True)
def iot_alert_webhook(device_id, alert_type, severity, gps_latitude=None,
                      gps_longitude=None, sensor_value=None, raw_payload=None):
    """
    Webhook endpoint for IoT alerts
    Now creates Asset Event Log entries for assets with is_iot_device=1

    Args:
        device_id: IoT device ID (maps to Asset.iot_device_id)
        alert_type: Type of alert
        severity: Severity level
        gps_latitude: GPS latitude
        gps_longitude: GPS longitude
        sensor_value: Sensor reading value
        raw_payload: Raw JSON payload

    Returns:
        Event log document
    """
    try:
        # Find asset with matching iot_device_id
        asset = frappe.db.get_value("Asset", {"iot_device_id": device_id}, ["name"])
        if not asset:
            frappe.throw(f"IoT Device {device_id} not found")

        # Create Asset Event Log entry
        event_log = frappe.new_doc("Asset Event Log")
        event_log.asset = asset[0]
        event_log.event_type = "Alert"
        event_log.event_timestamp = now()
        event_log.source = "IoT Webhook"

        if gps_latitude:
            event_log.latitude = gps_latitude
        if gps_longitude:
            event_log.longitude = gps_longitude

        # Store event data as JSON
        event_data = {
            "alert_type": alert_type,
            "severity": severity,
            "sensor_value": sensor_value
        }
        event_log.event_data = json.dumps(event_data)

        if raw_payload:
            event_log.raw_data = raw_payload if isinstance(raw_payload, str) else json.dumps(raw_payload)

        event_log.save()
        frappe.db.commit()

        return {
            "status": "success",
            "event_id": event_log.name,
            "device_id": device_id,
            "alert_type": alert_type
        }
    except Exception as e:
        frappe.log_error(f"Failed to process IoT alert: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def link_asset_event_to_case(event_log_name, case_name):
    """
    Link Asset Event Log to case

    Args:
        event_log_name: Asset Event Log name
        case_name: Case name

    Returns:
        Updated event log
    """
    try:
        event_log = frappe.get_doc("Asset Event Log", event_log_name)
        # Store case link in processing_notes for now
        event_log.processing_notes = f"Linked to Case: {case_name}"
        event_log.processed = 1
        event_log.save()

        return event_log
    except Exception as e:
        frappe.log_error(f"Failed to link Asset event to case: {str(e)}")
        frappe.throw(f"Failed to link Asset event to case: {str(e)}")


@frappe.whitelist()
def get_iot_device_status(device_id):
    """
    Get current status of IoT device (Asset with is_iot_device=1)

    Args:
        device_id: IoT device ID (Asset.iot_device_id)

    Returns:
        Device status
    """
    try:
        device = frappe.db.get_value("Asset", {"iot_device_id": device_id},
                                     ["name", "asset_name", "status", "communication_status",
                                      "last_communication", "asset_location"])

        if not device:
            frappe.throw(f"IoT Device {device_id} not found")

        return {
            "device_id": device_id,
            "asset_name": device[1],
            "status": device[2],
            "communication_status": device[3],
            "last_communication": device[4],
            "location": device[5]
        }
    except Exception as e:
        frappe.log_error(f"Failed to get device status: {str(e)}")
        frappe.throw(f"Failed to get device status: {str(e)}")


@frappe.whitelist()
def get_iot_alerts(device_id=None, event_type=None, days=7):
    """
    Get IoT alerts from Asset Event Log

    Args:
        device_id: Filter by IoT device ID (Asset.iot_device_id) (optional)
        event_type: Filter by event type (optional)
        days: Number of days to look back (default 7)

    Returns:
        List of alerts
    """
    try:
        filters = {"event_type": "Alert"}

        if device_id:
            # Find asset with this iot_device_id
            asset = frappe.db.get_value("Asset", {"iot_device_id": device_id}, ["name"])
            if asset:
                filters["asset"] = asset[0]

        if event_type:
            filters["event_type"] = event_type

        # Add date filter
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)
        filters["event_timestamp"] = [">", start_date.isoformat()]

        alerts = frappe.db.get_list(
            "Asset Event Log",
            filters=filters,
            fields=["name", "asset", "event_type", "event_timestamp", "source", "latitude", "longitude"],
            order_by="event_timestamp desc"
        )

        return alerts
    except Exception as e:
        frappe.log_error(f"Failed to get IoT alerts: {str(e)}")
        frappe.throw(f"Failed to get IoT alerts: {str(e)}")


@frappe.whitelist()
def update_device_heartbeat(device_id, communication_status=None):
    """
    Update device heartbeat and communication status

    Args:
        device_id: IoT device ID (Asset.iot_device_id)
        communication_status: Current communication status (Online/Offline/Unknown)

    Returns:
        Updated asset
    """
    try:
        asset = frappe.db.get_value("Asset", {"iot_device_id": device_id}, ["name"])
        if not asset:
            frappe.throw(f"IoT Device {device_id} not found")

        asset_doc = frappe.get_doc("Asset", asset[0])
        asset_doc.last_communication = now()

        if communication_status:
            asset_doc.communication_status = communication_status
        else:
            asset_doc.communication_status = "Online"

        asset_doc.save()

        return asset_doc
    except Exception as e:
        frappe.log_error(f"Failed to update device heartbeat: {str(e)}")
        frappe.throw(f"Failed to update device heartbeat: {str(e)}")


@frappe.whitelist()
def decommission_iot_device(device_id, reason):
    """
    Decommission IoT device (Asset with is_iot_device=1)

    Args:
        device_id: IoT device ID (Asset.iot_device_id)
        reason: Reason for decommissioning

    Returns:
        Updated asset
    """
    try:
        asset = frappe.db.get_value("Asset", {"iot_device_id": device_id}, ["name"])
        if not asset:
            frappe.throw(f"IoT Device {device_id} not found")

        asset_doc = frappe.get_doc("Asset", asset[0])
        asset_doc.status = "Fully Depreciated"
        asset_doc.communication_status = "Offline"
        asset_doc.is_iot_device = 0
        asset_doc.save()

        return asset_doc
    except Exception as e:
        frappe.log_error(f"Failed to decommission device: {str(e)}")
        frappe.throw(f"Failed to decommission device: {str(e)}")

