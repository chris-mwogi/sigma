"""
Comprehensive tests for Projects Integration

Tests the integration between Sigma Case Management and ERPNext Projects
"""

import frappe
import unittest
from frappe.utils import today
from sigma.sigma_erpnext_integrations.api.projects_integration import ProjectsIntegration


class TestProjectsIntegration(unittest.TestCase):
	"""Test Projects Integration functionality"""
	
	def setUp(self):
		"""Set up test data"""
		self.test_cases = []
		self.test_projects = []
		self.company = frappe.db.get_value('Company', {'is_group': 0}, 'name')
	
	def tearDown(self):
		"""Clean up test data"""
		frappe.set_user("Administrator")
		
		# Delete projects first
		for project_name in self.test_projects:
			if frappe.db.exists('Project', project_name):
				try:
					frappe.delete_doc('Project', project_name, force=True, ignore_permissions=True)
				except:
					pass
		
		# Delete cases
		for case_name in self.test_cases:
			if frappe.db.exists('Case Record', case_name):
				try:
					frappe.delete_doc('Case Record', case_name, force=True, ignore_permissions=True)
				except:
					pass
		
		frappe.db.commit()
	
	def _create_test_case(self, priority="High", case_type="Legal"):
		"""Helper to create a test case"""
		# Check if Case Record doctype exists
		if not frappe.db.exists('DocType', 'Case Record'):
			self.skipTest("Case Record DocType not available")
		
		case = frappe.get_doc({
			'doctype': 'Case Record',
			'title': f'Test Case - {priority}',
			'case_date': today(),
			'priority': priority,
			'case_type': case_type,
			'status': 'Open',
			'description': f'Test case with {priority} priority'
		})
		
		try:
			case.insert(ignore_permissions=True)
			self.test_cases.append(case.name)
			frappe.db.commit()
			return case
		except Exception as e:
			self.skipTest(f"Could not create Case Record: {str(e)}")
	
	def test_01_create_project_from_high_priority_case(self):
		"""
		Test: Create Project when High priority Case is created
		"""
		print('\n\n=== Test 1: Create Project from High Priority Case ===')
		
		# Create high priority case
		case = self._create_test_case(priority="High")
		
		# Call integration method
		ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		# Verify Project was created
		project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
		self.assertIsNotNone(project_name, "Project reference not set on Case")
		
		project = frappe.get_doc('Project', project_name)
		self.test_projects.append(project.name)
		
		# Verify project properties
		self.assertEqual(project.sigma_case, case.name, "Project not linked to Case")
		self.assertEqual(project.sigma_case_type, case.case_type, "Case type mismatch")
		self.assertEqual(project.status, 'Open', "Project status should be Open")
		self.assertIn(case.name, project.project_name, "Case name not in project name")
		
		# Verify Integration Log
		logs = frappe.get_all('Integration Log',
			filters={'source_doctype': 'Case Record', 'source_name': case.name},
			fields=['name', 'integration_type', 'status'])
		
		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		self.assertEqual(logs[0].status, 'Success', "Integration status not Success")
		
		print(f'✅ Created Project: {project.name}')
		print(f'✅ Project linked to Case: {case.name}')
		print(f'✅ Project name: {project.project_name}')
		print(f'✅ Integration logged: {len(logs)} entries')
		print('✅ Test 1 PASSED')
	
	def test_02_create_project_from_critical_priority_case(self):
		"""
		Test: Create Project when Critical priority Case is created
		"""
		print('\n\n=== Test 2: Create Project from Critical Priority Case ===')
		
		# Create critical priority case
		case = self._create_test_case(priority="Critical")
		
		# Call integration method
		ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		# Verify Project was created
		project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
		self.assertIsNotNone(project_name, "Project reference not set on Case")
		
		project = frappe.get_doc('Project', project_name)
		self.test_projects.append(project.name)
		
		# Verify project properties
		self.assertEqual(project.sigma_case, case.name, "Project not linked to Case")
		
		print(f'✅ Created Project: {project.name}')
		print(f'✅ Project linked to Critical Case: {case.name}')
		print('✅ Test 2 PASSED')
	
	def test_03_no_project_for_low_priority_case(self):
		"""
		Test: No Project created for Low priority Case
		"""
		print('\n\n=== Test 3: No Project for Low Priority Case ===')
		
		# Create low priority case
		case = self._create_test_case(priority="Low")
		
		# Call integration method
		ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		# Verify NO Project was created
		project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
		self.assertIsNone(project_name, "Project should not be created for Low priority")
		
		print(f'✅ No project created for Low priority case')
		print('✅ Test 3 PASSED')
	
	def test_04_no_project_for_medium_priority_case(self):
		"""
		Test: No Project created for Medium priority Case
		"""
		print('\n\n=== Test 4: No Project for Medium Priority Case ===')
		
		# Create medium priority case
		case = self._create_test_case(priority="Medium")
		
		# Call integration method
		ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		# Verify NO Project was created
		project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
		self.assertIsNone(project_name, "Project should not be created for Medium priority")
		
		print(f'✅ No project created for Medium priority case')
		print('✅ Test 4 PASSED')
	
	def test_05_multiple_high_priority_cases(self):
		"""
		Test: Create multiple Projects from multiple High priority Cases
		"""
		print('\n\n=== Test 5: Multiple High Priority Cases → Multiple Projects ===')
		
		# Create multiple high priority cases
		cases = [
			self._create_test_case(priority="High", case_type="Legal"),
			self._create_test_case(priority="Critical", case_type="Compliance"),
			self._create_test_case(priority="High", case_type="Investigation")
		]
		
		# Sync all cases
		for case in cases:
			ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		# Verify all projects created
		for case in cases:
			project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
			self.assertIsNotNone(project_name, f"Project not created for {case.name}")
			self.test_projects.append(project_name)
			
			project = frappe.get_doc('Project', project_name)
			self.assertEqual(project.sigma_case, case.name, "Project not linked to Case")
			
			print(f'✅ Created Project {project.name} for Case {case.name}')
		
		print(f'✅ Created {len(cases)} Projects from {len(cases)} Cases')
		print('✅ Test 5 PASSED')
	
	def test_06_integration_logging(self):
		"""
		Test: Verify all Projects operations are logged
		"""
		print('\n\n=== Test 6: Integration Logging ===')
		
		# Create case and trigger integration
		case = self._create_test_case(priority="High")
		ProjectsIntegration.sync_case_to_project(case)
		frappe.db.commit()
		
		project_name = frappe.db.get_value('Case Record', case.name, 'sigma_project')
		self.test_projects.append(project_name)
		
		# Check Integration Log
		logs = frappe.get_all('Integration Log',
			filters={
				'source_doctype': 'Case Record',
				'source_name': case.name,
				'integration_type': 'Case to Project'
			},
			fields=['name', 'status', 'integration_type', 'target_doctype', 'target_name'])
		
		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		self.assertEqual(logs[0].status, 'Success', "Integration status not Success")
		self.assertEqual(logs[0].integration_type, 'Case to Project', "Integration type mismatch")
		self.assertEqual(logs[0].target_doctype, 'Project', "Target doctype mismatch")
		self.assertEqual(logs[0].target_name, project_name, "Target name mismatch")
		
		print(f'✅ Integration logged: {len(logs)} entries')
		print(f'✅ Log status: {logs[0].status}')
		print(f'✅ Integration type: {logs[0].integration_type}')
		print(f'✅ Target: {logs[0].target_doctype} {logs[0].target_name}')
		print('✅ Test 6 PASSED')


def run_tests():
	"""Run all Projects integration tests"""
	suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectsIntegration)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	print(f'\n\n=== PROJECTS INTEGRATION TEST SUMMARY ===')
	print(f'Tests run: {result.testsRun}')
	print(f'Failures: {len(result.failures)}')
	print(f'Errors: {len(result.errors)}')
	print(f'Skipped: {len(result.skipped)}')
	
	if result.wasSuccessful():
		print('✅✅✅ ALL PROJECTS TESTS PASSED! ✅✅✅')
	else:
		print('❌ SOME TESTS FAILED')
	
	return result


if __name__ == '__main__':
	run_tests()

