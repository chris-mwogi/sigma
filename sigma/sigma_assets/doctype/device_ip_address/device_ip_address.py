# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DeviceIPAddress(Document):
	"""Child table for storing multiple IP addresses per monitored device."""
	
	def validate(self):
		"""Validate IP address format and ensure only one primary IP."""
		# Basic IP validation
		if self.ip_address:
			self.validate_ip_format()
		
		# Ensure only one primary IP per device
		if self.is_primary and self.parenttype == "Monitored Device":
			self.validate_single_primary()
	
	def validate_ip_format(self):
		"""Basic IP address format validation."""
		import re
		# Simple IPv4 pattern
		ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
		# Simple IPv6 pattern (basic)
		ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
		
		if not (re.match(ipv4_pattern, self.ip_address) or re.match(ipv6_pattern, self.ip_address)):
			frappe.msgprint(
				f"IP Address '{self.ip_address}' may not be in valid format",
				indicator="orange",
				alert=True
			)
	
	def validate_single_primary(self):
		"""Ensure only one IP is marked as primary."""
		if not self.parent:
			return
		
		# Check if another IP is already marked as primary
		existing_primary = frappe.db.sql("""
			SELECT name, ip_address
			FROM `tabDevice IP Address`
			WHERE parent = %s
			AND parenttype = 'Monitored Device'
			AND is_primary = 1
			AND name != %s
		""", (self.parent, self.name or ""), as_dict=True)
		
		if existing_primary:
			frappe.throw(
				f"IP Address '{existing_primary[0].ip_address}' is already marked as primary. "
				f"Please unmark it first before setting another IP as primary."
			)

