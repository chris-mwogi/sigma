# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import re
import frappe
from frappe.model.document import Document


class AssetMACAddress(Document):
	"""
	Child table for storing multiple MAC addresses per asset.
	Supports different interface types: Ethernet, WiFi, Other.
	"""

	def validate(self):
		"""Validate MAC address format"""
		self.validate_mac_address()

	def validate_mac_address(self):
		"""
		Validate that the MAC address is in valid format: XX:XX:XX:XX:XX:XX
		Supports both colon-separated and hyphen-separated formats.
		"""
		if not self.mac_address:
			frappe.throw("MAC Address is required")

		# MAC address validation pattern - supports both : and - separators
		mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

		if not re.match(mac_pattern, self.mac_address):
			frappe.throw(
				f"Invalid MAC address format: {self.mac_address}. "
				"Expected format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX"
			)

		# Normalize MAC address to colon-separated format
		self.mac_address = self.mac_address.replace('-', ':').upper()

