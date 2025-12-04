# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class KeyRiskIndicator(Document):
	def validate(self):
		"""Validate Key Risk Indicator"""
		self.validate_kri_owner()
		self.validate_thresholds()
		self.update_readings_status()
		self.update_current_status()
		self.calculate_trend()
	
	def validate_kri_owner(self):
		"""Validate that KRI owner is a valid user"""
		if self.kri_owner:
			if not frappe.db.exists("User", self.kri_owner):
				frappe.throw(f"KRI Owner '{self.kri_owner}' is not a valid user")
	
	def validate_thresholds(self):
		"""Validate threshold logic"""
		if self.threshold_direction == "Lower is Better":
			# For lower is better: green < yellow < red
			if not (self.threshold_green < self.threshold_yellow < self.threshold_red):
				frappe.throw("For 'Lower is Better', thresholds must be: Green < Yellow < Red")
		else:
			# For higher is better: green > yellow > red
			if not (self.threshold_green > self.threshold_yellow > self.threshold_red):
				frappe.throw("For 'Higher is Better', thresholds must be: Green > Yellow > Red")
	
	def update_readings_status(self):
		"""Update status for each reading based on thresholds"""
		for reading in self.kri_readings:
			reading.status = self.get_status_for_value(reading.actual_value)
	
	def get_status_for_value(self, value):
		"""Determine status based on value and thresholds"""
		value = flt(value)
		
		if self.threshold_direction == "Lower is Better":
			if value <= self.threshold_green:
				return "Normal"
			elif value <= self.threshold_yellow:
				return "Warning"
			else:
				return "Critical"
		else:  # Higher is Better
			if value >= self.threshold_green:
				return "Normal"
			elif value >= self.threshold_yellow:
				return "Warning"
			else:
				return "Critical"
	
	def update_current_status(self):
		"""Update current status based on latest reading"""
		if self.kri_readings:
			# Sort readings by date (most recent first)
			sorted_readings = sorted(self.kri_readings, key=lambda x: x.reading_date, reverse=True)
			latest_reading = sorted_readings[0]
			
			self.last_reading_date = latest_reading.reading_date
			self.last_reading_value = latest_reading.actual_value
			self.current_value = latest_reading.actual_value
			self.current_status = latest_reading.status
		else:
			self.last_reading_date = None
			self.last_reading_value = None
			self.current_value = None
			self.current_status = None
	
	def calculate_trend(self):
		"""Calculate trend based on recent readings"""
		if len(self.kri_readings) < 2:
			self.trend = "Stable"
			return
		
		# Sort readings by date
		sorted_readings = sorted(self.kri_readings, key=lambda x: x.reading_date)
		
		# Get last 3 readings or all if less than 3
		recent_readings = sorted_readings[-3:]
		
		# Calculate average change
		total_change = 0
		for i in range(1, len(recent_readings)):
			change = recent_readings[i].actual_value - recent_readings[i-1].actual_value
			total_change += change
		
		avg_change = total_change / (len(recent_readings) - 1)
		
		# Determine trend based on direction and change
		if self.threshold_direction == "Lower is Better":
			if avg_change < -0.05:  # Decreasing is improving
				self.trend = "Improving"
			elif avg_change > 0.05:  # Increasing is deteriorating
				self.trend = "Deteriorating"
			else:
				self.trend = "Stable"
		else:  # Higher is Better
			if avg_change > 0.05:  # Increasing is improving
				self.trend = "Improving"
			elif avg_change < -0.05:  # Decreasing is deteriorating
				self.trend = "Deteriorating"
			else:
				self.trend = "Stable"
	
	def on_update(self):
		"""Create alerts if status is critical"""
		if self.current_status == "Critical":
			self.create_critical_alert()
	
	def create_critical_alert(self):
		"""Create alert when KRI reaches critical threshold"""
		# Check if alert already exists for this reading
		existing_alert = frappe.db.exists("Notification Log", {
			"document_type": "Key Risk Indicator",
			"document_name": self.name,
			"subject": f"Critical KRI Alert: {self.kri_name}",
			"creation": [">=", self.last_reading_date]
		})
		
		if not existing_alert:
			notification = frappe.new_doc("Notification Log")
			notification.subject = f"Critical KRI Alert: {self.kri_name}"
			notification.for_user = self.kri_owner
			notification.type = "Alert"
			notification.document_type = "Key Risk Indicator"
			notification.document_name = self.name
			notification.email_content = f"""
				<p><strong>Critical KRI Alert</strong></p>
				<p><strong>KRI:</strong> {self.kri_name}</p>
				<p><strong>Current Value:</strong> {self.current_value} {self.unit_of_measurement}</p>
				<p><strong>Critical Threshold:</strong> {self.threshold_red} {self.unit_of_measurement}</p>
				<p><strong>Date:</strong> {self.last_reading_date}</p>
				<p><strong>Trend:</strong> {self.trend}</p>
				<p>Immediate action may be required.</p>
			"""
			notification.insert(ignore_permissions=True)


@frappe.whitelist()
def get_kri_summary(kri_name):
	"""Get summary of KRI"""
	kri = frappe.get_doc("Key Risk Indicator", kri_name)
	
	# Count readings by status
	normal_count = sum(1 for r in kri.kri_readings if r.status == "Normal")
	warning_count = sum(1 for r in kri.kri_readings if r.status == "Warning")
	critical_count = sum(1 for r in kri.kri_readings if r.status == "Critical")
	
	return {
		"kri_name": kri.kri_name,
		"current_status": kri.current_status,
		"current_value": kri.current_value,
		"target_value": kri.target_value,
		"unit_of_measurement": kri.unit_of_measurement,
		"trend": kri.trend,
		"total_readings": len(kri.kri_readings),
		"normal_count": normal_count,
		"warning_count": warning_count,
		"critical_count": critical_count,
		"last_reading_date": kri.last_reading_date
	}

