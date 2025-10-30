"""
Comprehensive tests for Helpdesk Integration

Tests the integration between Sigma Case Management and Frappe Helpdesk
"""

import frappe
import unittest
from frappe.utils import today
from sigma.sigma_erpnext_integrations.api.helpdesk_integration import HelpdeskIntegration


class TestHelpdeskIntegration(unittest.TestCase):
	"""Test Helpdesk Integration functionality"""
	
	def setUp(self):
		"""Set up test data"""
		self.test_cases = []
		self.test_tickets = []
	
	def tearDown(self):
		"""Clean up test data"""
		frappe.set_user("Administrator")
		
		# Delete tickets first
		for ticket_name in self.test_tickets:
			if frappe.db.exists('HD Ticket', ticket_name):
				try:
					frappe.delete_doc('HD Ticket', ticket_name, force=True, ignore_permissions=True)
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
	
	def _create_test_case(self, priority="Medium", status="Open"):
		"""Helper to create a test case"""
		# Check if Case Record doctype exists
		if not frappe.db.exists('DocType', 'Case Record'):
			self.skipTest("Case Record DocType not available")
		
		case = frappe.get_doc({
			'doctype': 'Case Record',
			'title': f'Test Case - {priority}',
			'case_date': today(),
			'priority': priority,
			'case_type': 'Investigation',
			'status': status,
			'description': f'Test case with {priority} priority'
		})
		
		try:
			case.insert(ignore_permissions=True)
			self.test_cases.append(case.name)
			frappe.db.commit()
			return case
		except Exception as e:
			self.skipTest(f"Could not create Case Record: {str(e)}")
	
	def test_01_create_ticket_from_case(self):
		"""
		Test: Create HD Ticket when Case is created
		"""
		print('\n\n=== Test 1: Create HD Ticket from Case ===')
		
		# Create case
		case = self._create_test_case(priority="High")
		
		# Call integration method
		HelpdeskIntegration.sync_case_to_ticket(case)
		frappe.db.commit()
		
		# Verify Ticket was created
		ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
		self.assertIsNotNone(ticket_name, "Ticket reference not set on Case")
		
		ticket = frappe.get_doc('HD Ticket', ticket_name)
		self.test_tickets.append(ticket.name)
		
		# Verify ticket properties
		self.assertEqual(ticket.sigma_case, case.name, "Ticket not linked to Case")
		self.assertEqual(ticket.sigma_case_type, case.case_type, "Case type mismatch")
		self.assertEqual(ticket.priority, case.priority, "Priority mismatch")
		self.assertEqual(ticket.status, 'Open', "Ticket status should be Open")
		self.assertIn(case.name, ticket.subject, "Case name not in ticket subject")
		
		# Verify Integration Log
		logs = frappe.get_all('Integration Log',
			filters={'source_doctype': 'Case Record', 'source_name': case.name},
			fields=['name', 'integration_type', 'status'])
		
		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		self.assertEqual(logs[0].status, 'Success', "Integration status not Success")
		
		print(f'✅ Created Ticket: {ticket.name}')
		print(f'✅ Ticket linked to Case: {case.name}')
		print(f'✅ Ticket subject: {ticket.subject}')
		print(f'✅ Integration logged: {len(logs)} entries')
		print('✅ Test 1 PASSED')
	
	def test_02_update_ticket_when_case_updated(self):
		"""
		Test: Update HD Ticket when Case status is updated
		"""
		print('\n\n=== Test 2: Update Ticket When Case Updated ===')
		
		# Create case and ticket
		case = self._create_test_case(status="Open")
		HelpdeskIntegration.sync_case_to_ticket(case)
		frappe.db.commit()
		
		ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
		self.test_tickets.append(ticket_name)
		
		# Update case status
		case.status = "Resolved"
		case.save(ignore_permissions=True)
		
		# Sync again
		HelpdeskIntegration.sync_case_to_ticket(case)
		frappe.db.commit()
		
		# Verify ticket was updated (not recreated)
		new_ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
		self.assertEqual(ticket_name, new_ticket_name, "Ticket was recreated instead of updated")
		
		# Verify ticket status updated
		ticket = frappe.get_doc('HD Ticket', ticket_name)
		self.assertEqual(ticket.status, 'Resolved', "Ticket status not updated")
		
		print(f'✅ Ticket updated (not recreated): {ticket.name}')
		print(f'✅ Ticket status updated to: {ticket.status}')
		print('✅ Test 2 PASSED')
	
	def test_03_status_mapping(self):
		"""
		Test: Verify Case status to Ticket status mapping
		"""
		print('\n\n=== Test 3: Status Mapping ===')
		
		status_tests = [
			("Open", "Open"),
			("In Progress", "Replied"),
			("Resolved", "Resolved"),
			("Closed", "Closed")
		]
		
		for case_status, expected_ticket_status in status_tests:
			# Create case with specific status
			case = self._create_test_case(status=case_status)
			HelpdeskIntegration.sync_case_to_ticket(case)
			frappe.db.commit()
			
			ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
			self.test_tickets.append(ticket_name)
			
			ticket = frappe.get_doc('HD Ticket', ticket_name)
			
			# Verify status mapping
			self.assertEqual(ticket.status, expected_ticket_status, 
				f"Status mapping failed: {case_status} -> {expected_ticket_status}")
			
			print(f'✅ Status mapping: {case_status} -> {ticket.status}')
		
		print('✅ Test 3 PASSED')
	
	def test_04_multiple_cases_multiple_tickets(self):
		"""
		Test: Create multiple Tickets from multiple Cases
		"""
		print('\n\n=== Test 4: Multiple Cases → Multiple Tickets ===')
		
		# Create multiple cases
		cases = [
			self._create_test_case(priority="High"),
			self._create_test_case(priority="Medium"),
			self._create_test_case(priority="Low")
		]
		
		# Sync all cases
		for case in cases:
			HelpdeskIntegration.sync_case_to_ticket(case)
		frappe.db.commit()
		
		# Verify all tickets created
		for case in cases:
			ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
			self.assertIsNotNone(ticket_name, f"Ticket not created for {case.name}")
			self.test_tickets.append(ticket_name)
			
			ticket = frappe.get_doc('HD Ticket', ticket_name)
			self.assertEqual(ticket.sigma_case, case.name, "Ticket not linked to Case")
			
			print(f'✅ Created Ticket {ticket.name} for Case {case.name}')
		
		print(f'✅ Created {len(cases)} Tickets from {len(cases)} Cases')
		print('✅ Test 4 PASSED')
	
	def test_05_integration_logging(self):
		"""
		Test: Verify all Helpdesk operations are logged
		"""
		print('\n\n=== Test 5: Integration Logging ===')
		
		# Create case and trigger integration
		case = self._create_test_case(priority="High")
		HelpdeskIntegration.sync_case_to_ticket(case)
		frappe.db.commit()
		
		ticket_name = frappe.db.get_value('Case Record', case.name, 'sigma_ticket')
		self.test_tickets.append(ticket_name)
		
		# Check Integration Log
		logs = frappe.get_all('Integration Log',
			filters={
				'source_doctype': 'Case Record',
				'source_name': case.name,
				'integration_type': 'Case to Ticket'
			},
			fields=['name', 'status', 'integration_type', 'target_doctype', 'target_name'])
		
		self.assertTrue(len(logs) > 0, "No Integration Log entries found")
		self.assertEqual(logs[0].status, 'Success', "Integration status not Success")
		self.assertEqual(logs[0].integration_type, 'Case to Ticket', "Integration type mismatch")
		self.assertEqual(logs[0].target_doctype, 'HD Ticket', "Target doctype mismatch")
		self.assertEqual(logs[0].target_name, ticket_name, "Target name mismatch")
		
		print(f'✅ Integration logged: {len(logs)} entries')
		print(f'✅ Log status: {logs[0].status}')
		print(f'✅ Integration type: {logs[0].integration_type}')
		print(f'✅ Target: {logs[0].target_doctype} {logs[0].target_name}')
		print('✅ Test 5 PASSED')


def run_tests():
	"""Run all Helpdesk integration tests"""
	suite = unittest.TestLoader().loadTestsFromTestCase(TestHelpdeskIntegration)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	print(f'\n\n=== HELPDESK INTEGRATION TEST SUMMARY ===')
	print(f'Tests run: {result.testsRun}')
	print(f'Failures: {len(result.failures)}')
	print(f'Errors: {len(result.errors)}')
	print(f'Skipped: {len(result.skipped)}')
	
	if result.wasSuccessful():
		print('✅✅✅ ALL HELPDESK TESTS PASSED! ✅✅✅')
	else:
		print('❌ SOME TESTS FAILED')
	
	return result


if __name__ == '__main__':
	run_tests()

