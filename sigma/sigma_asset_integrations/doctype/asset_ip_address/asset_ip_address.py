# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import re
import frappe
from frappe.model.document import Document


class AssetIPAddress(Document):
	"""
	Child table for storing multiple IP addresses per asset.
	Supports different IP types: Management, Production, Backup, Other.
	"""

	def validate(self):
		"""Validate IP address format"""
		self.validate_ip_address()

	def validate_ip_address(self):
		"""
		Validate that the IP address is in valid IPv4 or IPv6 format.
		Supports both IPv4 (xxx.xxx.xxx.xxx) and IPv6 formats.
		"""
		if not self.ip_address:
			frappe.throw("IP Address is required")

		# IPv4 validation pattern
		ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
		# IPv6 validation pattern (simplified)
		ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'

		if not (re.match(ipv4_pattern, self.ip_address) or re.match(ipv6_pattern, self.ip_address)):
			frappe.throw(f"Invalid IP address format: {self.ip_address}")

		# Additional IPv4 validation - check octets are 0-255
		if re.match(ipv4_pattern, self.ip_address):
			octets = self.ip_address.split('.')
			for octet in octets:
				if int(octet) > 255:
					frappe.throw(f"Invalid IPv4 address: {self.ip_address} - octets must be 0-255")

