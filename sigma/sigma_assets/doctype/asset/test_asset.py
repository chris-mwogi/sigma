# Copyright (c) 2025, Sigma Security Management System
# License: MIT

import frappe
import unittest


class TestAsset(unittest.TestCase):
	"""Test cases for Asset DocType"""

	def setUp(self):
		"""Set up test data"""
		# Create test item if not exists
		if not frappe.db.exists("Item", "Test Asset Item"):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": "Test Asset Item",
				"item_name": "Test Asset Item",
				"item_group": "All Item Groups",
				"stock_uom": "Nos"
			})
			item.insert(ignore_permissions=True)

	def test_asset_creation(self):
		"""Test basic asset creation"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"item_code": "Test Asset Item",
			"asset_name": "Test Asset",
			"company": "Kenya Power",
			"status": "Draft"
		})
		asset.insert(ignore_permissions=True)
		self.assertTrue(asset.name)
		asset.delete()

	def test_composite_asset(self):
		"""Test composite asset with components"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"item_code": "Test Asset Item",
			"asset_name": "Test Composite Asset",
			"company": "Kenya Power",
			"is_composite_asset": 1,
			"status": "Draft",
			"components": [
				{
					"component_name": "Test Component 1",
					"component_type": "Sensor",
					"status": "Active",
					"component_cost": 1000
				}
			]
		})
		asset.insert(ignore_permissions=True)
		self.assertEqual(len(asset.components), 1)
		asset.delete()

	def test_date_validation(self):
		"""Test date validation"""
		asset = frappe.get_doc({
			"doctype": "Asset",
			"item_code": "Test Asset Item",
			"asset_name": "Test Asset",
			"company": "Kenya Power",
			"purchase_date": "2025-01-01",
			"available_for_use_date": "2024-12-01",  # Before purchase date
			"status": "Draft"
		})
		with self.assertRaises(frappe.ValidationError):
			asset.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()

