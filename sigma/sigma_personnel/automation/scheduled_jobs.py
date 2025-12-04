# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, add_to_date, time_diff_in_seconds

def check_lone_workers_every_5_minutes():
	"""Check for lone workers in hazardous zones (ISO 45001)."""
	# Get all active zone presences
	presences = frappe.get_all("Zone Presence",
		filters={"status": "Active"},
		fields=["name", "human", "zone", "time_entered", "last_seen"]
	)
	
	for presence in presences:
		zone = frappe.get_doc("Zone Configuration", presence.zone)
		
		# Check if lone worker alert is configured
		if zone.lone_worker_alert_minutes and zone.lone_worker_alert_minutes > 0:
			# Count personnel in zone
			count = frappe.db.count("Zone Presence", {
				"zone": presence.zone,
				"status": "Active"
			})
			
			# If only one person in zone
			if count == 1:
				duration_seconds = time_diff_in_seconds(now_datetime(), presence.time_entered)
				duration_minutes = duration_seconds / 60
				
				# Check if exceeded threshold
				if duration_minutes > zone.lone_worker_alert_minutes:
					# Check if alert already exists
					existing_alert = frappe.db.exists("Lone Worker Alert", {
						"human": presence.human,
						"zone": presence.zone,
						"resolution_status": ["in", ["Open", "Acknowledged"]],
						"alert_type": "Lone Worker Timeout"
					})
					
					if not existing_alert:
						# Create alert
						frappe.get_doc({
							"doctype": "Lone Worker Alert",
							"human": presence.human,
							"alert_type": "Lone Worker Timeout",
							"zone": presence.zone,
							"severity": "High",
							"resolution_status": "Open"
						}).insert(ignore_permissions=True)
						frappe.db.commit()

def check_overdue_checkouts():
	"""Check for personnel who haven't checked out (ISO 22301)."""
	# Get check-ins from more than 24 hours ago without checkout
	from frappe.utils import add_to_date
	
	cutoff_time = add_to_date(now_datetime(), hours=-24)
	
	overdue_checkins = frappe.get_all("Personnel Check-In",
		filters={
			"docstatus": 1,
			"timestamp_in": ["<", cutoff_time]
		},
		fields=["name", "human", "timestamp_in"]
	)
	
	for checkin in overdue_checkins:
		# Check if checkout exists
		checkout = frappe.db.exists("Personnel Check-Out", {
			"related_check_in": checkin.name,
			"docstatus": 1
		})
		
		if not checkout:
			# Create alert
			frappe.get_doc({
				"doctype": "Lone Worker Alert",
				"human": checkin.human,
				"alert_type": "Missed Check-In",
				"severity": "Medium",
				"resolution_status": "Open"
			}).insert(ignore_permissions=True)
	
	frappe.db.commit()

def check_zone_max_duration():
	"""Check for personnel exceeding zone max duration."""
	presences = frappe.get_all("Zone Presence",
		filters={"status": "Active"},
		fields=["name", "human", "zone", "time_entered"]
	)
	
	for presence in presences:
		zone = frappe.get_doc("Zone Configuration", presence.zone)
		
		if zone.max_duration_minutes and zone.max_duration_minutes > 0:
			duration_seconds = time_diff_in_seconds(now_datetime(), presence.time_entered)
			duration_minutes = duration_seconds / 60
			
			if duration_minutes > zone.max_duration_minutes:
				# Update presence status
				presence_doc = frappe.get_doc("Zone Presence", presence.name)
				presence_doc.status = "Alert"
				presence_doc.alert_triggered = 1
				presence_doc.save(ignore_permissions=True)
	
	frappe.db.commit()

def daily_personnel_cleanup():
	"""Daily cleanup of old location events."""
	# Delete location events older than 90 days
	from frappe.utils import add_to_date
	
	cutoff_date = add_to_date(now_datetime(), days=-90)
	
	frappe.db.sql("""
		DELETE FROM `tabHuman Location Event`
		WHERE timestamp < %s
	""", (cutoff_date,))
	
	frappe.db.commit()

def generate_daily_attendance_summary():
	"""Generate daily attendance summary."""
	# This would generate a summary report
	pass

