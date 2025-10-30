# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime
from datetime import datetime


@frappe.whitelist(allow_guest=False)
def assign_visitor_to_guard(visitor_id, guard_id, location_id=None):
	"""
	Assign a visitor to a guard for escort.
	
	Args:
		visitor_id: Visitor document ID
		guard_id: Security Resource (Guard) ID
		location_id: Optional location ID
	
	Returns:
		Success/error response with assignment ID
	"""
	try:
		# Validate inputs
		if not frappe.db.exists("Visitor", visitor_id):
			return {"status": "error", "message": f"Visitor {visitor_id} not found"}
		
		if not frappe.db.exists("Security Resource", guard_id):
			return {"status": "error", "message": f"Guard {guard_id} not found"}
		
		# Create assignment
		assignment = frappe.new_doc("Visitor Guard Assignment")
		assignment.visitor = visitor_id
		assignment.guard = guard_id
		assignment.location = location_id
		assignment.assignment_time = now_datetime()
		assignment.status = "Assigned"
		
		assignment.insert(ignore_permissions=True)
		assignment.submit()
		
		return {
			"status": "success",
			"message": "Visitor assigned to guard successfully",
			"assignment_id": assignment.name
		}
		
	except Exception as e:
		frappe.log_error(f"Error assigning visitor to guard: {str(e)}")
		return {"status": "error", "message": f"Failed to assign visitor: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def check_out_visitor(assignment_id):
	"""
	Check out a visitor and end the assignment.
	
	Args:
		assignment_id: Visitor Guard Assignment ID
	
	Returns:
		Success/error response
	"""
	try:
		if not frappe.db.exists("Visitor Guard Assignment", assignment_id):
			return {"status": "error", "message": f"Assignment {assignment_id} not found"}
		
		assignment = frappe.get_doc("Visitor Guard Assignment", assignment_id)
		assignment.mark_checked_out()
		
		return {
			"status": "success",
			"message": "Visitor checked out successfully",
			"check_out_time": str(assignment.check_out_time)
		}
		
	except Exception as e:
		frappe.log_error(f"Error checking out visitor: {str(e)}")
		return {"status": "error", "message": f"Failed to check out visitor: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def initiate_evacuation(location_id, evacuation_type):
	"""
	Initiate an emergency evacuation.
	
	Args:
		location_id: Location ID
		evacuation_type: Type of evacuation (Fire, Medical Emergency, etc.)
	
	Returns:
		Success/error response with evacuation tracking ID
	"""
	try:
		if not frappe.db.exists("Location", location_id):
			return {"status": "error", "message": f"Location {location_id} not found"}
		
		# Get all active visitor-guard assignments at this location
		assignments = frappe.get_all(
			"Visitor Guard Assignment",
			filters={
				"location": location_id,
				"status": ["in", ["Assigned", "Escorting"]],
				"docstatus": 1
			},
			fields=["name", "visitor", "guard"]
		)
		
		# Create evacuation tracking
		evacuation = frappe.new_doc("Emergency Evacuation Tracking")
		evacuation.location = location_id
		evacuation.evacuation_date = datetime.now().date()
		evacuation.evacuation_type = evacuation_type
		evacuation.evacuation_start_time = now_datetime()
		evacuation.status = "Initiated"
		
		# Add assigned visitors
		for assignment in assignments:
			evacuation.append("assigned_visitors", {
				"visitor": assignment["visitor"],
				"guard": assignment["guard"],
				"visitor_guard_assignment": assignment["name"],
				"evacuated": 0
			})
		
		evacuation.insert(ignore_permissions=True)
		evacuation.submit()
		
		return {
			"status": "success",
			"message": "Evacuation initiated successfully",
			"evacuation_id": evacuation.name,
			"total_visitors": len(assignments)
		}
		
	except Exception as e:
		frappe.log_error(f"Error initiating evacuation: {str(e)}")
		return {"status": "error", "message": f"Failed to initiate evacuation: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def mark_visitor_evacuated(evacuation_id, visitor_guard_assignment_id):
	"""
	Mark a visitor as evacuated.
	
	Args:
		evacuation_id: Emergency Evacuation Tracking ID
		visitor_guard_assignment_id: Visitor Guard Assignment ID
	
	Returns:
		Success/error response
	"""
	try:
		if not frappe.db.exists("Emergency Evacuation Tracking", evacuation_id):
			return {"status": "error", "message": f"Evacuation {evacuation_id} not found"}
		
		evacuation = frappe.get_doc("Emergency Evacuation Tracking", evacuation_id)
		evacuation.mark_visitor_evacuated(visitor_guard_assignment_id)
		
		return {
			"status": "success",
			"message": "Visitor marked as evacuated",
			"total_evacuated": evacuation.total_evacuated,
			"evacuation_percentage": (evacuation.total_evacuated / evacuation.total_visitors * 100) if evacuation.total_visitors > 0 else 0
		}
		
	except Exception as e:
		frappe.log_error(f"Error marking visitor evacuated: {str(e)}")
		return {"status": "error", "message": f"Failed to mark visitor evacuated: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_evacuation_report(evacuation_id):
	"""
	Get evacuation report.
	
	Args:
		evacuation_id: Emergency Evacuation Tracking ID
	
	Returns:
		Evacuation report with statistics
	"""
	try:
		if not frappe.db.exists("Emergency Evacuation Tracking", evacuation_id):
			return {"status": "error", "message": f"Evacuation {evacuation_id} not found"}
		
		evacuation = frappe.get_doc("Emergency Evacuation Tracking", evacuation_id)
		report = evacuation.get_evacuation_report()
		
		return {
			"status": "success",
			"report": report
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting evacuation report: {str(e)}")
		return {"status": "error", "message": f"Failed to get evacuation report: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_active_assignments(location_id=None):
	"""
	Get all active visitor-guard assignments.
	
	Args:
		location_id: Optional location filter
	
	Returns:
		List of active assignments
	"""
	try:
		filters = {
			"status": ["in", ["Assigned", "Escorting"]],
			"docstatus": 1
		}
		
		if location_id:
			filters["location"] = location_id
		
		assignments = frappe.get_all(
			"Visitor Guard Assignment",
			filters=filters,
			fields=["name", "visitor", "guard", "location", "status", "assignment_time"],
			order_by="assignment_time desc"
		)
		
		return {
			"status": "success",
			"assignments": assignments,
			"total": len(assignments)
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting active assignments: {str(e)}")
		return {"status": "error", "message": f"Failed to get active assignments: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_guard_assignments(guard_id):
	"""
	Get all assignments for a specific guard.
	
	Args:
		guard_id: Security Resource (Guard) ID
	
	Returns:
		List of guard's assignments
	"""
	try:
		if not frappe.db.exists("Security Resource", guard_id):
			return {"status": "error", "message": f"Guard {guard_id} not found"}
		
		assignments = frappe.get_all(
			"Visitor Guard Assignment",
			filters={
				"guard": guard_id,
				"status": ["in", ["Assigned", "Escorting"]],
				"docstatus": 1
			},
			fields=["name", "visitor", "location", "status", "assignment_time"],
			order_by="assignment_time desc"
		)
		
		return {
			"status": "success",
			"assignments": assignments,
			"total": len(assignments)
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting guard assignments: {str(e)}")
		return {"status": "error", "message": f"Failed to get guard assignments: {str(e)}"}

