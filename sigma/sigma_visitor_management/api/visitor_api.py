# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime, getdate


@frappe.whitelist(allow_guest=False)
def register_visitor(first_name, last_name, visitor_type, location, email=None, phone=None, 
                     company_name=None, purpose_of_visit=None, identification_type=None, 
                     identification_number=None):
	"""
	Register a new visitor or update existing visitor record
	
	Args:
		first_name: Visitor's first name
		last_name: Visitor's last name
		visitor_type: Type of visitor (External Visitor, Inter-Station Staff, Contractor, Vendor)
		location: Location where visitor is registering
		email: Visitor's email
		phone: Visitor's phone
		company_name: Company/Organization name
		purpose_of_visit: Purpose of visit
		identification_type: Type of identification
		identification_number: Identification number
	
	Returns:
		Success/error response with visitor ID
	"""
	try:
		# Check if visitor already exists (using Human Profile with Visitor type)
		full_name = f"{first_name} {last_name}".strip()
		existing = frappe.get_all(
			"Human Profile",
			filters={
				"full_name": full_name,
				"person_type": "Visitor",
				"email": email or ""
			},
			limit_page_length=1
		)

		if existing:
			visitor_id = existing[0]["name"]
			visitor = frappe.get_doc("Human Profile", visitor_id)
		else:
			# Create new visitor as Human Profile
			visitor = frappe.new_doc("Human Profile")
			visitor.full_name = full_name
			visitor.person_type = "Visitor"
			visitor.visitor_type = visitor_type

		# Update visitor details
		visitor.email = email
		visitor.phone = phone
		visitor.company_name = company_name
		visitor.identification_type = identification_type
		visitor.identification_number = identification_number

		visitor.insert(ignore_permissions=True)

		return {
			"status": "success",
			"message": "Visitor registered successfully",
			"visitor_id": visitor.name
		}
	
	except Exception as e:
		frappe.log_error(f"Error registering visitor: {str(e)}")
		return {"status": "error", "message": f"Failed to register visitor: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def check_in_visitor(visitor_id, location, guard_id, check_in_method="Guard-Initiated", 
                     escort_guard=None, notes=None):
	"""
	Check in a visitor
	
	Args:
		visitor_id: Visitor ID
		location: Location where visitor is checking in
		guard_id: Guard performing check-in
		check_in_method: Method of check-in
		escort_guard: Optional escort guard
		notes: Optional notes
	
	Returns:
		Success/error response with check-in record ID
	"""
	try:
		# Validate visitor (now using Human Profile)
		if not frappe.db.exists("Human Profile", visitor_id):
			return {"status": "error", "message": f"Visitor {visitor_id} not found"}

		visitor = frappe.get_doc("Human Profile", visitor_id)
		if visitor.is_blacklisted:
			return {"status": "error", "message": f"Visitor is blacklisted: {visitor.blacklist_reason}"}
		
		# Create check-in record
		checkin = frappe.new_doc("Visitor Checkin Checkout")
		checkin.visitor = visitor_id
		checkin.location = location
		checkin.guard = guard_id
		checkin.escort_guard = escort_guard
		checkin.check_in_time = now_datetime()
		checkin.check_in_method = check_in_method
		checkin.status = "Checked In"
		checkin.notes = notes
		
		checkin.insert(ignore_permissions=True)
		
		return {
			"status": "success",
			"message": "Visitor checked in successfully",
			"checkin_id": checkin.name,
			"check_in_time": str(checkin.check_in_time)
		}
	
	except Exception as e:
		frappe.log_error(f"Error checking in visitor: {str(e)}")
		return {"status": "error", "message": f"Failed to check in visitor: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def check_out_visitor(checkin_id, check_out_method="Guard-Initiated", notes=None):
	"""
	Check out a visitor
	
	Args:
		checkin_id: Check-in record ID
		check_out_method: Method of check-out
		notes: Optional notes
	
	Returns:
		Success/error response
	"""
	try:
		if not frappe.db.exists("Visitor Checkin Checkout", checkin_id):
			return {"status": "error", "message": f"Check-in record {checkin_id} not found"}

		checkin = frappe.get_doc("Visitor Checkin Checkout", checkin_id)
		checkin.check_out_time = now_datetime()
		checkin.check_out_method = check_out_method
		checkin.status = "Checked Out"
		if notes:
			checkin.notes = notes
		
		checkin.save(ignore_permissions=True)
		
		return {
			"status": "success",
			"message": "Visitor checked out successfully",
			"check_out_time": str(checkin.check_out_time),
			"duration_minutes": checkin.duration_minutes
		}
	
	except Exception as e:
		frappe.log_error(f"Error checking out visitor: {str(e)}")
		return {"status": "error", "message": f"Failed to check out visitor: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def search_visitor(search_term):
	"""
	Search for visitors
	
	Args:
		search_term: Search term (name, email, phone)
	
	Returns:
		List of matching visitors
	"""
	try:
		visitors = frappe.get_all(
			"Visitor",
			filters=[
				["first_name", "like", f"%{search_term}%"],
				["last_name", "like", f"%{search_term}%"],
				["email", "like", f"%{search_term}%"],
				["phone", "like", f"%{search_term}%"]
			],
			fields=["name", "first_name", "last_name", "email", "phone", "visitor_type", "is_blacklisted"],
			limit_page_length=20
		)
		
		return {
			"status": "success",
			"visitors": visitors,
			"total": len(visitors)
		}
	
	except Exception as e:
		frappe.log_error(f"Error searching visitors: {str(e)}")
		return {"status": "error", "message": f"Failed to search visitors: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_active_visitors(location=None):
	"""
	Get all currently checked-in visitors
	
	Args:
		location: Optional location filter
	
	Returns:
		List of active visitors
	"""
	try:
		from sigma.sigma_visitor_management.doctype.visitor_checkin_checkout.visitor_checkin_checkout import VisitorCheckInCheckOut
		
		active = VisitorCheckInCheckOut.get_active_visitors(location)
		
		return {
			"status": "success",
			"visitors": active,
			"total": len(active)
		}
	
	except Exception as e:
		frappe.log_error(f"Error getting active visitors: {str(e)}")
		return {"status": "error", "message": f"Failed to get active visitors: {str(e)}"}


@frappe.whitelist(allow_guest=False)
def get_visitor_history(visitor_id, location=None):
	"""
	Get visitor's check-in/check-out history
	
	Args:
		visitor_id: Visitor ID
		location: Optional location filter
	
	Returns:
		List of visitor sessions
	"""
	try:
		from sigma.sigma_visitor_management.doctype.visitor_checkin_checkout.visitor_checkin_checkout import VisitorCheckInCheckOut
		
		history = VisitorCheckInCheckOut.get_visitor_sessions(visitor_id, location)
		
		return {
			"status": "success",
			"history": history,
			"total": len(history)
		}
	
	except Exception as e:
		frappe.log_error(f"Error getting visitor history: {str(e)}")
		return {"status": "error", "message": f"Failed to get visitor history: {str(e)}"}

