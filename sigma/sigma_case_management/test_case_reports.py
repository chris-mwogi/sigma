#!/usr/bin/env python3
"""
Test script for Case Management Reports
Tests all 4 reports to ensure they execute without SQL errors
"""

import frappe
from frappe.utils import getdate, add_days

def test_reports():
    """Test all 4 Case Management reports"""
    
    print("=" * 80)
    print("TESTING CASE MANAGEMENT REPORTS")
    print("=" * 80)
    
    # Ensure we have some test data
    create_test_data()
    
    # Test each report
    reports = [
        {
            "name": "Case Aging Report",
            "module": "sigma.sigma_case_management.report.case_aging_report.case_aging_report"
        },
        {
            "name": "Case Summary Dashboard",
            "module": "sigma.sigma_case_management.report.case_summary_dashboard.case_summary_dashboard"
        },
        {
            "name": "High Severity Case Matrix",
            "module": "sigma.sigma_case_management.report.high_severity_case_matrix.high_severity_case_matrix"
        },
        {
            "name": "Case Outcome Analysis",
            "module": "sigma.sigma_case_management.report.case_outcome_analysis.case_outcome_analysis"
        }
    ]
    
    passed = 0
    failed = 0
    
    for report in reports:
        print(f"\n{passed + failed + 1}. Testing {report['name']}...")
        try:
            # Import the report module
            module = frappe.get_module(report['module'])
            
            # Execute the report with basic filters
            filters = {
                "from_date": add_days(getdate(), -30),
                "to_date": getdate()
            }
            
            result = module.execute(filters)
            
            # Check result structure
            if len(result) >= 2:
                columns, data = result[0], result[1]
                print(f"   ✓ Report executed successfully")
                print(f"   ✓ Columns: {len(columns)}")
                print(f"   ✓ Data rows: {len(data)}")
                
                if len(result) >= 4 and result[3]:
                    print(f"   ✓ Chart data: True")
                
                passed += 1
            else:
                print(f"   ✗ Invalid result structure")
                failed += 1
                
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return passed, failed


def create_test_data():
    """Create minimal test data if needed"""
    
    # Check if we have any cases
    case_count = frappe.db.count("Case")
    
    if case_count == 0:
        print("\n⚠ No cases found. Creating test data...")
        
        # Create test severity if needed
        if not frappe.db.exists("Case Severity Matrix", "High"):
            severity = frappe.get_doc({
                "doctype": "Case Severity Matrix",
                "severity_level": "High",
                "severity_score": 8,
                "response_time_hours": 4
            })
            severity.insert(ignore_permissions=True)
        
        # Create test category if needed
        if not frappe.db.exists("Case Category", "Test Category"):
            category = frappe.get_doc({
                "doctype": "Case Category",
                "category_name": "Test Category",
                "risk_weight": 5
            })
            category.insert(ignore_permissions=True)
        
        # Create test source if needed
        if not frappe.db.exists("Case Source", "Test Source"):
            source = frappe.get_doc({
                "doctype": "Case Source",
                "source_name": "Test Source"
            })
            source.insert(ignore_permissions=True)
        
        # Create a test case
        case = frappe.get_doc({
            "doctype": "Case",
            "case_title": "Test Case for Reports",
            "case_type": "Complaint",
            "case_category": "Test Category",
            "case_source": "Test Source",
            "severity": "High",
            "status": "Open",
            "description": "Test case for report testing",
            "date_reported": getdate()
        })
        case.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print("✓ Test data created")
    else:
        print(f"\n✓ Found {case_count} existing cases")


if __name__ == "__main__":
    test_reports()

