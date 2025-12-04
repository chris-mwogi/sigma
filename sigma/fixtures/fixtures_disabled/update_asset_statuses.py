"""
Update Asset Statuses for Testing UI Color-Coding
Updates various assets to different statuses to showcase the UI variations
"""

import frappe


def update_asset_statuses():
	"""Update assets to different statuses for testing"""
	
	print("\n" + "="*80)
	print("Updating Asset Statuses for UI Testing")
	print("="*80 + "\n")
	
	# Assets to update with their new statuses
	assets_to_update = [
		# Regional Office Nairobi - Mix of statuses
		('ACC-ASS-2025-00020', 'In Use'),
		('ACC-ASS-2025-00021', 'In Use'),
		('ACC-ASS-2025-00022', 'In Use'),
		('ACC-ASS-2025-00023', 'Available'),
		('ACC-ASS-2025-00024', 'In Use'),
		('ACC-ASS-2025-00025', 'In Use'),
		('ACC-ASS-2025-00026', 'In Use'),
		('ACC-ASS-2025-00027', 'In Use'),
		('ACC-ASS-2025-00028', 'In Use'),
		('ACC-ASS-2025-00029', 'In Use'),
		('ACC-ASS-2025-00030', 'In Use'),
		('ACC-ASS-2025-00031', 'In Use'),
		('ACC-ASS-2025-00032', 'In Use'),
		('ACC-ASS-2025-00033', 'In Use'),
		
		# Substation Kisumu - Mostly In Use
		('ACC-ASS-2025-00034', 'In Use'),
		('ACC-ASS-2025-00035', 'In Use'),
		('ACC-ASS-2025-00036', 'In Use'),
		('ACC-ASS-2025-00037', 'In Use'),
		('ACC-ASS-2025-00038', 'In Use'),
		('ACC-ASS-2025-00039', 'In Use'),
		('ACC-ASS-2025-00040', 'In Use'),
		('ACC-ASS-2025-00041', 'In Use'),
		('ACC-ASS-2025-00042', 'In Use'),
		('ACC-ASS-2025-00043', 'In Use'),
		('ACC-ASS-2025-00044', 'In Use'),
		('ACC-ASS-2025-00045', 'In Use'),
		('ACC-ASS-2025-00046', 'In Use'),
		('ACC-ASS-2025-00047', 'In Use'),
		('ACC-ASS-2025-00048', 'Available'),
		('ACC-ASS-2025-00049', 'In Use'),
		('ACC-ASS-2025-00050', 'In Use'),
		('ACC-ASS-2025-00051', 'In Use'),
		('ACC-ASS-2025-00052', 'In Use'),
		
		# Branch Office Nakuru - Mix including Under Maintenance
		('ACC-ASS-2025-00053', 'In Use'),
		('ACC-ASS-2025-00054', 'In Use'),
		('ACC-ASS-2025-00055', 'In Use'),
		('ACC-ASS-2025-00056', 'Under Maintenance'),
		('ACC-ASS-2025-00057', 'In Use'),
		('ACC-ASS-2025-00058', 'In Use'),
		('ACC-ASS-2025-00059', 'In Use'),
		('ACC-ASS-2025-00060', 'In Use'),
		('ACC-ASS-2025-00061', 'Available'),
		('ACC-ASS-2025-00062', 'In Use'),
		('ACC-ASS-2025-00063', 'In Use'),
		('ACC-ASS-2025-00064', 'In Use'),
		('ACC-ASS-2025-00065', 'In Use'),
		('ACC-ASS-2025-00066', 'In Use'),
		('ACC-ASS-2025-00067', 'In Use'),
		('ACC-ASS-2025-00068', 'In Use'),
		('ACC-ASS-2025-00069', 'Available'),
	]
	
	updated_count = 0
	status_counts = {}
	
	for asset_id, status in assets_to_update:
		if frappe.db.exists('Asset', asset_id):
			asset = frappe.get_doc('Asset', asset_id)
			asset.status = status
			asset.save(ignore_permissions=True)
			updated_count += 1
			
			# Count statuses
			status_counts[status] = status_counts.get(status, 0) + 1
			
			print(f"  Updated {asset_id} to status: {status}")
		else:
			print(f"  Asset {asset_id} not found")
	
	frappe.db.commit()
	
	print("\n" + "="*80)
	print("Asset Status Update Complete!")
	print("="*80 + "\n")
	print(f"Total Assets Updated: {updated_count}")
	print("\nStatus Distribution:")
	for status, count in sorted(status_counts.items()):
		print(f"  {status}: {count} assets")
	print()
	
	return {
		"status": "success",
		"updated_count": updated_count,
		"status_distribution": status_counts
	}

