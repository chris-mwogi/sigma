# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

"""
Phase 7 Testing Script - Complete Risk Assessment Module Workflow
This script creates sample data and tests the entire risk management workflow
"""

import frappe
from frappe.utils import today, add_days, add_months, nowdate
import json


def execute():
	"""Main execution function for Phase 7 testing"""
	print("=" * 80)
	print("PHASE 7: TESTING & DOCUMENTATION")
	print("Complete Risk Assessment Module Workflow Test")
	print("=" * 80)

	# Step 1: Setup Configuration
	print("\n[STEP 1] Setting up configuration...")
	setup_configuration()

	# Step 2: Create Master Data
	print("\n[STEP 2] Creating master data...")
	create_master_data()

	# Step 3: Create Risk Register Entries
	print("\n[STEP 3] Creating risk register entries...")
	create_risk_register()

	# Step 4: Create Risk Assessments
	print("\n[STEP 4] Creating risk assessments...")
	create_risk_assessments()

	# Step 5: Create Controls
	print("\n[STEP 5] Creating risk controls...")
	create_risk_controls()

	# Step 6: Create Treatment Plans
	print("\n[STEP 6] Creating treatment plans...")
	create_treatment_plans()

	# Step 7: Create Compliance Requirements
	print("\n[STEP 7] Creating compliance requirements...")
	create_compliance_requirements()

	# Step 8: Create Business Processes
	print("\n[STEP 8] Creating business processes...")
	create_business_processes()

	# Step 9: Create KRIs
	print("\n[STEP 9] Creating key risk indicators...")
	create_kris()

	# Step 10: Create Incidents
	print("\n[STEP 10] Creating risk incidents...")
	create_incidents()

	# Step 11: Test Reports
	print("\n[STEP 11] Testing all reports...")
	test_reports()

	# Step 12: Summary
	print("\n[STEP 12] Generating test summary...")
	generate_summary()

	print("\n" + "=" * 80)
	print("PHASE 7 TESTING COMPLETE")
	print("=" * 80)

	frappe.db.commit()


def setup_configuration():
	"""Setup Risk Dashboard Settings"""
	try:
		settings = frappe.get_single("Risk Dashboard Settings")
		settings.risk_score_low_threshold = 6
		settings.risk_score_medium_threshold = 12
		settings.risk_score_high_threshold = 20
		settings.enable_email_alerts = 1
		settings.alert_on_critical_risk = 1
		settings.alert_on_high_risk = 1
		settings.save()
		print("  ✓ Risk Dashboard Settings configured")
	except Exception as e:
		print(f"  ✗ Error configuring settings: {str(e)}")


def create_master_data():
	"""Create master data: Categories, Impact Matrix, Likelihood Matrix"""
	# Create Risk Categories
	categories = [
		{"category_name": "Financial Risk", "category_code": "FIN", "description": "Financial and revenue risks"},
		{"category_name": "Operational Risk", "category_code": "OPS", "description": "Operational and process risks"},
		{"category_name": "Compliance Risk", "category_code": "COM", "description": "Regulatory and compliance risks"},
		{"category_name": "Strategic Risk", "category_code": "STR", "description": "Strategic and business risks"},
		{"category_name": "Technology Risk", "category_code": "TEC", "description": "IT and technology risks"},
	]

	for cat in categories:
		try:
			if not frappe.db.exists("Risk Category", {"category_code": cat["category_code"]}):
				doc = frappe.get_doc({
					"doctype": "Risk Category",
					**cat
				})
				doc.insert(ignore_permissions=True)
				print(f"  ✓ Created category: {cat['category_name']}")
		except Exception as e:
			print(f"  ✗ Error creating category {cat['category_name']}: {str(e)}")

	# Create Impact Matrix
	impacts = [
		{"impact_level": "Insignificant", "impact_score": 1, "description": "Minimal impact"},
		{"impact_level": "Minor", "impact_score": 2, "description": "Small impact"},
		{"impact_level": "Moderate", "impact_score": 3, "description": "Moderate impact"},
		{"impact_level": "Major", "impact_score": 4, "description": "Significant impact"},
		{"impact_level": "Catastrophic", "impact_score": 5, "description": "Severe impact"},
	]

	for impact in impacts:
		try:
			if not frappe.db.exists("Risk Impact Matrix", {"impact_level": impact["impact_level"]}):
				doc = frappe.get_doc({
					"doctype": "Risk Impact Matrix",
					**impact
				})
				doc.insert(ignore_permissions=True)
				print(f"  ✓ Created impact level: {impact['impact_level']}")
		except Exception as e:
			print(f"  ✗ Error creating impact {impact['impact_level']}: {str(e)}")

	# Create Likelihood Matrix
	likelihoods = [
		{"likelihood_level": "Rare", "likelihood_score": 1, "description": "Very unlikely"},
		{"likelihood_level": "Unlikely", "likelihood_score": 2, "description": "Not likely"},
		{"likelihood_level": "Possible", "likelihood_score": 3, "description": "Could happen"},
		{"likelihood_level": "Likely", "likelihood_score": 4, "description": "Probably will happen"},
		{"likelihood_level": "Almost Certain", "likelihood_score": 5, "description": "Expected to happen"},
	]

	for likelihood in likelihoods:
		try:
			if not frappe.db.exists("Risk Likelihood Matrix", {"likelihood_level": likelihood["likelihood_level"]}):
				doc = frappe.get_doc({
					"doctype": "Risk Likelihood Matrix",
					**likelihood
				})
				doc.insert(ignore_permissions=True)
				print(f"  ✓ Created likelihood level: {likelihood['likelihood_level']}")
		except Exception as e:
			print(f"  ✗ Error creating likelihood {likelihood['likelihood_level']}: {str(e)}")


def create_risk_register():
	"""Create sample risk register entries"""
	risks = [
		{
			"risk_title": "Cybersecurity Breach",
			"risk_description": "Potential unauthorized access to critical systems and data",
			"risk_category": "Technology Risk",
			"risk_owner": "Administrator",
			"date_identified": today(),
			"status": "Active",
			"review_frequency_days": 90
		},
		{
			"risk_title": "Revenue Collection Shortfall",
			"risk_description": "Failure to meet revenue targets due to collection inefficiencies",
			"risk_category": "Financial Risk",
			"risk_owner": "Administrator",
			"date_identified": add_days(today(), -30),
			"status": "Active",
			"review_frequency_days": 60
		},
		{
			"risk_title": "Regulatory Non-Compliance",
			"risk_description": "Failure to comply with industry regulations and standards",
			"risk_category": "Compliance Risk",
			"risk_owner": "Administrator",
			"date_identified": add_days(today(), -15),
			"status": "Active",
			"review_frequency_days": 30
		}
	]

	created_risks = []
	for risk in risks:
		try:
			doc = frappe.get_doc({
				"doctype": "Risk Register",
				**risk
			})
			doc.insert(ignore_permissions=True)
			doc.submit()
			created_risks.append(doc.name)
			print(f"  ✓ Created risk: {risk['risk_title']} ({doc.name})")
		except Exception as e:
			print(f"  ✗ Error creating risk {risk['risk_title']}: {str(e)}")

	return created_risks


def create_risk_assessments():
	"""Create risk assessments for registered risks"""
	# Get all active risks
	risks = frappe.get_all("Risk Register", filters={"status": "Active"}, pluck="name")

	for risk_name in risks[:3]:  # Create assessments for first 3 risks
		try:
			doc = frappe.get_doc({
				"doctype": "Risk Assessment",
				"linked_risk": risk_name,
				"assessment_type": "Initial",
				"assessment_date": today(),
				"assessed_by": "Administrator",
				"inherent_impact_level": "Major",
				"inherent_likelihood_level": "Likely",
				"existing_controls": "Basic security measures in place",
				"residual_impact_level": "Moderate",
				"residual_likelihood_level": "Possible",
				"risk_response_strategy": "Reduce",
				"recommended_actions": "Implement additional controls and monitoring"
			})
			doc.insert(ignore_permissions=True)
			doc.submit()
			print(f"  ✓ Created assessment for: {risk_name}")
		except Exception as e:
			print(f"  ✗ Error creating assessment for {risk_name}: {str(e)}")


def create_risk_controls():
	"""Create risk controls"""
	controls = [
		{
			"control_name": "Multi-Factor Authentication",
			"control_type": "Preventive",
			"control_category": "IT-Dependent",
			"control_owner": "Administrator",
			"implementation_status": "Implemented",
			"control_description": "MFA for all system access",
			"control_objective": "Prevent unauthorized access",
			"implementation_date": add_days(today(), -60)
		},
		{
			"control_name": "Revenue Reconciliation Process",
			"control_type": "Detective",
			"control_category": "Manual",
			"control_owner": "Administrator",
			"implementation_status": "Implemented",
			"control_description": "Daily revenue reconciliation",
			"control_objective": "Detect revenue discrepancies",
			"implementation_date": add_days(today(), -90)
		}
	]

	for control in controls:
		try:
			doc = frappe.get_doc({
				"doctype": "Risk Control",
				**control
			})
			doc.insert(ignore_permissions=True)
			print(f"  ✓ Created control: {control['control_name']}")
		except Exception as e:
			print(f"  ✗ Error creating control {control['control_name']}: {str(e)}")


def create_treatment_plans():
	"""Create risk treatment plans"""
	risks = frappe.get_all("Risk Register", filters={"status": "Active"}, pluck="name", limit=2)

	for risk_name in risks:
		try:
			doc = frappe.get_doc({
				"doctype": "Risk Treatment Plan",
				"plan_title": f"Treatment Plan for {risk_name}",
				"linked_risk": risk_name,
				"treatment_strategy": "Reduce",
				"plan_owner": "Administrator",
				"status": "In Progress",
				"start_date": today(),
				"target_completion_date": add_months(today(), 3),
				"estimated_budget": 50000,
				"treatment_actions": [
					{
						"action_description": "Implement enhanced monitoring",
						"responsible_person": "Administrator",
						"target_date": add_months(today(), 1),
						"status": "In Progress",
						"estimated_cost": 20000
					},
					{
						"action_description": "Conduct training program",
						"responsible_person": "Administrator",
						"target_date": add_months(today(), 2),
						"status": "Planned",
						"estimated_cost": 30000
					}
				]
			})
			doc.insert(ignore_permissions=True)
			doc.submit()
			print(f"  ✓ Created treatment plan for: {risk_name}")
		except Exception as e:
			print(f"  ✗ Error creating treatment plan for {risk_name}: {str(e)}")


def create_compliance_requirements():
	"""Create compliance requirements"""
	requirements = [
		{
			"requirement_title": "ISO 27001 Compliance",
			"requirement_type": "Industry Standard",
			"regulatory_framework": "ISO 27001",
			"compliance_owner": "Administrator",
			"compliance_status": "In Progress",
			"current_compliance_level": 75,
			"priority": "High",
			"effective_date": add_days(today(), -180)
		},
		{
			"requirement_title": "Data Protection Compliance",
			"requirement_type": "Regulatory",
			"regulatory_framework": "GDPR",
			"compliance_owner": "Administrator",
			"compliance_status": "Compliant",
			"current_compliance_level": 95,
			"priority": "Critical",
			"effective_date": add_days(today(), -365)
		}
	]

	for req in requirements:
		try:
			doc = frappe.get_doc({
				"doctype": "Compliance Requirement",
				**req
			})
			doc.insert(ignore_permissions=True)
			print(f"  ✓ Created compliance requirement: {req['requirement_title']}")
		except Exception as e:
			print(f"  ✗ Error creating requirement {req['requirement_title']}: {str(e)}")



def create_business_processes():
	"""Create business process register entries"""
	processes = [
		{
			"process_name": "Revenue Collection Process",
			"process_code": "REV-001",
			"process_owner": "Administrator",
			"process_criticality": "High",
			"process_description": "End-to-end revenue collection and reconciliation"
		},
		{
			"process_name": "IT Security Management",
			"process_code": "IT-001",
			"process_owner": "Administrator",
			"process_criticality": "Critical",
			"process_description": "Information security and access control management"
		}
	]

	for process in processes:
		try:
			doc = frappe.get_doc({
				"doctype": "Business Process Register",
				**process
			})
			doc.insert(ignore_permissions=True)
			print(f"  ✓ Created business process: {process['process_name']}")
		except Exception as e:
			print(f"  ✗ Error creating process {process['process_name']}: {str(e)}")


def create_kris():
	"""Create key risk indicators"""
	risks = frappe.get_all("Risk Register", filters={"status": "Active"}, pluck="name", limit=2)

	kris = [
		{
			"kri_name": "System Uptime Percentage",
			"kri_category": "Technology",
			"linked_risk": risks[0] if len(risks) > 0 else None,
			"kri_owner": "Administrator",
			"measurement_frequency": "Daily",
			"unit_of_measurement": "Percentage",
			"target_value": 99.9,
			"current_value": 99.5,
			"threshold_direction": "Higher is Better",
			"threshold_green": 99.5,
			"threshold_yellow": 98.0,
			"threshold_red": 95.0,
			"status": "Active"
		},
		{
			"kri_name": "Revenue Collection Rate",
			"kri_category": "Financial",
			"linked_risk": risks[1] if len(risks) > 1 else None,
			"kri_owner": "Administrator",
			"measurement_frequency": "Monthly",
			"unit_of_measurement": "Percentage",
			"target_value": 95.0,
			"current_value": 92.0,
			"threshold_direction": "Higher is Better",
			"threshold_green": 95.0,
			"threshold_yellow": 90.0,
			"threshold_red": 85.0,
			"status": "Active"
		}
	]

	for kri in kris:
		try:
			doc = frappe.get_doc({
				"doctype": "Key Risk Indicator",
				**kri
			})
			doc.insert(ignore_permissions=True)
			print(f"  ✓ Created KRI: {kri['kri_name']}")
		except Exception as e:
			print(f"  ✗ Error creating KRI {kri['kri_name']}: {str(e)}")


def create_incidents():
	"""Create risk incidents"""
	risks = frappe.get_all("Risk Register", filters={"status": "Active"}, pluck="name", limit=2)

	incidents = [
		{
			"incident_title": "Unauthorized Access Attempt",
			"incident_type": "Security Incident",
			"incident_category": "Technology Risk",
			"incident_date": add_days(today(), -5),
			"reported_by": "Administrator",
			"incident_status": "Under Investigation",
			"impact_level": "Medium",
			"financial_impact": 5000,
			"linked_risk": risks[0] if len(risks) > 0 else None,
			"incident_description": "Multiple failed login attempts detected",
			"investigation_status": "In Progress",
			"investigation_owner": "Administrator"
		},
		{
			"incident_title": "Payment Processing Delay",
			"incident_type": "Operational Failure",
			"incident_category": "Financial Risk",
			"incident_date": add_days(today(), -10),
			"reported_by": "Administrator",
			"incident_status": "Resolved",
			"impact_level": "Low",
			"financial_impact": 2000,
			"linked_risk": risks[1] if len(risks) > 1 else None,
			"incident_description": "System downtime caused payment delays",
			"investigation_status": "Completed",
			"investigation_owner": "Administrator",
			"closure_date": add_days(today(), -2)
		}
	]

	for incident in incidents:
		try:
			doc = frappe.get_doc({
				"doctype": "Risk Incident",
				**incident
			})
			doc.insert(ignore_permissions=True)
			if incident["incident_status"] == "Resolved":
				doc.submit()
			print(f"  ✓ Created incident: {incident['incident_title']}")
		except Exception as e:
			print(f"  ✗ Error creating incident {incident['incident_title']}: {str(e)}")


def test_reports():
	"""Test all script reports"""
	reports = [
		"Risk Register Report",
		"Risk Heat Map",
		"Risk Treatment Status Report",
		"Compliance Status Report",
		"KRI Dashboard Report",
		"Risk Incident Analysis"
	]

	for report_name in reports:
		try:
			# Import the report module dynamically
			report_module = frappe.get_attr(
				f"sigma.sigma_risk_assessment.report.{report_name.lower().replace(' ', '_')}.{report_name.lower().replace(' ', '_')}.execute"
			)

			# Execute the report
			columns, data = report_module()[:2]

			print(f"  ✓ {report_name}: {len(data)} records, {len(columns)} columns")
		except Exception as e:
			print(f"  ✗ Error testing report {report_name}: {str(e)}")


def generate_summary():
	"""Generate test summary"""
	print("\n" + "=" * 80)
	print("TEST SUMMARY")
	print("=" * 80)

	# Count all created records
	doctypes = [
		"Risk Category",
		"Risk Impact Matrix",
		"Risk Likelihood Matrix",
		"Risk Register",
		"Risk Assessment",
		"Risk Control",
		"Risk Treatment Plan",
		"Compliance Requirement",
		"Business Process Register",
		"Key Risk Indicator",
		"Risk Incident"
	]

	for doctype in doctypes:
		try:
			count = frappe.db.count(doctype)
			print(f"  {doctype}: {count} records")
		except Exception as e:
			print(f"  {doctype}: Error - {str(e)}")

	print("\n" + "=" * 80)
	print("BROWSER TESTING URLS")
	print("=" * 80)
	print("\nWorkspace:")
	print("  http://172.24.13.88:8000/app/risk-assessment")
	print("\nDocTypes:")
	print("  http://172.24.13.88:8000/app/risk-register")
	print("  http://172.24.13.88:8000/app/risk-assessment")
	print("  http://172.24.13.88:8000/app/risk-control")
	print("  http://172.24.13.88:8000/app/risk-treatment-plan")
	print("  http://172.24.13.88:8000/app/key-risk-indicator")
	print("  http://172.24.13.88:8000/app/risk-incident")
	print("\nReports:")
	print("  http://172.24.13.88:8000/app/query-report/Risk%20Register%20Report")
	print("  http://172.24.13.88:8000/app/query-report/Risk%20Heat%20Map")
	print("  http://172.24.13.88:8000/app/query-report/Risk%20Treatment%20Status%20Report")
	print("  http://172.24.13.88:8000/app/query-report/Compliance%20Status%20Report")
	print("  http://172.24.13.88:8000/app/query-report/KRI%20Dashboard%20Report")
	print("  http://172.24.13.88:8000/app/query-report/Risk%20Incident%20Analysis")


