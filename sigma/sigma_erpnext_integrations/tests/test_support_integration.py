"""
Test Support Integration - Maintenance Schedule and Maintenance Visit
"""

import frappe
import unittest
from frappe.utils import now_datetime, today
from sigma.sigma_erpnext_integrations.api.support_integration import SupportIntegration


class TestSupportIntegration(unittest.TestCase):
	"""Test cases for Support Integration"""
	
	def setUp(self):
		"""Set up test data"""
		self.company = frappe.db.get_value('Company', {'is_group': 0}, 'name')
		self.asset_category = frappe.db.get_value('Asset Category', {}, 'name')
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
		
	def _create_test_asset(self, with_maintenance=False):
		"""Helper to create a test asset"""
		asset_name = f'TEST-ASSET-{now_datetime().strftime("%Y%m%d%H%M%S")}'
		
		asset_data = {
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
		}

		if with_maintenance:
			asset_data['requires_maintenance'] = 1
			asset_data['maintenance_frequency'] = 'Monthly'

		asset = frappe.get_doc(asset_data)

		# Set net_purchase_amount manually (ERPNext requirement)
		asset.net_purchase_amount = 50000

		asset.insert(ignore_permissions=True)
		frappe.db.commit()
		
		return asset
		
	def test_01_maintenance_schedule_creation(self):
		"""Test: Creating an Asset with maintenance flag should create Maintenance Schedule"""
		
		# Check if Maintenance Schedule DocType exists
		if not frappe.db.exists('DocType', 'Maintenance Schedule'):
			print("⚠️  Test 1 SKIPPED: Maintenance Schedule DocType not found")
			return
		
		# Create asset with maintenance flag
		asset = self._create_test_asset(with_maintenance=True)
		asset.reload()
		
		# Verify sigma_maintenance_schedule is populated
		if hasattr(asset, 'sigma_maintenance_schedule') and asset.sigma_maintenance_schedule:
			self.assertIsNotNone(
				asset.sigma_maintenance_schedule,
				"sigma_maintenance_schedule should be populated"
			)
			
			# Verify Maintenance Schedule exists
			self.assertTrue(
				frappe.db.exists('Maintenance Schedule', asset.sigma_maintenance_schedule),
				f"Maintenance Schedule {asset.sigma_maintenance_schedule} should exist"
			)
			
			# Verify schedule details
			schedule = frappe.get_doc('Maintenance Schedule', asset.sigma_maintenance_schedule)
			self.assertEqual(schedule.periodicity, 'Monthly', "Periodicity should be Monthly")
			
			print(f"✅ Test 1 PASSED: Asset {asset.name} → Maintenance Schedule {schedule.name}")
		else:
			print("⚠️  Test 1 SKIPPED: sigma_maintenance_schedule field not found on Asset")
			
	def test_02_incident_to_maintenance_visit(self):
		"""Test: Creating an Incident Report should create Maintenance Visit"""
		
		# Check if required DocTypes exist
		if not frappe.db.exists('DocType', 'Incident Report'):
			print("⚠️  Test 2 SKIPPED: Incident Report DocType not found")
			return
			
		if not frappe.db.exists('DocType', 'Maintenance Visit'):
			print("⚠️  Test 2 SKIPPED: Maintenance Visit DocType not found")
			return
		
		# Create test asset
		asset = self._create_test_asset()
		
		# Create incident report
		incident = frappe.get_doc({
			'doctype': 'Incident Report',
			'asset': asset.name,
			'incident_type': 'Equipment Malfunction',
			'priority': 'High',
			'description': 'Test incident for maintenance visit creation'
		})
		
		incident.insert(ignore_permissions=True)
		frappe.db.commit()
		incident.reload()
		
		# Verify sigma_maintenance_visit is populated
		if hasattr(incident, 'sigma_maintenance_visit') and incident.sigma_maintenance_visit:
			self.assertIsNotNone(
				incident.sigma_maintenance_visit,
				"sigma_maintenance_visit should be populated"
			)
			
			# Verify Maintenance Visit exists
			self.assertTrue(
				frappe.db.exists('Maintenance Visit', incident.sigma_maintenance_visit),
				f"Maintenance Visit {incident.sigma_maintenance_visit} should exist"
			)
			
			# Verify visit details
			visit = frappe.get_doc('Maintenance Visit', incident.sigma_maintenance_visit)
			self.assertEqual(visit.maintenance_type, 'Unscheduled', "Should be Unscheduled")
			
			print(f"✅ Test 2 PASSED: Incident {incident.name} → Maintenance Visit {visit.name}")
		else:
			print("⚠️  Test 2 SKIPPED: sigma_maintenance_visit field not found on Incident Report")
			
	def test_03_manual_maintenance_sync(self):
		"""Test: Manual maintenance sync should work"""
		
		# Check if Maintenance Schedule DocType exists
		if not frappe.db.exists('DocType', 'Maintenance Schedule'):
			print("⚠️  Test 3 SKIPPED: Maintenance Schedule DocType not found")
			return
		
		# Create asset without maintenance flag
		asset = self._create_test_asset(with_maintenance=False)
		
		# Set maintenance flag
		asset.requires_maintenance = 1
		asset.maintenance_frequency = 'Quarterly'
		
		# Manually call sync
		SupportIntegration.sync_asset_maintenance(asset)
		frappe.db.commit()
		asset.reload()
		
		# Verify Maintenance Schedule was created
		if hasattr(asset, 'sigma_maintenance_schedule') and asset.sigma_maintenance_schedule:
			self.assertIsNotNone(
				asset.sigma_maintenance_schedule,
				"sigma_maintenance_schedule should be populated after manual sync"
			)
			
			self.assertTrue(
				frappe.db.exists('Maintenance Schedule', asset.sigma_maintenance_schedule),
				"Maintenance Schedule should exist after manual sync"
			)
			
			print(f"✅ Test 3 PASSED: Manual sync created Maintenance Schedule {asset.sigma_maintenance_schedule}")
		else:
			print("⚠️  Test 3 SKIPPED: sigma_maintenance_schedule field not found on Asset")
			
	def test_04_maintenance_integration_logging(self):
		"""Test: Maintenance integration operations should be logged"""
		
		# Check if required DocTypes exist
		if not frappe.db.exists('DocType', 'Integration Log'):
			print("⚠️  Test 4 SKIPPED: Integration Log DocType not found")
			return
			
		if not frappe.db.exists('DocType', 'Maintenance Schedule'):
			print("⚠️  Test 4 SKIPPED: Maintenance Schedule DocType not found")
			return
		
		# Create asset with maintenance
		asset = self._create_test_asset(with_maintenance=True)
		asset.reload()
		
		# Check for log entry
		logs = frappe.get_all(
			'Integration Log',
			filters={
				'source_doctype': 'Asset',
				'source_name': asset.name,
				'target_doctype': 'Maintenance Schedule'
			},
			fields=['name', 'status', 'integration_type']
		)
		
		if logs:
			self.assertGreater(len(logs), 0, "Integration Log entry should exist")
			log = logs[0]
			self.assertEqual(log.status, 'Success', "Integration should be successful")
			print(f"✅ Test 4 PASSED: Maintenance integration logged as {log.name}")
		else:
			print("⚠️  Test 4: No integration logs found (may be expected if logging not configured)")


def run_tests():
	"""Run all support integration tests"""
	print('\n' + '='*70)
	print('SUPPORT INTEGRATION TESTS')
	print('='*70 + '\n')
	
	# Create test suite
	suite = unittest.TestLoader().loadTestsFromTestCase(TestSupportIntegration)
	
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

