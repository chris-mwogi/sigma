# Copyright (c) 2025, Nevel Enterprises Limited and contributors
# For license information, please see license.txt

"""
Migration Script: Guard Shift to Security Resource
Migrates existing Guard Shift records to the new Security Resource DocType
"""

import frappe
from frappe.utils import now_datetime


def migrate_guard_shifts(dry_run=True):
	"""
	Migrate Guard Shift records to Security Resource
	
	Args:
		dry_run (bool): If True, only show what would be migrated without making changes
	
	Returns:
		dict: Migration summary with counts
	"""
	
	print("\n" + "=" * 80)
	print("GUARD SHIFT TO SECURITY RESOURCE MIGRATION")
	print("=" * 80)
	print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}\n")
	
	summary = {
		"total_guard_shifts": 0,
		"migrated": 0,
		"skipped": 0,
		"errors": 0,
		"error_details": []
	}
	
	try:
		# Get all Guard Shift records
		guard_shifts = frappe.get_all(
			"Guard Shift",
			fields=["name", "site_allocation", "guard_name", "check_in_time", "check_out_time", "status", "shift_report"],
			order_by="creation"
		)
		
		summary["total_guard_shifts"] = len(guard_shifts)
		print(f"Found {len(guard_shifts)} Guard Shift records to migrate\n")
		
		for idx, gs in enumerate(guard_shifts, 1):
			try:
				# Get site allocation details
				site_alloc = frappe.get_doc("Site Allocation", gs.site_allocation)
				
				# Create Security Resource record
				security_resource = frappe.new_doc("Security Resource")
				security_resource.resource_type = "Guard"
				security_resource.resource_name = gs.guard_name
				security_resource.supplier = site_alloc.supplier
				security_resource.status = "Active" if gs.status == "Active" else "Inactive"
				security_resource.employee_id = None  # Will need manual linking
				
				if not dry_run:
					security_resource.insert(ignore_permissions=True)
					frappe.db.commit()
				
				print(f"[{idx}/{len(guard_shifts)}] ✓ Migrated: {gs.name} → {security_resource.name if not dry_run else 'SR-Guard-XXXX'}")
				summary["migrated"] += 1
				
			except Exception as e:
				print(f"[{idx}/{len(guard_shifts)}] ✗ Error: {gs.name} - {str(e)}")
				summary["errors"] += 1
				summary["error_details"].append({
					"guard_shift": gs.name,
					"error": str(e)
				})
		
		print("\n" + "=" * 80)
		print("MIGRATION SUMMARY")
		print("=" * 80)
		print(f"Total Guard Shifts: {summary['total_guard_shifts']}")
		print(f"Migrated: {summary['migrated']}")
		print(f"Skipped: {summary['skipped']}")
		print(f"Errors: {summary['errors']}")
		
		if summary["error_details"]:
			print("\nError Details:")
			for error in summary["error_details"]:
				print(f"  - {error['guard_shift']}: {error['error']}")
		
		print("\n" + "=" * 80)
		
		if dry_run:
			print("DRY RUN COMPLETE - No changes made")
		else:
			print("MIGRATION COMPLETE - All changes committed")
		
		print("=" * 80 + "\n")
		
		return summary
		
	except Exception as e:
		print(f"\n✗ MIGRATION FAILED: {str(e)}")
		import traceback
		traceback.print_exc()
		return summary


def migrate_site_allocation_to_resource_deployment(dry_run=True):
	"""
	Migrate Site Allocation records to Resource Deployment
	
	Args:
		dry_run (bool): If True, only show what would be migrated without making changes
	
	Returns:
		dict: Migration summary with counts
	"""
	
	print("\n" + "=" * 80)
	print("SITE ALLOCATION TO RESOURCE DEPLOYMENT MIGRATION")
	print("=" * 80)
	print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}\n")
	
	summary = {
		"total_site_allocations": 0,
		"migrated": 0,
		"skipped": 0,
		"errors": 0,
		"error_details": []
	}
	
	try:
		# Get all Site Allocation records
		site_allocs = frappe.get_all(
			"Site Allocation",
			fields=["name", "location", "supplier", "start_date", "end_date"],
			order_by="creation"
		)
		
		summary["total_site_allocations"] = len(site_allocs)
		print(f"Found {len(site_allocs)} Site Allocation records to migrate\n")
		
		for idx, sa in enumerate(site_allocs, 1):
			try:
				# Create Resource Deployment record
				resource_deployment = frappe.new_doc("Resource Deployment")
				resource_deployment.deployment_date = sa.start_date or frappe.utils.today()
				resource_deployment.location = sa.location
				resource_deployment.service_contract = None  # Will need manual linking
				
				# Note: Resources will need to be added manually as we don't have direct mapping
				
				if not dry_run:
					resource_deployment.insert(ignore_permissions=True)
					frappe.db.commit()
				
				print(f"[{idx}/{len(site_allocs)}] ✓ Migrated: {sa.name} → {resource_deployment.name if not dry_run else 'RD-XXXX-XXXX'}")
				summary["migrated"] += 1
				
			except Exception as e:
				print(f"[{idx}/{len(site_allocs)}] ✗ Error: {sa.name} - {str(e)}")
				summary["errors"] += 1
				summary["error_details"].append({
					"site_allocation": sa.name,
					"error": str(e)
				})
		
		print("\n" + "=" * 80)
		print("MIGRATION SUMMARY")
		print("=" * 80)
		print(f"Total Site Allocations: {summary['total_site_allocations']}")
		print(f"Migrated: {summary['migrated']}")
		print(f"Skipped: {summary['skipped']}")
		print(f"Errors: {summary['errors']}")
		
		if summary["error_details"]:
			print("\nError Details:")
			for error in summary["error_details"]:
				print(f"  - {error['site_allocation']}: {error['error']}")
		
		print("\n" + "=" * 80)
		
		if dry_run:
			print("DRY RUN COMPLETE - No changes made")
		else:
			print("MIGRATION COMPLETE - All changes committed")
		
		print("=" * 80 + "\n")
		
		return summary
		
	except Exception as e:
		print(f"\n✗ MIGRATION FAILED: {str(e)}")
		import traceback
		traceback.print_exc()
		return summary


if __name__ == "__main__":
	# This script should be run via Frappe console:
	# bench --site prismod.localhost execute sigma.api.migrations.migrate_guard_shift_to_security_resource.migrate_guard_shifts --kwargs "{'dry_run': True}"
	pass

