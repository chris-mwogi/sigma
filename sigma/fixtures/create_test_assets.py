"""
Test Data Script for Location-Based Asset Tree
Creates sample assets at "Electricity House Mombasa" location for testing the asset tree viewer.
"""

import frappe
from frappe import _


def create_test_assets():
	"""
	Create test assets with hierarchical structure at Electricity House Mombasa location.
	This creates a realistic asset hierarchy for testing the location-based asset tree viewer.
	"""
	frappe.flags.in_test = False
	
	print("\n" + "="*80)
	print("Creating Test Assets for Location-Based Asset Tree")
	print("="*80 + "\n")
	
	# Step 1: Ensure Location exists
	location_name = ensure_location_exists()
	print(f"✓ Location: {location_name}")
	
	# Step 2: Ensure Asset Categories exist
	categories = ensure_asset_categories_exist()
	print(f"✓ Asset Categories: {len(categories)} categories created/verified")
	
	# Step 3: Create root-level assets (systems at the location)
	root_assets = create_root_assets(location_name, categories)
	print(f"✓ Root Assets: {len(root_assets)} root-level systems created")
	
	# Step 4: Create child assets (components of systems)
	child_assets = create_child_assets(root_assets, location_name, categories)
	print(f"✓ Child Assets: {len(child_assets)} child components created")
	
	# Step 5: Create sub-components (nested hierarchy)
	subcomponents = create_subcomponents(child_assets, location_name, categories)
	print(f"✓ Sub-components: {len(subcomponents)} sub-components created")
	
	frappe.db.commit()
	
	print("\n" + "="*80)
	print("Test Data Creation Complete!")
	print("="*80)
	print(f"\nTotal Assets Created: {len(root_assets) + len(child_assets) + len(subcomponents)}")
	print(f"Location: {location_name}")
	print("\nYou can now test the Asset Tree Viewer at:")
	print("http://prismod.localhost:8000/app/asset-tree-viewer")
	print("\n")
	
	return {
		"status": "success",
		"location": location_name,
		"root_assets": len(root_assets),
		"child_assets": len(child_assets),
		"subcomponents": len(subcomponents),
		"total": len(root_assets) + len(child_assets) + len(subcomponents)
	}


def ensure_location_exists():
	"""Ensure the test location exists."""
	location_name = "Electricity House Mombasa"

	if not frappe.db.exists("Location", location_name):
		location = frappe.get_doc({
			"doctype": "Location",
			"location_name": location_name,
			"location_type": "Office",
			"is_group": 0
		})
		location.insert(ignore_permissions=True)
		print(f"  Created location: {location_name}")
	else:
		print(f"  Location already exists: {location_name}")

	return location_name


def ensure_asset_categories_exist():
	"""Ensure required asset categories exist."""
	categories = [
		"HVAC System",
		"Electrical System",
		"Security System",
		"Fire Safety System",
		"Access Control System"
	]

	company = get_default_company()

	# Get default accounts for the company
	default_accounts = get_default_asset_accounts(company)

	created_categories = []
	for category_name in categories:
		if not frappe.db.exists("Asset Category", category_name):
			category = frappe.get_doc({
				"doctype": "Asset Category",
				"asset_category_name": category_name,
				"enable_cwip_accounting": 0,
				"accounts": [{
					"company_name": company,
					"fixed_asset_account": default_accounts.get("fixed_asset_account"),
					"accumulated_depreciation_account": default_accounts.get("accumulated_depreciation_account"),
					"depreciation_expense_account": default_accounts.get("depreciation_expense_account")
				}]
			})
			category.insert(ignore_permissions=True)
			print(f"  Created category: {category_name}")
		else:
			print(f"  Category already exists: {category_name}")
		created_categories.append(category_name)

	return created_categories


def create_root_assets(location_name, categories):
	"""Create root-level assets (main systems at the location)."""
	root_assets_data = [
		{
			"asset_name": "Main HVAC System",
			"asset_category": "HVAC System",
			"item_code": "HVAC-MAIN-001",
			"status": "In Use"
		},
		{
			"asset_name": "Primary Electrical Panel",
			"asset_category": "Electrical System",
			"item_code": "ELEC-PANEL-001",
			"status": "In Use"
		},
		{
			"asset_name": "Building Security System",
			"asset_category": "Security System",
			"item_code": "SEC-SYS-001",
			"status": "In Use"
		},
		{
			"asset_name": "Fire Alarm System",
			"asset_category": "Fire Safety System",
			"item_code": "FIRE-SYS-001",
			"status": "In Use"
		}
	]
	
	created_assets = []
	for asset_data in root_assets_data:
		# Check if asset already exists
		if frappe.db.exists("Asset", {"item_code": asset_data["item_code"]}):
			asset_name = frappe.db.get_value("Asset", {"item_code": asset_data["item_code"]}, "name")
			print(f"  Asset already exists: {asset_data['asset_name']} ({asset_name})")
			created_assets.append(asset_name)
			continue
		
		# Ensure item exists
		item_code = ensure_item_exists(asset_data["item_code"], asset_data["asset_name"], asset_data["asset_category"])

		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": asset_data["asset_name"],
			"asset_category": asset_data["asset_category"],
			"item_code": item_code,
			"location": location_name,
			"asset_location": location_name,
			"company": get_default_company(),
			"is_existing_asset": 1,
			"gross_purchase_amount": 100000,
			"net_purchase_amount": 100000,
			"purchase_date": frappe.utils.today(),
			"available_for_use_date": frappe.utils.today(),
			"calculate_depreciation": 0
		})
		asset.insert(ignore_permissions=True)
		# Don't submit - just save as draft for testing
		created_assets.append(asset.name)
		print(f"  Created root asset: {asset_data['asset_name']} ({asset.name})")
	
	return created_assets


def create_child_assets(parent_assets, location_name, categories):
	"""Create child assets (components of main systems)."""
	child_assets_config = {
		0: [  # Children of Main HVAC System
			{"name": "Air Handler Unit 1", "category": "HVAC System", "code": "AHU-001"},
			{"name": "Air Handler Unit 2", "category": "HVAC System", "code": "AHU-002"},
			{"name": "Chiller Unit", "category": "HVAC System", "code": "CHILL-001"}
		],
		1: [  # Children of Primary Electrical Panel
			{"name": "Distribution Panel A", "category": "Electrical System", "code": "DIST-A-001"},
			{"name": "Distribution Panel B", "category": "Electrical System", "code": "DIST-B-001"},
			{"name": "UPS System", "category": "Electrical System", "code": "UPS-001"}
		],
		2: [  # Children of Building Security System
			{"name": "CCTV Camera System", "category": "Security System", "code": "CCTV-001"},
			{"name": "Access Control Panel", "category": "Access Control System", "code": "ACC-CTRL-001"},
			{"name": "Intrusion Detection System", "category": "Security System", "code": "IDS-001"}
		],
		3: [  # Children of Fire Alarm System
			{"name": "Fire Control Panel", "category": "Fire Safety System", "code": "FIRE-CTRL-001"},
			{"name": "Smoke Detector Network", "category": "Fire Safety System", "code": "SMOKE-NET-001"}
		]
	}
	
	created_children = []
	for parent_idx, children_data in child_assets_config.items():
		if parent_idx >= len(parent_assets):
			continue
			
		parent_asset_id = parent_assets[parent_idx]
		
		for child_data in children_data:
			# Check if asset already exists
			if frappe.db.exists("Asset", {"item_code": child_data["code"]}):
				asset_name = frappe.db.get_value("Asset", {"item_code": child_data["code"]}, "name")
				print(f"  Child asset already exists: {child_data['name']} ({asset_name})")
				created_children.append(asset_name)
				continue
			
			# Ensure item exists
			item_code = ensure_item_exists(child_data["code"], child_data["name"], child_data["category"])

			asset = frappe.get_doc({
				"doctype": "Asset",
				"asset_name": child_data["name"],
				"asset_category": child_data["category"],
				"item_code": item_code,
				"location": location_name,
				"asset_location": location_name,
				"parent_system": parent_asset_id,
				"company": get_default_company(),
				"is_existing_asset": 1,
				"gross_purchase_amount": 50000,
				"net_purchase_amount": 50000,
				"purchase_date": frappe.utils.today(),
				"available_for_use_date": frappe.utils.today(),
				"calculate_depreciation": 0
			})
			asset.insert(ignore_permissions=True)
			# Don't submit - just save as draft for testing
			created_children.append(asset.name)
			print(f"  Created child asset: {child_data['name']} ({asset.name}) under {parent_asset_id}")
	
	return created_children


def create_subcomponents(parent_children, location_name, categories):
	"""Create sub-components (third level in hierarchy)."""
	# Create sub-components for CCTV Camera System (index 6 in parent_children if all created)
	subcomponents_data = [
		{"name": "Camera - Main Entrance", "category": "Security System", "code": "CAM-ENT-001", "parent_idx": 6},
		{"name": "Camera - Parking Lot", "category": "Security System", "code": "CAM-PARK-001", "parent_idx": 6},
		{"name": "Camera - Lobby", "category": "Security System", "code": "CAM-LOBBY-001", "parent_idx": 6},
		{"name": "NVR Recording System", "category": "Security System", "code": "NVR-001", "parent_idx": 6}
	]
	
	created_subcomponents = []
	for subcomp_data in subcomponents_data:
		parent_idx = subcomp_data["parent_idx"]
		
		if parent_idx >= len(parent_children):
			continue
		
		parent_asset_id = parent_children[parent_idx]
		
		# Check if asset already exists
		if frappe.db.exists("Asset", {"item_code": subcomp_data["code"]}):
			asset_name = frappe.db.get_value("Asset", {"item_code": subcomp_data["code"]}, "name")
			print(f"  Sub-component already exists: {subcomp_data['name']} ({asset_name})")
			created_subcomponents.append(asset_name)
			continue
		
		# Ensure item exists
		item_code = ensure_item_exists(subcomp_data["code"], subcomp_data["name"], subcomp_data["category"])

		asset = frappe.get_doc({
			"doctype": "Asset",
			"asset_name": subcomp_data["name"],
			"asset_category": subcomp_data["category"],
			"item_code": item_code,
			"location": location_name,
			"asset_location": location_name,
			"parent_system": parent_asset_id,
			"company": get_default_company(),
			"is_existing_asset": 1,
			"gross_purchase_amount": 10000,
			"net_purchase_amount": 10000,
			"purchase_date": frappe.utils.today(),
			"available_for_use_date": frappe.utils.today(),
			"calculate_depreciation": 0
		})
		asset.insert(ignore_permissions=True)
		# Don't submit - just save as draft for testing
		created_subcomponents.append(asset.name)
		print(f"  Created sub-component: {subcomp_data['name']} ({asset.name}) under {parent_asset_id}")
	
	return created_subcomponents


def ensure_item_exists(item_code, item_name, asset_category):
	"""Ensure an item exists for the asset."""
	if not frappe.db.exists("Item", item_code):
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_name,
			"item_group": "Products",
			"stock_uom": "Nos",
			"is_stock_item": 0,
			"is_fixed_asset": 1,
			"asset_category": asset_category
		})
		item.insert(ignore_permissions=True)
	return item_code


def get_default_company():
	"""Get the default company."""
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		company = frappe.db.get_value("Company", {}, "name")
	return company


def get_default_asset_accounts(company):
	"""Get default asset accounts for the company."""
	# Try to get from an existing asset category
	existing_category = frappe.db.get_value(
		"Asset Category Account",
		{"company_name": company},
		["fixed_asset_account", "accumulated_depreciation_account", "depreciation_expense_account"],
		as_dict=True
	)

	if existing_category:
		return existing_category

	# Fallback: Get from company's default accounts
	company_doc = frappe.get_doc("Company", company)

	# Try to find appropriate accounts
	fixed_asset_account = frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Fixed Asset", "is_group": 0},
		"name"
	)

	accumulated_depreciation_account = frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Accumulated Depreciation", "is_group": 0},
		"name"
	)

	depreciation_expense_account = frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Depreciation", "is_group": 0},
		"name"
	)

	return {
		"fixed_asset_account": fixed_asset_account,
		"accumulated_depreciation_account": accumulated_depreciation_account,
		"depreciation_expense_account": depreciation_expense_account
	}

