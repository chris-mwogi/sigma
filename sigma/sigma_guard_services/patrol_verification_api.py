# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime
from datetime import datetime


@frappe.whitelist(allow_guest=False)
def submit_patrol_verification(data):
	"""
	API endpoint for mobile app to submit patrol verification data.
	
	Expected data format:
	{
		"patrol_schedule": "PS-2025-0001",
		"checkpoint": "PC-LOC-0001",
		"verification_time": "2025-10-24 14:30:00",
		"gps_latitude": 40.7128,
		"gps_longitude": -74.0060,
		"resources_verified": [
			{"resource_type": "Guard", "resource_id": "SR-001", "verification_status": "Present"},
			{"resource_type": "Guard Dog", "resource_id": "SR-002", "verification_status": "Present"}
		],
		"photos": ["base64_encoded_image_1", "base64_encoded_image_2"],
		"notes": "All resources present and accounted for"
	}
	"""
	try:
		# Parse input data
		if isinstance(data, str):
			data = json.loads(data)
		
		# Validate required fields
		required_fields = ["patrol_schedule", "checkpoint", "verification_time"]
		for field in required_fields:
			if field not in data:
				return {
					"status": "error",
					"message": f"Missing required field: {field}"
				}
		
		# Create patrol verification record
		verification = frappe.new_doc("Patrol Verification Record")
		verification.patrol_schedule = data.get("patrol_schedule")
		verification.patrol_date = datetime.strptime(data.get("verification_time"), "%Y-%m-%d %H:%M:%S").date()
		verification.checkpoint = data.get("checkpoint")
		verification.verification_time = data.get("verification_time")
		verification.gps_latitude = data.get("gps_latitude")
		verification.gps_longitude = data.get("gps_longitude")
		verification.notes = data.get("notes", "")
		
		# Add resources verified
		for resource in data.get("resources_verified", []):
			verification.append("resources_verified", {
				"resource_type": resource.get("resource_type"),
				"resource_id": resource.get("resource_id"),
				"verification_status": resource.get("verification_status", "Present"),
				"notes": resource.get("notes", "")
			})
		
		# Save and submit
		verification.insert(ignore_permissions=True)
		verification.submit()
		
		return {
			"status": "success",
			"message": "Patrol verification submitted successfully",
			"verification_id": verification.name,
			"discrepancies_found": verification.discrepancies_found,
			"discrepancy_report": verification.discrepancy_report
		}
		
	except Exception as e:
		frappe.log_error(f"Error submitting patrol verification: {str(e)}")
		return {
			"status": "error",
			"message": f"Failed to submit patrol verification: {str(e)}"
		}


@frappe.whitelist(allow_guest=False)
def get_patrol_schedule(patrol_schedule_id):
	"""
	Get patrol schedule details for mobile app.
	
	Returns schedule with checkpoints and required resources.
	"""
	try:
		if not frappe.db.exists("Patrol Schedule", patrol_schedule_id):
			return {
				"status": "error",
				"message": f"Patrol Schedule {patrol_schedule_id} not found"
			}
		
		schedule = frappe.get_doc("Patrol Schedule", patrol_schedule_id)
		
		# Build response with checkpoint details
		checkpoints = []
		for item in schedule.checkpoints:
			checkpoint = frappe.get_doc("Patrol Checkpoint", item.checkpoint)
			checkpoints.append({
				"checkpoint_id": checkpoint.name,
				"checkpoint_name": checkpoint.checkpoint_name,
				"location": checkpoint.location,
				"gps_latitude": checkpoint.gps_latitude,
				"gps_longitude": checkpoint.gps_longitude,
				"scheduled_time": item.scheduled_time,
				"sequence": item.sequence,
				"required_resources": [
					{
						"resource_type": req.resource_type,
						"required_count": req.required_count
					}
					for req in checkpoint.required_resources
				]
			})
		
		return {
			"status": "success",
			"schedule": {
				"patrol_schedule_id": schedule.name,
				"patrol_date": str(schedule.patrol_date),
				"patrol_officer": schedule.patrol_officer,
				"location": schedule.location,
				"status": schedule.status,
				"checkpoints": checkpoints
			}
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting patrol schedule: {str(e)}")
		return {
			"status": "error",
			"message": f"Failed to get patrol schedule: {str(e)}"
		}


@frappe.whitelist(allow_guest=False)
def get_pending_patrols():
	"""
	Get all pending patrol schedules for the current user.
	
	Returns list of patrol schedules with status "Scheduled" or "In Progress".
	"""
	try:
		# Get current user's security resource
		user = frappe.session.user
		security_resource = frappe.db.get_value(
			"Security Resource",
			{"user": user},
			"name"
		)
		
		if not security_resource:
			return {
				"status": "error",
				"message": "No security resource found for current user"
			}
		
		# Get pending patrols
		patrols = frappe.get_all(
			"Patrol Schedule",
			filters={
				"patrol_officer": security_resource,
				"status": ["in", ["Scheduled", "In Progress"]]
			},
			fields=["name", "patrol_date", "location", "status"],
			order_by="patrol_date asc"
		)
		
		return {
			"status": "success",
			"patrols": patrols
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting pending patrols: {str(e)}")
		return {
			"status": "error",
			"message": f"Failed to get pending patrols: {str(e)}"
		}


@frappe.whitelist(allow_guest=False)
def sync_offline_data(data):
	"""
	Sync offline patrol verification data when connection is restored.
	
	Accepts array of verification records to submit.
	"""
	try:
		if isinstance(data, str):
			data = json.loads(data)
		
		results = []
		for verification_data in data:
			result = submit_patrol_verification(verification_data)
			results.append(result)
		
		return {
			"status": "success",
			"message": f"Synced {len(results)} patrol verifications",
			"results": results
		}
		
	except Exception as e:
		frappe.log_error(f"Error syncing offline data: {str(e)}")
		return {
			"status": "error",
			"message": f"Failed to sync offline data: {str(e)}"
		}

