"""
Master Test Runner for Sigma ERPNext Integrations
Run all integration tests and generate comprehensive report
"""

import frappe
from frappe.utils import now_datetime
import sys


def run_all_integration_tests():
	"""Run all integration tests and generate report"""
	
	print('\n' + '='*80)
	print('SIGMA ERPNEXT INTEGRATION - COMPREHENSIVE TEST SUITE')
	print('='*80)
	print(f'Started: {now_datetime()}')
	print(f'Site: {frappe.local.site}')
	print('='*80 + '\n')
	
	results = {}
	
	# Test 1: Stock Integration
	print('\n' + '─'*80)
	print('TEST SUITE 1: STOCK INTEGRATION')
	print('─'*80)
	try:
		from sigma.sigma_erpnext_integrations.tests.test_stock_integration import run_tests
		result = run_tests()
		results['Stock Integration'] = {
			'tests_run': result.testsRun,
			'failures': len(result.failures),
			'errors': len(result.errors),
			'success': result.wasSuccessful()
		}
	except Exception as e:
		print(f'❌ Error running Stock Integration tests: {e}')
		results['Stock Integration'] = {'error': str(e)}
	
	# Test 2: Support Integration
	print('\n' + '─'*80)
	print('TEST SUITE 2: SUPPORT INTEGRATION')
	print('─'*80)
	try:
		from sigma.sigma_erpnext_integrations.tests.test_support_integration import run_tests
		result = run_tests()
		results['Support Integration'] = {
			'tests_run': result.testsRun,
			'failures': len(result.failures),
			'errors': len(result.errors),
			'success': result.wasSuccessful()
		}
	except Exception as e:
		print(f'❌ Error running Support Integration tests: {e}')
		results['Support Integration'] = {'error': str(e)}
	
	# Print comprehensive summary
	print('\n' + '='*80)
	print('COMPREHENSIVE TEST REPORT')
	print('='*80)
	
	total_tests = 0
	total_failures = 0
	total_errors = 0
	all_success = True
	
	for suite_name, result in results.items():
		print(f'\n{suite_name}:')
		if 'error' in result:
			print(f'  ❌ Suite Error: {result["error"]}')
			all_success = False
		else:
			tests_run = result['tests_run']
			failures = result['failures']
			errors = result['errors']
			success = result['success']
			
			total_tests += tests_run
			total_failures += failures
			total_errors += errors
			
			status = '✅ PASSED' if success else '❌ FAILED'
			print(f'  Status: {status}')
			print(f'  Tests Run: {tests_run}')
			print(f'  Failures: {failures}')
			print(f'  Errors: {errors}')
			
			if not success:
				all_success = False
	
	print('\n' + '─'*80)
	print('OVERALL SUMMARY:')
	print(f'  Total Tests: {total_tests}')
	print(f'  Total Failures: {total_failures}')
	print(f'  Total Errors: {total_errors}')
	print(f'  Success Rate: {((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0:.1f}%')
	print(f'  Overall Status: {"✅ ALL TESTS PASSED" if all_success else "❌ SOME TESTS FAILED"}')
	print('='*80)
	print(f'Completed: {now_datetime()}')
	print('='*80 + '\n')
	
	return all_success


if __name__ == '__main__':
	success = run_all_integration_tests()
	sys.exit(0 if success else 1)

