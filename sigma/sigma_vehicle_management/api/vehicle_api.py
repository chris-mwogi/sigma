# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, now_datetime, get_datetime


@frappe.whitelist()
def vehicle_checkin(license_plate, entry_gate, driver_name=None, visitor_type=None, 
                    vehicle_pass_number=None, is_company_vehicle=0, current_driver=None,
                    odometer_in=None, **kwargs):
	"""
	Process vehicle check-in at gate
	
	Args:
		license_plate: Vehicle license plate number
		entry_gate: Gate/entrance name
		driver_name: Name of driver
		visitor_type: Type of visitor (Local Staff, Visiting Staff, etc.)
		vehicle_pass_number: Vehicle pass number (if applicable)
		is_company_vehicle: Whether this is a company vehicle (0 or 1)
		current_driver: User ID of current driver (for pool vehicles)
		odometer_in: Odometer reading at check-in (for company vehicles)
		**kwargs: Additional fields
	
	Returns:
		dict: Created Vehicle Checkin Checkout record
	"""
	try:
		# Check if vehicle exists
		vehicle_record = frappe.db.get_value("Vehicle", {"license_plate": license_plate}, "name")
		
		# Validate vehicle pass for non-company vehicles
		if not is_company_vehicle and not vehicle_pass_number:
			# Check if vehicle requires a pass
			if vehicle_record:
				requires_pass = frappe.db.get_value("Vehicle", vehicle_record, "requires_pass")
				if requires_pass:
					frappe.throw(_("Vehicle pass is required for this vehicle"))
		
		# Validate vehicle pass if provided
		if vehicle_pass_number:
			pass_doc = frappe.get_doc("Vehicle Pass", vehicle_pass_number)
			if pass_doc.status != "Active":
				frappe.throw(_("Vehicle pass is not active"))
			if pass_doc.license_plate != license_plate:
				frappe.throw(_("Vehicle pass does not match license plate"))
		
		# Create check-in record
		checkin = frappe.get_doc({
			"doctype": "Vehicle Checkin Checkout",
			"license_plate": license_plate,
			"vehicle_record": vehicle_record or "",
			"check_in_time": now_datetime(),
			"entry_gate": entry_gate,
			"guard_in": frappe.session.user,
			"driver_name": driver_name,
			"visitor_type": visitor_type,
			"vehicle_pass_number": vehicle_pass_number or "",
			"is_company_vehicle": is_company_vehicle,
			"current_driver": current_driver or "",
			"odometer_in": odometer_in,
			"status": "Checked In"
		})
		
		# Add any additional fields from kwargs
		for key, value in kwargs.items():
			if hasattr(checkin, key):
				setattr(checkin, key, value)
		
		checkin.insert()
		frappe.db.commit()
		
		# Create access log entry
		create_access_log(
			event_type="Check-In",
			license_plate=license_plate,
			vehicle_record=vehicle_record or "",
			location=entry_gate,
			linked_checkin=checkin.name
		)
		
		return {
			"success": True,
			"message": _("Vehicle checked in successfully"),
			"checkin_id": checkin.name,
			"data": checkin.as_dict()
		}
	
	except Exception as e:
		frappe.log_error(f"Vehicle check-in error: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def vehicle_checkout(checkin_id, exit_gate, odometer_out=None, **kwargs):
	"""
	Process vehicle check-out at gate
	
	Args:
		checkin_id: Vehicle Checkin Checkout record ID
		exit_gate: Gate/exit name
		odometer_out: Odometer reading at check-out (for company vehicles)
		**kwargs: Additional fields
	
	Returns:
		dict: Updated Vehicle Checkin Checkout record
	"""
	try:
		# Get check-in record
		checkin = frappe.get_doc("Vehicle Checkin Checkout", checkin_id)
		
		if checkin.status == "Checked Out":
			frappe.throw(_("Vehicle is already checked out"))
		
		# Update check-out information
		checkin.check_out_time = now_datetime()
		checkin.exit_gate = exit_gate
		checkin.guard_out = frappe.session.user
		checkin.status = "Checked Out"
		
		if odometer_out:
			checkin.odometer_out = odometer_out
		
		# Add any additional fields from kwargs
		for key, value in kwargs.items():
			if hasattr(checkin, key):
				setattr(checkin, key, value)
		
		checkin.save()
		frappe.db.commit()
		
		# Release parking space if assigned
		if checkin.parking_space_assigned:
			release_parking_space(checkin.parking_space_assigned)
		
		# Create access log entry
		create_access_log(
			event_type="Check-Out",
			license_plate=checkin.license_plate,
			vehicle_record=checkin.vehicle_record,
			location=exit_gate,
			linked_checkin=checkin.name
		)
		
		return {
			"success": True,
			"message": _("Vehicle checked out successfully"),
			"data": checkin.as_dict()
		}
	
	except Exception as e:
		frappe.log_error(f"Vehicle check-out error: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def issue_vehicle_pass(license_plate, pass_type, expiry_date, issued_to_name, 
                       issued_to_contact=None, authorized_areas=None, parking_zone=None):
	"""
	Issue a vehicle pass
	
	Args:
		license_plate: Vehicle license plate number
		pass_type: Type of pass (Daily, Weekly, Monthly, Permanent, Temporary)
		expiry_date: Pass expiry date
		issued_to_name: Name of person pass is issued to
		issued_to_contact: Contact number
		authorized_areas: Areas vehicle can access
		parking_zone: Authorized parking zone
	
	Returns:
		dict: Created Vehicle Pass record
	"""
	try:
		# Check if vehicle exists
		vehicle_record = frappe.db.get_value("Vehicle", {"license_plate": license_plate}, "name")
		
		# Create vehicle pass
		vehicle_pass = frappe.get_doc({
			"doctype": "Vehicle Pass",
			"pass_type": pass_type,
			"license_plate": license_plate,
			"vehicle_record": vehicle_record or "",
			"issue_date": now_datetime().date(),
			"expiry_date": expiry_date,
			"issued_to_name": issued_to_name,
			"issued_to_contact": issued_to_contact or "",
			"issued_by_guard": frappe.session.user,
			"authorized_areas": authorized_areas or "",
			"parking_zone": parking_zone or "",
			"status": "Active"
		})
		
		vehicle_pass.insert()
		frappe.db.commit()
		
		# Create access log entry
		create_access_log(
			event_type="Pass Issued",
			license_plate=license_plate,
			vehicle_record=vehicle_record or "",
			linked_pass=vehicle_pass.name,
			description=f"Vehicle pass {vehicle_pass.name} issued to {issued_to_name}"
		)
		
		return {
			"success": True,
			"message": _("Vehicle pass issued successfully"),
			"pass_id": vehicle_pass.name,
			"data": vehicle_pass.as_dict()
		}
	
	except Exception as e:
		frappe.log_error(f"Vehicle pass issuance error: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def assign_parking(checkin_id, space_number):
	"""
	Assign parking space to a vehicle
	
	Args:
		checkin_id: Vehicle Checkin Checkout record ID
		space_number: Parking space number
	
	Returns:
		dict: Success status and message
	"""
	try:
		# Get check-in record
		checkin = frappe.get_doc("Vehicle Checkin Checkout", checkin_id)
		
		# Check if parking space is available
		parking_space = frappe.get_doc("Parking Space", space_number)
		
		if parking_space.status != "Available":
			frappe.throw(_("Parking space is not available"))
		
		# Update check-in record
		checkin.parking_space_assigned = space_number
		checkin.save()
		
		# Update parking space
		parking_space.status = "Occupied"
		parking_space.current_vehicle = checkin.license_plate
		parking_space.current_checkin = checkin.name
		parking_space.save()
		
		frappe.db.commit()
		
		# Create access log entry
		create_access_log(
			event_type="Parking Assigned",
			license_plate=checkin.license_plate,
			vehicle_record=checkin.vehicle_record,
			location=space_number,
			linked_checkin=checkin.name,
			description=f"Parking space {space_number} assigned"
		)
		
		return {
			"success": True,
			"message": _("Parking space assigned successfully"),
			"space_number": space_number
		}
	
	except Exception as e:
		frappe.log_error(f"Parking assignment error: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def process_vms_vehicle_event(vms_event_id, license_plate, camera_id, event_type="Check-In", **kwargs):
	"""
	Process VMS vehicle event (ALPR integration)
	
	Args:
		vms_event_id: VMS Event record ID
		license_plate: Detected license plate number
		camera_id: Camera ID that captured the event
		event_type: Type of event (Check-In or Check-Out)
		**kwargs: Additional fields (snapshot, etc.)
	
	Returns:
		dict: Success status and message
	"""
	try:
		# This would integrate with VMS Event doctype
		# For now, just create an access log entry
		
		vehicle_record = frappe.db.get_value("Vehicle", {"license_plate": license_plate}, "name")
		
		create_access_log(
			event_type=event_type,
			license_plate=license_plate,
			vehicle_record=vehicle_record or "",
			vms_event=vms_event_id,
			camera_id=camera_id,
			description=f"VMS event captured by camera {camera_id}"
		)
		
		return {
			"success": True,
			"message": _("VMS vehicle event processed successfully"),
			"vms_event_id": vms_event_id
		}
	
	except Exception as e:
		frappe.log_error(f"VMS event processing error: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


def create_access_log(event_type, license_plate, vehicle_record="", location="", 
                      linked_checkin="", linked_pass="", vms_event="", camera_id="", 
                      description="", **kwargs):
	"""
	Create a vehicle access log entry
	
	Args:
		event_type: Type of event
		license_plate: Vehicle license plate
		vehicle_record: Vehicle record ID
		location: Location of event
		linked_checkin: Linked checkin record
		linked_pass: Linked pass record
		vms_event: VMS event ID
		camera_id: Camera ID
		description: Event description
	"""
	try:
		access_log = frappe.get_doc({
			"doctype": "Vehicle Access Log",
			"timestamp": now_datetime(),
			"event_type": event_type,
			"license_plate": license_plate,
			"vehicle_record": vehicle_record,
			"location": location,
			"guard": frappe.session.user,
			"linked_checkin": linked_checkin,
			"linked_pass": linked_pass,
			"vms_event": vms_event,
			"camera_id": camera_id,
			"description": description
		})
		
		access_log.insert(ignore_permissions=True)
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Access log creation error: {str(e)}")


def release_parking_space(space_number):
	"""
	Release a parking space
	
	Args:
		space_number: Parking space number
	"""
	try:
		parking_space = frappe.get_doc("Parking Space", space_number)
		parking_space.status = "Available"
		parking_space.current_vehicle = ""
		parking_space.current_checkin = ""
		parking_space.save()
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Parking space release error: {str(e)}")

