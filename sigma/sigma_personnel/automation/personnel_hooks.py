# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime

def calculate_risk_score(doc, method):
	"""Calculate risk score for Human Profile."""
	if doc.doctype == "Human Profile":
		doc.calculate_risk_score()

def activate_tracking_devices(doc, method):
	"""Activate tracking devices on Human Profile submit."""
	if doc.doctype == "Human Profile":
		doc.activate_tracking_devices()

def create_initial_zone_presence(doc, method):
	"""Create zone presence on Personnel Check-In submit."""
	if doc.doctype == "Personnel Check-In":
		doc.create_zone_presence()
		doc.create_location_event()

def close_zone_presence(doc, method):
	"""Close zone presence on Personnel Check-Out submit."""
	if doc.doctype == "Personnel Check-Out":
		doc.close_zone_presence()

def update_zone_presence(doc, method):
	"""Update zone presence on Human Location Event insert."""
	if doc.doctype == "Human Location Event":
		doc.update_zone_presence()

