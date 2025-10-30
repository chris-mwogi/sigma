# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class VMSEvent(Document):
	"""
	VMS Event DocType
	
	Stores camera events from VMS platforms (Genetec, Hikvision)
	Integrates with visitor records for comprehensive tracking
	"""
	
	def validate(self):
		"""Validate VMS event"""
		self.validate_event_id()
		self.validate_location()
		self.validate_visitor_status()
	
	def validate_event_id(self):
		"""Validate event ID is unique"""
		existing = frappe.db.exists("VMS Event", {"event_id": self.event_id})
		if existing and existing != self.name:
			frappe.throw(f"Event ID {self.event_id} already exists")
	
	def validate_location(self):
		"""Validate location exists"""
		if not frappe.db.exists("Location", self.location):
			frappe.throw(f"Location {self.location} not found")
	
	def validate_visitor_status(self):
		"""Validate visitor status"""
		if self.visitor and not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
		
		# Check if visitor is blacklisted
		if self.visitor:
			visitor = frappe.get_doc("Visitor", self.visitor)
			if visitor.is_blacklisted:
				self.visitor_status = "Blacklisted"
	
	def on_insert(self):
		"""Handle VMS event insertion"""
		self.process_event()
	
	def process_event(self):
		"""Process VMS event and link to visitor records"""
		try:
			# Try to match visitor based on facial recognition
			if self.facial_recognition_confidence and self.facial_recognition_confidence > 80:
				self.match_visitor_by_facial_recognition()
			
			# Create access log entry
			self.create_access_log_entry()
			
			# Check for unregistered visitors
			if not self.is_registered and self.event_type in ["Entry", "Facial Recognition"]:
				self.flag_unregistered_visitor()
			
			self.processed = 1
			self.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error processing VMS event: {str(e)}")
			self.processing_notes = f"Error: {str(e)}"
	
	def match_visitor_by_facial_recognition(self):
		"""Match visitor using facial recognition"""
		# This would integrate with VMS facial recognition system
		# For now, we'll store the facial ID for manual matching
		pass
	
	def create_access_log_entry(self):
		"""Create visitor access log entry"""
		try:
			log_entry = frappe.get_doc({
				"doctype": "Visitor Access Log",
				"visitor": self.visitor,
				"location": self.location,
				"activity_type": "Area Access" if self.event_type == "Entry" else self.event_type,
				"timestamp": self.event_time,
				"camera_id": self.camera_id,
				"vms_event": self.name,
				"access_granted": 1 if not self.visitor_status == "Blacklisted" else 0,
				"access_reason": f"VMS {self.vms_platform} Event"
			})
			log_entry.insert(ignore_permissions=True)
			self.linked_access_log = log_entry.name
		except Exception as e:
			frappe.log_error(f"Error creating access log: {str(e)}")
	
	def flag_unregistered_visitor(self):
		"""Flag unregistered visitor alert"""
		try:
			alert = frappe.get_doc({
				"doctype": "Visitor Access Log",
				"visitor": self.visitor or "Unknown",
				"location": self.location,
				"activity_type": "Incident",
				"timestamp": self.event_time,
				"camera_id": self.camera_id,
				"vms_event": self.name,
				"access_granted": 0,
				"access_reason": "Unregistered visitor detected by VMS"
			})
			alert.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error flagging unregistered visitor: {str(e)}")
	
	@staticmethod
	def get_unprocessed_events():
		"""Get unprocessed VMS events"""
		return frappe.get_all(
			"VMS Event",
			filters={"processed": 0},
			fields=["name", "vms_platform", "event_type", "event_time", "location", "visitor"],
			order_by="event_time asc"
		)
	
	@staticmethod
	def get_unregistered_visitor_events(location=None, days=7):
		"""Get events for unregistered visitors"""
		from frappe.utils import add_days, get_datetime
		
		filters = {"is_registered": 0}
		if location:
			filters["location"] = location
		
		start_date = add_days(get_datetime(), -days)
		filters["event_time"] = [">=", start_date]
		
		return frappe.get_all(
			"VMS Event",
			filters=filters,
			fields=["name", "event_type", "event_time", "location", "camera_id", "visitor_status"],
			order_by="event_time desc"
		)
	
	@staticmethod
	def get_blacklisted_visitor_events(location=None):
		"""Get events for blacklisted visitors"""
		filters = {"visitor_status": "Blacklisted"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"VMS Event",
			filters=filters,
			fields=["name", "event_type", "event_time", "location", "visitor", "camera_id"],
			order_by="event_time desc"
		)

