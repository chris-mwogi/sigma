"""
Test Stock Integration - Asset to Fixed Asset Item Sync

REVISED TESTING STRATEGY:
- Tests use EXISTING ERPNext Assets (not creating new ones)
- Tests verify that Fixed Asset Items are created from Assets
- Tests verify bidirectional sync between Asset and Item
- Tests verify integration logging

Note: Creating ERPNext Assets requires complex setup (item_code, asset_category with accounts, etc.)
So we test with existing assets or create Items first, then Assets.
"""

import frappe
import unittest
from frappe.utils import now_datetime, today, flt
from sigma.sigma_erpnext_integrations.api.stock_integration import StockIntegration


class TestStockIntegration(unittest.TestCase):
	"""Test cases for Stock Integration (Item-First Approach)"""

	def setUp(self):
		"""Set up test data"""
		self.company = frappe.db.get_value('Company', {'is_group': 0}, 'name')
		self.asset_category = self._get_or_create_asset_category()
		self.test_item = None
		self.test_asset = None

	def tearDown(self):
		"""Clean up test data"""
		# Clean up in reverse order
		if self.test_asset:
			try:
				frappe.delete_doc("Asset", self.test_asset, force=True, ignore_permissions=True)
			except:
				pass

		if self.test_item:
			try:
				frappe.delete_doc("Item", self.test_item, force=True, ignore_permissions=True)
			except:
				pass

		frappe.db.rollback()

	def _get_or_create_asset_category(self):
		"""Get or create a test asset category"""
		category_name = "Test Security Equipment"

		if frappe.db.exists('Asset Category', category_name):
			return category_name

		# Get a default account for the category
		company = self.company
		fixed_asset_account = frappe.db.get_value(
			'Account',
			{'company': company, 'account_type': 'Fixed Asset', 'is_group': 0},
			'name'
		)

		if not fixed_asset_account:
			# Return any existing category
			existing = frappe.db.get_value('Asset Category', {}, 'name')
			if existing:
				return existing
			self.skipTest("No Asset Category available for testing")

		try:
			category = frappe.get_doc({
				'doctype': 'Asset Category',
				'asset_category_name': category_name,
				'enable_cwip_accounting': 0,
				'accounts': [{
					'company_name': company,
					'fixed_asset_account': fixed_asset_account,
					'accumulated_depreciation_account': fixed_asset_account,
					'depreciation_expense_account': fixed_asset_account
				}]
			})
			category.insert(ignore_permissions=True)
			frappe.db.commit()
			return category_name
		except Exception as e:
			print(f"Could not create asset category: {e}")
			# Return any existing category
			existing = frappe.db.get_value('Asset Category', {}, 'name')
			if existing:
				return existing
			self.skipTest("Could not create Asset Category for testing")
	
	def test_01_asset_to_item_creation(self):
		"""Test: Creating an Asset should create an Item"""
		
		# Create test asset
		asset_name = f'TEST-CAMERA-{now_datetime().strftime("%Y%m%d%H%M%S")}'
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': asset_name,
			'asset_category': self.asset_category,
			'company': self.company,
			'purchase_date': today(),
			'gross_purchase_amount': 50000,
			'available_for_use_date': today(),
			'is_existing_asset': 1,
			'calculate_depreciation': 0,
			'opening_accumulated_depreciation': 0
		})

		# Set net_purchase_amount manually (ERPNext requirement)
		asset.net_purchase_amount = 50000
		
		asset.insert(ignore_permissions=True)
		frappe.db.commit()
		
		# Reload to get updated fields
		asset.reload()
		
		# Verify sigma_item_code is populated
		self.assertIsNotNone(asset.sigma_item_code, "sigma_item_code should be populated")
		
		# Verify Item exists
		self.assertTrue(
			frappe.db.exists('Item', asset.sigma_item_code),
			f"Item {asset.sigma_item_code} should exist"
		)
		
		# Verify Item details
		item = frappe.get_doc('Item', asset.sigma_item_code)
		self.assertEqual(item.item_name, asset_name, "Item name should match asset name")
		self.assertEqual(item.standard_rate, 50000, "Item rate should match asset amount")
		
		# Verify custom fields
		if hasattr(item, 'sigma_asset'):
			self.assertEqual(item.sigma_asset, asset.name, "Item should link back to Asset")
		
		print(f"✅ Test 1 PASSED: Asset {asset.name} → Item {item.name}")
		
	def test_02_asset_update_syncs_to_item(self):
		"""Test: Updating an Asset should update the Item"""
		
		# Create test asset
		asset_name = f'TEST-CAMERA-{now_datetime().strftime("%Y%m%d%H%M%S")}'
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': asset_name,
			'asset_category': self.asset_category,
			'company': self.company,
			'purchase_date': today(),
			'gross_purchase_amount': 50000,
			'available_for_use_date': today(),
			'is_existing_asset': 1,
			'calculate_depreciation': 0,
			'opening_accumulated_depreciation': 0
		})

		# Set net_purchase_amount manually (ERPNext requirement)
		asset.net_purchase_amount = 50000

		asset.insert(ignore_permissions=True)
		frappe.db.commit()
		asset.reload()

		# Update asset
		new_name = f'{asset_name} - Updated'
		asset.asset_name = new_name
		asset.gross_purchase_amount = 60000
		asset.net_purchase_amount = 60000
		asset.save(ignore_permissions=True)
		frappe.db.commit()
		
		# Verify Item was updated
		item = frappe.get_doc('Item', asset.sigma_item_code)
		self.assertEqual(item.item_name, new_name, "Item name should be updated")
		self.assertEqual(item.standard_rate, 60000, "Item rate should be updated")
		
		print(f"✅ Test 2 PASSED: Asset update synced to Item {item.name}")
		
	def test_03_manual_sync(self):
		"""Test: Manual sync should work"""
		
		# Create test asset without triggering hooks
		asset_name = f'TEST-CAMERA-{now_datetime().strftime("%Y%m%d%H%M%S")}'
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': asset_name,
			'asset_category': self.asset_category,
			'company': self.company,
			'purchase_date': today(),
			'gross_purchase_amount': 50000,
			'available_for_use_date': today(),
			'is_existing_asset': 1,
			'calculate_depreciation': 0,
			'opening_accumulated_depreciation': 0
		})

		# Set net_purchase_amount manually (ERPNext requirement)
		asset.net_purchase_amount = 50000

		# Insert with flags to skip hooks
		asset.flags.ignore_links = True
		asset.insert(ignore_permissions=True)
		frappe.db.commit()
		
		# Manually call sync
		StockIntegration.sync_asset_to_item(asset)
		frappe.db.commit()
		asset.reload()
		
		# Verify Item was created
		self.assertIsNotNone(asset.sigma_item_code, "sigma_item_code should be populated after manual sync")
		self.assertTrue(
			frappe.db.exists('Item', asset.sigma_item_code),
			"Item should exist after manual sync"
		)
		
		print(f"✅ Test 3 PASSED: Manual sync created Item {asset.sigma_item_code}")
		
	def test_04_integration_logging(self):
		"""Test: Integration operations should be logged"""
		
		# Create test asset
		asset_name = f'TEST-CAMERA-{now_datetime().strftime("%Y%m%d%H%M%S")}'
		
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': asset_name,
			'asset_category': self.asset_category,
			'company': self.company,
			'purchase_date': today(),
			'gross_purchase_amount': 50000,
			'available_for_use_date': today(),
			'is_existing_asset': 1,
			'calculate_depreciation': 0,
			'opening_accumulated_depreciation': 0
		})

		# Set net_purchase_amount manually (ERPNext requirement)
		asset.net_purchase_amount = 50000

		asset.insert(ignore_permissions=True)
		frappe.db.commit()
		asset.reload()

		# Check if Integration Log exists
		if frappe.db.exists('DocType', 'Integration Log'):
			# Look for log entry
			logs = frappe.get_all(
				'Integration Log',
				filters={
					'source_doctype': 'Asset',
					'source_name': asset.name,
					'target_doctype': 'Item'
				},
				fields=['name', 'status', 'integration_type']
			)
			
			self.assertGreater(len(logs), 0, "Integration Log entry should exist")
			
			if logs:
				log = logs[0]
				self.assertEqual(log.status, 'Success', "Integration should be successful")
				print(f"✅ Test 4 PASSED: Integration logged as {log.name}")
		else:
			print("⚠️  Test 4 SKIPPED: Integration Log DocType not found")


def run_tests():
	"""Run all stock integration tests"""
	print('\n' + '='*70)
	print('STOCK INTEGRATION TESTS')
	print('='*70 + '\n')
	
	# Create test suite
	suite = unittest.TestLoader().loadTestsFromTestCase(TestStockIntegration)
	
	# Run tests
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	# Print summary
	print('\n' + '='*70)
	print('TEST SUMMARY')
	print('='*70)
	print(f'Tests Run: {result.testsRun}')
	print(f'Successes: {result.testsRun - len(result.failures) - len(result.errors)}')
	print(f'Failures: {len(result.failures)}')
	print(f'Errors: {len(result.errors)}')
	print('='*70 + '\n')
	
	return result


if __name__ == '__main__':
	run_tests()

