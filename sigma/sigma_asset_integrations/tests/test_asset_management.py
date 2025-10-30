# Copyright (c) 2025, Sigma Security Management System
# License: MIT

"""
Tests for Asset Management functionality
Tests cover:
- Serial number generation
- IP address validation and queries
- MAC address validation and queries
- GPS coordinate validation
- Asset hierarchy management
- Project linking
"""

import frappe
import unittest
from frappe.test_runner import make_test_records
from frappe.utils import getdate


class TestAssetManagement(unittest.TestCase):
	"""Test Asset Management functionality"""

	def setUp(self):
		"""Set up test fixtures"""
		self.asset_category = frappe.get_doc({
			"doctype": "Asset Category",
			"asset_category_name": "Test Category",
			"asset_category_name_en": "Test Category"
		})
		self.asset_category.insert(ignore_if_duplicate=True)

	def test_auto_serial_number_generation(self):
		"""Test automatic serial number generation on asset creation"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset 1",
			"asset_category": "Test Category",
			"status": "Active"
		})
		asset.insert()
		
		# Check that serial number was generated
		self.assertIsNotNone(asset.serial_number)
		self.assertTrue(asset.serial_number.startswith("ASSET-"))
		
		# Check format: ASSET-YYYY-MM-NNNNN
		parts = asset.serial_number.split('-')
		self.assertEqual(len(parts), 4)
		self.assertEqual(parts[0], "ASSET")
		self.assertEqual(len(parts[1]), 4)  # Year
		self.assertEqual(len(parts[2]), 2)  # Month
		self.assertEqual(len(parts[3]), 5)  # Number

	def test_unique_serial_numbers(self):
		"""Test that each asset gets a unique serial number"""
		asset1 = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset 1",
			"asset_category": "Test Category",
			"status": "Active"
		})
		asset1.insert()
		
		asset2 = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset 2",
			"asset_category": "Test Category",
			"status": "Active"
		})
		asset2.insert()
		
		# Serial numbers should be different
		self.assertNotEqual(asset1.serial_number, asset2.serial_number)

	def test_ip_address_validation(self):
		"""Test IP address validation"""
		from sigma.sigma_asset_integrations.doctype.asset_ip_address.asset_ip_address import AssetIPAddress
		
		# Valid IPv4
		ip = AssetIPAddress({
			"ip_address": "192.168.1.1",
			"ip_type": "Management"
		})
		ip.validate()  # Should not raise
		
		# Invalid IPv4
		ip_invalid = AssetIPAddress({
			"ip_address": "256.256.256.256",
			"ip_type": "Management"
		})
		with self.assertRaises(frappe.ValidationError):
			ip_invalid.validate()

	def test_mac_address_validation(self):
		"""Test MAC address validation and normalization"""
		from sigma.sigma_asset_integrations.doctype.asset_mac_address.asset_mac_address import AssetMACAddress
		
		# Valid MAC with colons
		mac = AssetMACAddress({
			"mac_address": "00:1A:2B:3C:4D:5E",
			"interface_name": "eth0",
			"interface_type": "Ethernet"
		})
		mac.validate()
		self.assertEqual(mac.mac_address, "00:1A:2B:3C:4D:5E")
		
		# Valid MAC with hyphens (should be normalized)
		mac_hyphen = AssetMACAddress({
			"mac_address": "00-1A-2B-3C-4D-5E",
			"interface_name": "eth0",
			"interface_type": "Ethernet"
		})
		mac_hyphen.validate()
		self.assertEqual(mac_hyphen.mac_address, "00:1A:2B:3C:4D:5E")
		
		# Invalid MAC
		mac_invalid = AssetMACAddress({
			"mac_address": "invalid",
			"interface_name": "eth0",
			"interface_type": "Ethernet"
		})
		with self.assertRaises(frappe.ValidationError):
			mac_invalid.validate()

	def test_gps_coordinates_validation(self):
		"""Test GPS coordinates validation"""
		from sigma.sigma_asset_integrations.asset_hooks import validate_gps_coordinates
		
		# Valid coordinates
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset GPS",
			"asset_category": "Test Category",
			"status": "Active",
			"latitude": 40.7128,
			"longitude": -74.0060
		})
		validate_gps_coordinates(asset, None)  # Should not raise
		
		# Invalid latitude
		asset_invalid_lat = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset Invalid",
			"asset_category": "Test Category",
			"status": "Active",
			"latitude": 91.0,
			"longitude": -74.0060
		})
		with self.assertRaises(frappe.ValidationError):
			validate_gps_coordinates(asset_invalid_lat, None)
		
		# Invalid longitude
		asset_invalid_lon = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset Invalid",
			"asset_category": "Test Category",
			"status": "Active",
			"latitude": 40.7128,
			"longitude": 181.0
		})
		with self.assertRaises(frappe.ValidationError):
			validate_gps_coordinates(asset_invalid_lon, None)

	def test_parent_system_validation(self):
		"""Test parent system validation and circular reference detection"""
		from sigma.sigma_asset_integrations.asset_hooks import validate_parent_system
		
		# Asset cannot be its own parent
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset",
			"asset_category": "Test Category",
			"status": "Active",
			"parent_system": "Test Asset"
		})
		with self.assertRaises(frappe.ValidationError):
			validate_parent_system(asset, None)

	def test_asset_component_date_validation(self):
		"""Test asset component date validation"""
		from sigma.sigma_asset_integrations.doctype.asset_component.asset_component import AssetComponent
		
		# date_removed before date_installed should raise error
		component = AssetComponent({
			"component_name": "RAM Module",
			"component_type": "RAM",
			"date_installed": getdate("2025-10-25"),
			"date_removed": getdate("2025-10-20"),
			"status": "Removed"
		})
		with self.assertRaises(frappe.ValidationError):
			component.validate()

	def test_asset_project_link_date_validation(self):
		"""Test asset project link date validation"""
		from sigma.sigma_asset_integrations.doctype.asset_project_link.asset_project_link import AssetProjectLink

		# date_removed before date_assigned should raise error
		project_link = AssetProjectLink({
			"project": "Test Project",
			"date_assigned": getdate("2025-10-25"),
			"date_removed": getdate("2025-10-20")
		})
		with self.assertRaises(frappe.ValidationError):
			project_link.validate()

	def test_iot_device_creation(self):
		"""Test creating asset with is_iot_device=1"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test IoT Device",
			"asset_category": "Test Category",
			"status": "Active",
			"is_iot_device": 1,
			"is_networked_asset": 1,
			"is_tracked_asset": 1,
			"iot_device_id": "TEST-IOT-001",
			"iot_platform": "Traccar",
			"communication_status": "Online"
		})
		asset.insert()

		# Verify IoT fields are set
		self.assertEqual(asset.is_iot_device, 1)
		self.assertEqual(asset.iot_device_id, "TEST-IOT-001")
		self.assertEqual(asset.iot_platform, "Traccar")

	def test_conditional_field_visibility(self):
		"""Test that conditional fields are properly set based on flags"""
		# Asset with is_networked_asset=1 should allow network fields
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Networked Asset",
			"asset_category": "Test Category",
			"status": "Active",
			"is_networked_asset": 1,
			"firmware_version": "v1.0.0",
			"switch_port": "GigabitEthernet0/1"
		})
		asset.insert()

		self.assertEqual(asset.firmware_version, "v1.0.0")
		self.assertEqual(asset.switch_port, "GigabitEthernet0/1")

	def test_asset_event_log_creation(self):
		"""Test creating Asset Event Log entries"""
		# First create an asset
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Asset for Events",
			"asset_category": "Test Category",
			"status": "Active",
			"is_iot_device": 1
		})
		asset.insert()

		# Create Asset Event Log entry
		event_log = frappe.get_doc({
			"doctype": "Asset Event Log",
			"asset": asset.name,
			"event_type": "GPS Update",
			"event_timestamp": frappe.utils.now(),
			"source": "Test",
			"latitude": 40.7128,
			"longitude": -74.0060,
			"event_data": '{"test": "data"}'
		})
		event_log.insert()

		# Verify event log was created
		self.assertIsNotNone(event_log.name)
		self.assertEqual(event_log.asset, asset.name)
		self.assertEqual(event_log.event_type, "GPS Update")

	def test_gps_tracking(self):
		"""Test GPS tracking for tracked assets"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Tracked Asset",
			"asset_category": "Test Category",
			"status": "Active",
			"is_tracked_asset": 1,
			"latitude": 40.7128,
			"longitude": -74.0060,
			"altitude": 10.5
		})
		asset.insert()

		# Verify GPS coordinates are stored
		self.assertEqual(asset.latitude, 40.7128)
		self.assertEqual(asset.longitude, -74.0060)
		self.assertEqual(asset.altitude, 10.5)

	def test_network_information(self):
		"""Test network information for networked assets"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": "Test Network Asset",
			"asset_category": "Test Category",
			"status": "Active",
			"is_networked_asset": 1
		})

		# Add IP address
		asset.append("ip_addresses", {
			"ip_address": "192.168.1.100",
			"ip_type": "Management",
			"is_primary": 1
		})

		# Add MAC address
		asset.append("mac_addresses", {
			"mac_address": "00:1A:2B:3C:4D:5E",
			"interface_name": "eth0",
			"interface_type": "Ethernet"
		})

		asset.insert()

		# Verify network information
		self.assertEqual(len(asset.ip_addresses), 1)
		self.assertEqual(asset.ip_addresses[0].ip_address, "192.168.1.100")
		self.assertEqual(len(asset.mac_addresses), 1)
		self.assertEqual(asset.mac_addresses[0].mac_address, "00:1A:2B:3C:4D:5E")


if __name__ == "__main__":
	unittest.main()

