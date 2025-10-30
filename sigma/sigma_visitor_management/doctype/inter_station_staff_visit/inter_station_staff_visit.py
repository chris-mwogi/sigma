# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class InterStationStaffVisit(Document):
	"""
	Inter-Station Staff Visit DocType
	
	Tracks staff members from other locations visiting this location
	"""
	
	def validate(self):
		"""Validate visit record"""
		self.validate_employee()
		self.validate_locations()
		self.validate_times()
		self.validate_guard()
	
	def validate_employee(self):
		"""Validate employee exists"""
		if not frappe.db.exists("Employee", self.employee):
			frappe.throw(f"Employee {self.employee} not found")
	
	def validate_locations(self):
		"""Validate locations"""
		if not frappe.db.exists("Location", self.home_location):
			frappe.throw(f"Home Location {self.home_location} not found")
		
		if not frappe.db.exists("Location", self.visiting_location):
			frappe.throw(f"Visiting Location {self.visiting_location} not found")
		
		if self.home_location == self.visiting_location:
			frappe.throw("Home Location and Visiting Location cannot be the same")
	
	def validate_times(self):
		"""Validate times"""
		if self.check_out_time and self.check_in_time >= self.check_out_time:
			frappe.throw("Check-Out Time must be after Check-In Time")
	
	def validate_guard(self):
		"""Validate guard exists"""
		if not frappe.db.exists("Security Resource", self.check_in_guard):
			frappe.throw(f"Guard {self.check_in_guard} not found")
	
	def on_update(self):
		"""Handle visit updates"""
		self.update_duration()
	
	def update_duration(self):
		"""Calculate duration in hours"""
		if self.check_out_time:
			check_in = get_datetime(self.check_in_time)
			check_out = get_datetime(self.check_out_time)
			duration = (check_out - check_in).total_seconds() / 3600
			self.duration_hours = round(duration, 2)
	
	def mark_checked_out(self, check_out_guard):
		"""Mark staff as checked out"""
		self.check_out_time = now_datetime()
		self.check_out_guard = check_out_guard
		self.status = "Checked Out"
		self.update_duration()
		self.save(ignore_permissions=True)
	
	@staticmethod
	def get_active_visits(location=None):
		"""Get all currently checked-in inter-station staff"""
		filters = {"status": "Checked In"}
		if location:
			filters["visiting_location"] = location
		
		return frappe.get_all(
			"Inter-Station Staff Visit",
			filters=filters,
			fields=["name", "employee", "home_location", "visiting_location", "check_in_time"],
			order_by="check_in_time desc"
		)
	
	@staticmethod
	def get_employee_visits(employee_id, location=None):
		"""Get all visits for an employee"""
		filters = {"employee": employee_id}
		if location:
			filters["visiting_location"] = location
		
		return frappe.get_all(
			"Inter-Station Staff Visit",
			filters=filters,
			fields=["name", "visiting_location", "visit_date", "check_in_time", "check_out_time", "status"],
			order_by="visit_date desc"
		)
	
	@staticmethod
	def get_location_visits(location, date=None):
		"""Get all inter-station staff visits at a location"""
		filters = {"visiting_location": location}
		if date:
			filters["visit_date"] = date
		
		return frappe.get_all(
			"Inter-Station Staff Visit",
			filters=filters,
			fields=["name", "employee", "check_in_time", "check_out_time", "status"],
			order_by="check_in_time desc"
		)
	
	@staticmethod
	def get_visit_frequency_report(location=None, days=30):
		"""Get visit frequency report"""
		from frappe.utils import add_days, get_datetime
		
		filters = {}
		if location:
			filters["visiting_location"] = location
		
		start_date = add_days(get_datetime(), -days)
		filters["visit_date"] = [">=", start_date]
		
		visits = frappe.get_all(
			"Inter-Station Staff Visit",
			filters=filters,
			fields=["employee", "visiting_location", "visit_date"],
			order_by="visit_date desc"
		)
		
		# Group by employee
		employee_visits = {}
		for visit in visits:
			emp = visit["employee"]
			if emp not in employee_visits:
				employee_visits[emp] = 0
			employee_visits[emp] += 1
		
		return employee_visits

