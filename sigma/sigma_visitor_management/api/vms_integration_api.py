# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def genetec_webhook_handler():
	"""
	Handle Genetec Security Center webhook events
	
	Receives entry/exit events from Genetec cameras
	"""
	try:
		# Get request data
		data = frappe.request.get_json()
		
		if not data:
			return {"status": "error", "message": "No data provided"}
		
		# Process Genetec event
		event_type = data.get("eventType")
		event_id = data.get("eventId")
		camera_id = data.get("cameraId")
		timestamp = data.get("timestamp")
		location = data.get("location")
		
		# Check for duplicate event
		if frappe.db.exists("VMS Event", {"event_id": event_id}):
			return {"status": "success", "message": "Event already processed"}
		
		# Create VMS event record
		vms_event = frappe.new_doc("VMS Event")
		vms_event.vms_platform = "Genetec"
		vms_event.event_type = "Entry" if event_type == "Entry" else "Exit"
		vms_event.event_id = event_id
		vms_event.event_time = timestamp
		vms_event.camera_id = camera_id
		vms_event.location = location
		vms_event.raw_event_data = json.dumps(data)
		
		# Extract facial recognition data if available
		if "facialRecognition" in data:
			facial_data = data["facialRecognition"]
			vms_event.facial_recognition_confidence = facial_data.get("confidence", 0)
			vms_event.visitor_status = "Registered" if facial_data.get("matched") else "Unregistered"
		
		vms_event.insert(ignore_permissions=True)
		
		return {
			"status": "success",
			"message": "Genetec event processed",
			"event_id": vms_event.name
		}
	
	except Exception as e:
		frappe.log_error(f"Error processing Genetec webhook: {str(e)}")
		return {"status": "error", "message": f"Failed to process event: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def hikvision_webhook_handler():
	"""
	Handle Hikvision VMS webhook events
	
	Receives entry/exit events from Hikvision cameras
	"""
	try:
		# Get request data
		data = frappe.request.get_json()
		
		if not data:
			return {"status": "error", "message": "No data provided"}
		
		# Process Hikvision event
		event_type = data.get("eventType")
		event_id = data.get("eventId")
		camera_id = data.get("cameraId")
		timestamp = data.get("timestamp")
		location = data.get("location")
		
		# Check for duplicate event
		if frappe.db.exists("VMS Event", {"event_id": event_id}):
			return {"status": "success", "message": "Event already processed"}
		
		# Create VMS event record
		vms_event = frappe.new_doc("VMS Event")
		vms_event.vms_platform = "Hikvision"
		vms_event.event_type = "Entry" if event_type == "Entry" else "Exit"
		vms_event.event_id = event_id
		vms_event.event_time = timestamp
		vms_event.camera_id = camera_id
		vms_event.location = location
		vms_event.raw_event_data = json.dumps(data)
		
		# Extract facial recognition data if available
		if "facialRecognition" in data:
			facial_data = data["facialRecognition"]
			vms_event.facial_recognition_confidence = facial_data.get("confidence", 0)
			vms_event.visitor_status = "Registered" if facial_data.get("matched") else "Unregistered"
		
		vms_event.insert(ignore_permissions=True)
		
		return {
			"status": "success",
			"message": "Hikvision event processed",
			"event_id": vms_event.name
		}
	
	except Exception as e:
		frappe.log_error(f"Error processing Hikvision webhook: {str(e)}")
		return {"status": "error", "message": f"Failed to process event: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def link_vms_to_visitor(vms_event_id, visitor_id):
	"""
	Link a VMS event to a visitor record
	
	Args:
		vms_event_id: VMS Event ID
		visitor_id: Visitor ID
	
	Returns:
		Success/error response
	"""
	try:
		if not frappe.db.exists("VMS Event", vms_event_id):
			return {"status": "error", "message": f"VMS Event {vms_event_id} not found"}

		if not frappe.db.exists("Human Profile", visitor_id):
			return {"status": "error", "message": f"Visitor {visitor_id} not found"}
		
		vms_event = frappe.get_doc("VMS Event", vms_event_id)
		vms_event.visitor = visitor_id
		vms_event.is_registered = 1
		vms_event.visitor_status = "Registered"
		vms_event.save(ignore_permissions=True)
		
		return {
			"status": "success",
			"message": "VMS event linked to visitor"
		}
	
	except Exception as e:
		frappe.log_error(f"Error linking VMS to visitor: {str(e)}")
		return {"status": "error", "message": f"Failed to link VMS event: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_unregistered_visitor_alerts(location=None, days=7):
	"""
	Get alerts for unregistered visitors detected by VMS
	
	Args:
		location: Optional location filter
		days: Number of days to look back
	
	Returns:
		List of unregistered visitor events
	"""
	try:
		from sigma.sigma_visitor_management.doctype.vms_event.vms_event import VMSEvent
		
		alerts = VMSEvent.get_unregistered_visitor_events(location, days)
		
		return {
			"status": "success",
			"alerts": alerts,
			"total": len(alerts)
		}
	
	except Exception as e:
		frappe.log_error(f"Error getting unregistered visitor alerts: {str(e)}")
		return {"status": "error", "message": f"Failed to get alerts: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_blacklisted_visitor_alerts(location=None):
	"""
	Get alerts for blacklisted visitors detected by VMS
	
	Args:
		location: Optional location filter
	
	Returns:
		List of blacklisted visitor events
	"""
	try:
		from sigma.sigma_visitor_management.doctype.vms_event.vms_event import VMSEvent
		
		alerts = VMSEvent.get_blacklisted_visitor_events(location)
		
		return {
			"status": "success",
			"alerts": alerts,
			"total": len(alerts)
		}
	
	except Exception as e:
		frappe.log_error(f"Error getting blacklisted visitor alerts: {str(e)}")
		return {"status": "error", "message": f"Failed to get alerts: {str(e)}"}

