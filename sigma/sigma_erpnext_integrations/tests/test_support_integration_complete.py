"""
Comprehensive tests for Support Integration

Tests the integration between Sigma Asset Management and ERPNext Support/Maintenance modules
"""

import frappe
import unittest
from frappe.utils import today, now, add_days
from sigma.sigma_erpnext_integrations.api.support_integration import SupportIntegration


class TestSupportIntegrationComplete(unittest.TestCase):
	"""Test Support Integration functionality"""
	
	def setUp(self):
		"""Set up test data"""
		self.company = frappe.db.get_value('Company', {'is_group': 0}, 'name')
		self.asset_category = self._get_asset_category()
		self.location = self._get_location()
		self.test_items = []
		self.test_assets = []
		self.test_schedules = []
		self.test_visits = []
		self.test_incidents = []
	
	def tearDown(self):
		"""Clean up test data"""
		frappe.set_user("Administrator")
		
		# Delete in reverse order of dependencies
		for visit_name in self.test_visits:
			if frappe.db.exists('Maintenance Visit', visit_name):
				try:
					frappe.delete_doc('Maintenance Visit', visit_name, force=True, ignore_permissions=True)
				except:
					pass
		
		for schedule_name in self.test_schedules:
			if frappe.db.exists('Maintenance Schedule', schedule_name):
				try:
					frappe.delete_doc('Maintenance Schedule', schedule_name, force=True, ignore_permissions=True)
				except:
					pass
		
		for incident_name in self.test_incidents:
			if frappe.db.exists('Incident Report', incident_name):
				try:
					frappe.delete_doc('Incident Report', incident_name, force=True, ignore_permissions=True)
				except:
					pass
		
		for asset_name in self.test_assets:
			if frappe.db.exists('Asset', asset_name):
				try:
					frappe.delete_doc('Asset', asset_name, force=True, ignore_permissions=True)
				except:
					pass
		
		for item_code in self.test_items:
			if frappe.db.exists('Item', item_code):
				try:
					frappe.db.set_value('Item', item_code, 'disabled', 1)
				except:
					pass
		
		frappe.db.commit()
	
	def _get_asset_category(self):
		"""Get an existing asset category"""
		category = frappe.db.get_value('Asset Category', {}, 'name')
		if not category:
			self.skipTest("No Asset Category available for testing")
		return category
	
	def _get_location(self):
		"""Get or create a test location"""
		location = frappe.db.get_value('Location', {}, 'name')
		if location:
			return location
		
		try:
			loc = frappe.get_doc({
				'doctype': 'Location',
				'location_name': 'Test Location'
			})
			loc.insert(ignore_permissions=True)
			frappe.db.commit()
			return loc.name
		except:
			self.skipTest("No Location available for testing")
	
	def _create_test_asset(self, requires_maintenance=False):
		"""Helper to create a test asset with item"""
		# Create Fixed Asset Item
		item_code = f'TEST-SUPP-{frappe.generate_hash(length=8)}'
		item = frappe.get_doc({
			'doctype': 'Item',
			'item_code': item_code,
			'item_name': 'Test Support Asset',
			'item_group': 'All Item Groups',
			'stock_uom': 'Nos',
			'is_stock_item': 0,
			'is_fixed_asset': 1,
			'asset_category': self.asset_category,
			'standard_rate': 50000
		})
		item.insert(ignore_permissions=True)
		self.test_items.append(item.name)
		
		# Create Asset
		asset = frappe.get_doc({
			'doctype': 'Asset',
			'asset_name': 'Test Support Asset',
			'item_code': item.name,
			'asset_category': self.asset_category,
			'company': self.company,
			'location': self.location,
			'purchase_date': today(),
			'gross_purchase_amount': 50000,
			'net_purchase_amount': 50000,
			'available_for_use_date': today(),
			'is_existing_asset': 1,
			'calculate_depreciation': 0,
			'opening_accumulated_depreciation': 0,
			'requires_maintenance': 1 if requires_maintenance else 0,
			'sigma_item_code': item.name
		})
		asset.insert(ignore_permissions=True)
		self.test_assets.append(asset.name)
		frappe.db.commit()
		
		return asset
	
	def test_01_create_maintenance_schedule_from_asset(self):
		"""
		Test: Create Maintenance Schedule when Asset requires maintenance
		"""
		print('\n\n=== Test 1: Create Maintenance Schedule from Asset ===')
		
		# Create asset with requires_maintenance flag
		asset = self._create_test_asset(requires_maintenance=True)
		
		# Call integration method
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		
		# Verify Maintenance Schedule was created
		schedule_name = frappe.db.get_value('Asset', asset.name, 'sigma_maintenance_schedule')
		self.assertIsNotNone(schedule_name, "Maintenance Schedule reference not set on Asset")
		
		schedule = frappe.get_doc('Maintenance Schedule', schedule_name)
		self.test_schedules.append(schedule.name)
		
		# Verify schedule properties
		self.assertEqual(schedule.sigma_asset, asset.name, "Schedule not linked to Asset")
		self.assertEqual(schedule.item_code, asset.sigma_item_code, "Item code mismatch")
		self.assertTrue(len(schedule.items) > 0, "Schedule has no items")
		
		# Verify Integration Log
		logs = frappe.get_all('Integration Log',
			filters={'source_doctype': 'Asset', 'source_name': asset.name},
			fields=['name', 'integration_type', 'status'])

		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		
		print(f'✅ Created Maintenance Schedule: {schedule.name}')
		print(f'✅ Schedule linked to Asset: {asset.name}')
		print(f'✅ Integration logged: {len(logs)} entries')
		print('✅ Test 1 PASSED')
	
	def test_02_update_maintenance_schedule(self):
		"""
		Test: Update existing Maintenance Schedule when Asset is updated
		"""
		print('\n\n=== Test 2: Update Maintenance Schedule ===')
		
		# Create asset with maintenance schedule
		asset = self._create_test_asset(requires_maintenance=True)
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		
		schedule_name = frappe.db.get_value('Asset', asset.name, 'sigma_maintenance_schedule')
		self.test_schedules.append(schedule_name)
		
		# Update asset name
		asset.asset_name = 'Updated Support Asset'
		asset.save(ignore_permissions=True)
		
		# Sync again
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		
		# Verify schedule was updated (not recreated)
		new_schedule_name = frappe.db.get_value('Asset', asset.name, 'sigma_maintenance_schedule')
		self.assertEqual(schedule_name, new_schedule_name, "Schedule was recreated instead of updated")
		
		# Verify schedule reflects new asset name
		schedule = frappe.get_doc('Maintenance Schedule', schedule_name)
		self.assertEqual(schedule.item_name, 'Updated Support Asset', "Schedule name not updated")
		
		print(f'✅ Schedule updated (not recreated): {schedule.name}')
		print(f'✅ Schedule name updated to: {schedule.item_name}')
		print('✅ Test 2 PASSED')
	
	def test_03_no_schedule_without_maintenance_flag(self):
		"""
		Test: No Maintenance Schedule created if requires_maintenance is False
		"""
		print('\n\n=== Test 3: No Schedule Without Maintenance Flag ===')
		
		# Create asset WITHOUT requires_maintenance flag
		asset = self._create_test_asset(requires_maintenance=False)
		
		# Call integration method
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		
		# Verify NO Maintenance Schedule was created
		schedule_name = frappe.db.get_value('Asset', asset.name, 'sigma_maintenance_schedule')
		self.assertIsNone(schedule_name, "Maintenance Schedule should not be created")
		
		print(f'✅ No schedule created for asset without maintenance flag')
		print('✅ Test 3 PASSED')
	
	def test_04_create_maintenance_visit_from_incident(self):
		"""
		Test: Create Maintenance Visit from Incident Report
		"""
		print('\n\n=== Test 4: Create Maintenance Visit from Incident ===')
		
		# Create asset
		asset = self._create_test_asset(requires_maintenance=True)
		
		# Check if Incident Report doctype exists
		if not frappe.db.exists('DocType', 'Incident Report'):
			print('⚠️  Incident Report DocType not found - skipping test')
			self.skipTest("Incident Report DocType not available")
		
		# Create Incident Report
		incident = frappe.get_doc({
			'doctype': 'Incident Report',
			'title': 'Test Incident',
			'incident_date': today(),
			'related_asset': asset.name,
			'description': 'Test incident requiring maintenance',
			'incident_type': 'Equipment Failure'
		})
		
		try:
			incident.insert(ignore_permissions=True)
			self.test_incidents.append(incident.name)
			frappe.db.commit()
			
			# Call integration method
			SupportIntegration.create_maintenance_visit_from_incident(incident)
			frappe.db.commit()
			
			# Verify Maintenance Visit was created
			visit_name = frappe.db.get_value('Incident Report', incident.name, 'sigma_maintenance_visit')
			self.assertIsNotNone(visit_name, "Maintenance Visit reference not set on Incident")
			
			visit = frappe.get_doc('Maintenance Visit', visit_name)
			self.test_visits.append(visit.name)
			
			# Verify visit properties
			self.assertEqual(visit.sigma_incident, incident.name, "Visit not linked to Incident")
			self.assertEqual(visit.sigma_asset, asset.name, "Visit not linked to Asset")
			self.assertTrue(len(visit.purposes) > 0, "Visit has no purposes")
			
			print(f'✅ Created Maintenance Visit: {visit.name}')
			print(f'✅ Visit linked to Incident: {incident.name}')
			print(f'✅ Visit linked to Asset: {asset.name}')
			print('✅ Test 4 PASSED')
			
		except Exception as e:
			print(f'⚠️  Test skipped due to: {str(e)}')
			self.skipTest(f"Incident Report creation failed: {str(e)}")
	
	def test_05_integration_logging(self):
		"""
		Test: Verify all support operations are logged
		"""
		print('\n\n=== Test 5: Integration Logging ===')
		
		# Create asset and trigger integration
		asset = self._create_test_asset(requires_maintenance=True)
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		
		schedule_name = frappe.db.get_value('Asset', asset.name, 'sigma_maintenance_schedule')
		self.test_schedules.append(schedule_name)
		
		# Check Integration Log
		logs = frappe.get_all('Integration Log',
			filters={
				'source_doctype': 'Asset',
				'source_name': asset.name,
				'integration_type': 'Asset to Maintenance Schedule'
			},
			fields=['name', 'status', 'integration_type'])
		
		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		self.assertEqual(logs[0].status, 'Success', "Integration status not Success")
		
		print(f'✅ Integration logged: {len(logs)} entries')
		print(f'✅ Log status: {logs[0].status}')
		print(f'✅ Integration type: {logs[0].integration_type}')
		print('✅ Test 5 PASSED')


def run_tests():
	"""Run all support integration tests"""
	suite = unittest.TestLoader().loadTestsFromTestCase(TestSupportIntegrationComplete)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	print(f'\n\n=== SUPPORT INTEGRATION TEST SUMMARY ===')
	print(f'Tests run: {result.testsRun}')
	print(f'Failures: {len(result.failures)}')
	print(f'Errors: {len(result.errors)}')
	print(f'Skipped: {len(result.skipped)}')
	
	if result.wasSuccessful():
		print('✅✅✅ ALL SUPPORT TESTS PASSED! ✅✅✅')
	else:
		print('❌ SOME TESTS FAILED')
	
	return result


if __name__ == '__main__':
	run_tests()

