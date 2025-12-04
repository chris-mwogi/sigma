#!/usr/bin/env python3
"""
Script to create all Personnel Tracking Module DocTypes.
Run with: bench --site prismod.localhost execute sigma.sigma_personnel.create_doctypes.create_all_doctypes
"""

import frappe
import json
import os

def create_all_doctypes():
	"""Create all PTM DocTypes."""
	
	# DocType definitions
	doctypes = get_doctype_definitions()
	
	for doctype_name, doctype_def in doctypes.items():
		try:
			print(f"\n{'='*80}")
			print(f"Creating DocType: {doctype_name}")
			print(f"{'='*80}")
			
			# Check if DocType already exists
			if frappe.db.exists("DocType", doctype_name):
				print(f"✓ DocType '{doctype_name}' already exists. Skipping...")
				continue
			
			# Create DocType
			doc = frappe.get_doc(doctype_def)
			doc.insert(ignore_permissions=True)
			frappe.db.commit()
			
			print(f"✓ Successfully created DocType: {doctype_name}")
			
		except Exception as e:
			print(f"✗ Error creating DocType '{doctype_name}': {str(e)}")
			frappe.db.rollback()
			import traceback
			traceback.print_exc()
	
	print(f"\n{'='*80}")
	print("DocType creation complete!")
	print(f"{'='*80}\n")

def get_doctype_definitions():
	"""Get all DocType definitions."""
	
	doctypes = {}
	
	# Personnel Check-In
	doctypes["Personnel Check-In"] = {
		"doctype": "DocType",
		"name": "Personnel Check-In",
		"module": "Sigma Personnel",
		"autoname": "format:KPLC-CHECKIN-{YYYY}-{#####}",
		"is_submittable": 1,
		"track_changes": 1,
		"fields": [
			{"fieldname": "human", "fieldtype": "Link", "label": "Human Profile", "options": "Human Profile", "reqd": 1, "in_list_view": 1},
			{"fieldname": "timestamp_in", "fieldtype": "Datetime", "label": "Check-In Time", "reqd": 1, "default": "now", "in_list_view": 1},
			{"fieldname": "entry_gate", "fieldtype": "Data", "label": "Entry Gate", "reqd": 1},
			{"fieldname": "column_break_3", "fieldtype": "Column Break"},
			{"fieldname": "method", "fieldtype": "Select", "label": "Check-In Method", "options": "RFID\nBiometric\nMobile App\nManual\nBLE\nNFC", "reqd": 1},
			{"fieldname": "device_id", "fieldtype": "Link", "label": "Device Used", "options": "Tracking Device"},
			{"fieldname": "initial_zone", "fieldtype": "Link", "label": "Initial Zone", "options": "Zone Configuration", "reqd": 1},
			{"fieldname": "section_break_ppe", "fieldtype": "Section Break", "label": "PPE Verification"},
			{"fieldname": "ppe_verification_status", "fieldtype": "Select", "label": "PPE Verification Status", "options": "Not Required\nVerified\nFailed\nPartial", "default": "Not Required"},
			{"fieldname": "ppe_items_verified", "fieldtype": "Small Text", "label": "PPE Items Verified"},
			{"fieldname": "column_break_ppe", "fieldtype": "Column Break"},
			{"fieldname": "escort_required", "fieldtype": "Check", "label": "Escort Required"},
			{"fieldname": "escort_assigned", "fieldtype": "Link", "label": "Escort Assigned", "options": "Human Profile"},
			{"fieldname": "section_break_purpose", "fieldtype": "Section Break", "label": "Purpose"},
			{"fieldname": "purpose_of_visit", "fieldtype": "Small Text", "label": "Purpose of Visit"}
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1}
		]
	}
	
	# Personnel Check-Out
	doctypes["Personnel Check-Out"] = {
		"doctype": "DocType",
		"name": "Personnel Check-Out",
		"module": "Sigma Personnel",
		"autoname": "format:KPLC-CHECKOUT-{YYYY}-{#####}",
		"is_submittable": 1,
		"track_changes": 1,
		"fields": [
			{"fieldname": "human", "fieldtype": "Link", "label": "Human Profile", "options": "Human Profile", "reqd": 1, "in_list_view": 1},
			{"fieldname": "related_check_in", "fieldtype": "Link", "label": "Related Check-In", "options": "Personnel Check-In"},
			{"fieldname": "timestamp_out", "fieldtype": "Datetime", "label": "Check-Out Time", "reqd": 1, "default": "now", "in_list_view": 1},
			{"fieldname": "column_break_3", "fieldtype": "Column Break"},
			{"fieldname": "exit_gate", "fieldtype": "Data", "label": "Exit Gate", "reqd": 1},
			{"fieldname": "method", "fieldtype": "Select", "label": "Check-Out Method", "options": "RFID\nBiometric\nMobile App\nManual\nBLE\nNFC", "reqd": 1},
			{"fieldname": "duration_onsite", "fieldtype": "Duration", "label": "Duration On-Site", "read_only": 1},
			{"fieldname": "section_break_incident", "fieldtype": "Section Break", "label": "Incident Report"},
			{"fieldname": "incident_note", "fieldtype": "Text", "label": "Incident Note"}
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1}
		]
	}
	
	return doctypes

if __name__ == "__main__":
	create_all_doctypes()

