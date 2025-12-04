"""
Extended Test Data Script for Asset Tree Viewer
Creates multiple locations with diverse asset hierarchies for testing scalability and UI variations.

Locations:
1. Regional Office Nairobi - Office equipment, IT infrastructure, security
2. Substation Kisumu - Electrical and power distribution equipment
3. Branch Office Nakuru - Office equipment and security systems

Total Assets: 50-100 across all locations
"""

import frappe
from frappe import _


def create_extended_test_assets():
	"""Main function to create extended test data across multiple locations"""
	
	print("\n" + "="*80)
	print("Creating Extended Test Assets for Multiple Locations")
	print("="*80 + "\n")
	
	frappe.flags.in_test = True
	
	# Create locations
	locations = create_locations()
	print(f"✓ Locations: {len(locations)} locations created/verified\n")
	
	# Create additional asset categories
	categories = ensure_asset_categories_exist()
	print(f"✓ Asset Categories: {len(categories)} categories created/verified\n")
	
	# Create assets for each location
	total_assets = 0
	
	# Location 1: Regional Office Nairobi
	nairobi_assets = create_nairobi_office_assets(locations['nairobi'], categories)
	total_assets += nairobi_assets
	print(f"✓ Regional Office Nairobi: {nairobi_assets} assets created\n")
	
	# Location 2: Substation Kisumu
	kisumu_assets = create_kisumu_substation_assets(locations['kisumu'], categories)
	total_assets += kisumu_assets
	print(f"✓ Substation Kisumu: {kisumu_assets} assets created\n")
	
	# Location 3: Branch Office Nakuru
	nakuru_assets = create_nakuru_branch_assets(locations['nakuru'], categories)
	total_assets += nakuru_assets
	print(f"✓ Branch Office Nakuru: {nakuru_assets} assets created\n")
	
	frappe.db.commit()
	
	print("="*80)
	print("Extended Test Data Creation Complete!")
	print("="*80 + "\n")
	print(f"Total Assets Created: {total_assets}")
	print(f"Total Locations: {len(locations)}")
	print("\nYou can now test the Asset Tree Viewer with multiple locations at:")
	print("http://prismod.localhost:8000/app/asset-tree-viewer\n")
	
	return {
		"status": "success",
		"locations": len(locations),
		"total_assets": total_assets,
		"nairobi": nairobi_assets,
		"kisumu": kisumu_assets,
		"nakuru": nakuru_assets
	}


def create_locations():
	"""Create test locations"""
	locations = {}
	
	location_data = [
		{"name": "Regional Office Nairobi", "type": "Office", "key": "nairobi"},
		{"name": "Substation Kisumu", "type": "Substation", "key": "kisumu"},
		{"name": "Branch Office Nakuru", "type": "Branch", "key": "nakuru"}
	]
	
	for loc in location_data:
		if not frappe.db.exists("Location", loc["name"]):
			location = frappe.get_doc({
				"doctype": "Location",
				"location_name": loc["name"],
				"location_type": loc["type"]
			})
			location.insert(ignore_permissions=True)
			print(f"  Created location: {loc['name']}")
		else:
			print(f"  Location exists: {loc['name']}")
		
		locations[loc["key"]] = loc["name"]
	
	return locations


def ensure_asset_categories_exist():
	"""Ensure all required asset categories exist"""
	company = get_default_company()
	accounts = get_default_asset_accounts(company)
	
	categories = [
		"HVAC System",
		"Electrical System",
		"Security System",
		"Fire Safety System",
		"Access Control System",
		"IT Equipment",
		"Network Equipment",
		"Office Furniture",
		"Power Distribution",
		"Generator System"
	]
	
	existing_categories = []
	
	for category_name in categories:
		if not frappe.db.exists("Asset Category", category_name):
			category = frappe.get_doc({
				"doctype": "Asset Category",
				"asset_category_name": category_name,
				"enable_cwip_accounting": 0,
				"accounts": [{
					"company_name": company,
					"fixed_asset_account": accounts["fixed_asset_account"],
					"accumulated_depreciation_account": accounts["accumulated_depreciation_account"],
					"depreciation_expense_account": accounts["depreciation_expense_account"]
				}]
			})
			category.insert(ignore_permissions=True)
		
		existing_categories.append(category_name)
	
	return existing_categories


def get_default_company():
	"""Get the default company"""
	return frappe.db.get_single_value("Global Defaults", "default_company") or frappe.get_all("Company", limit=1)[0].name


def get_default_asset_accounts(company):
	"""Get default asset accounts for the company"""
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


def ensure_item_exists(item_code, item_name, asset_category):
	"""Ensure an item exists for the asset"""
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


def create_asset(asset_name, category, location, parent_system=None, status="Draft", purchase_amount=50000):
	"""Helper function to create an asset"""
	item_code = f"ITEM-{asset_name.replace(' ', '-').upper()}"
	ensure_item_exists(item_code, asset_name, category)
	
	asset = frappe.get_doc({
		"doctype": "Asset",
		"asset_name": asset_name,
		"asset_category": category,
		"item_code": item_code,
		"location": location,
		"asset_location": location,
		"company": get_default_company(),
		"is_existing_asset": 1,
		"gross_purchase_amount": purchase_amount,
		"net_purchase_amount": purchase_amount,
		"purchase_date": frappe.utils.today(),
		"available_for_use_date": frappe.utils.today(),
		"calculate_depreciation": 0
	})
	
	if parent_system:
		asset.parent_system = parent_system
	
	asset.insert(ignore_permissions=True)
	
	# Update status if not Draft
	if status != "Draft":
		asset.status = status
		asset.save(ignore_permissions=True)
	
	return asset.name


def create_nairobi_office_assets(location, categories):
	"""Create assets for Regional Office Nairobi (20-30 assets)"""
	assets_created = 0
	
	# IT Infrastructure (Root)
	it_infra = create_asset("IT Infrastructure System", "IT Equipment", location, status="In Use", purchase_amount=500000)
	assets_created += 1
	print(f"  Created root asset: IT Infrastructure System ({it_infra})")
	
	# Servers under IT Infrastructure
	servers = [
		("Application Server", "IT Equipment", 150000, "In Use"),
		("Database Server", "IT Equipment", 180000, "In Use"),
		("Backup Server", "IT Equipment", 120000, "Available")
	]
	
	for server_name, cat, amount, stat in servers:
		asset_id = create_asset(server_name, cat, location, it_infra, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {server_name} ({asset_id}) under {it_infra}")
	
	# Network Equipment (Root)
	network = create_asset("Network Infrastructure", "Network Equipment", location, status="In Use", purchase_amount=300000)
	assets_created += 1
	print(f"  Created root asset: Network Infrastructure ({network})")
	
	# Network devices
	network_devices = [
		("Core Switch", "Network Equipment", 80000, "In Use"),
		("Distribution Switch 1", "Network Equipment", 50000, "In Use"),
		("Distribution Switch 2", "Network Equipment", 50000, "In Use"),
		("Firewall", "Network Equipment", 100000, "In Use"),
		("WiFi Controller", "Network Equipment", 40000, "In Use")
	]
	
	for device_name, cat, amount, stat in network_devices:
		asset_id = create_asset(device_name, cat, location, network, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {device_name} ({asset_id}) under {network}")
	
	# Security System (Root)
	security = create_asset("Office Security System", "Security System", location, status="In Use", purchase_amount=250000)
	assets_created += 1
	print(f"  Created root asset: Office Security System ({security})")
	
	# Security components
	security_items = [
		("CCTV System", "Security System", 80000, "In Use"),
		("Access Control System", "Access Control System", 60000, "In Use"),
		("Intrusion Alarm", "Security System", 40000, "In Use")
	]
	
	for sec_name, cat, amount, stat in security_items:
		asset_id = create_asset(sec_name, cat, location, security, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {sec_name} ({asset_id}) under {security}")
	
	return assets_created


def create_kisumu_substation_assets(location, categories):
	"""Create assets for Substation Kisumu (15-25 assets)"""
	assets_created = 0

	# Power Distribution System (Root)
	power_dist = create_asset("Main Power Distribution System", "Power Distribution", location, status="In Use", purchase_amount=800000)
	assets_created += 1
	print(f"  Created root asset: Main Power Distribution System ({power_dist})")

	# Transformers
	transformers = [
		("Primary Transformer 1", "Power Distribution", 300000, "In Use"),
		("Primary Transformer 2", "Power Distribution", 300000, "In Use"),
		("Step-Down Transformer", "Power Distribution", 150000, "In Use")
	]

	for trans_name, cat, amount, stat in transformers:
		asset_id = create_asset(trans_name, cat, location, power_dist, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {trans_name} ({asset_id}) under {power_dist}")

	# Electrical System (Root)
	electrical = create_asset("Electrical Control System", "Electrical System", location, status="In Use", purchase_amount=400000)
	assets_created += 1
	print(f"  Created root asset: Electrical Control System ({electrical})")

	# Electrical components
	electrical_items = [
		("Main Circuit Breaker Panel", "Electrical System", 80000, "In Use"),
		("Distribution Panel A", "Electrical System", 50000, "In Use"),
		("Distribution Panel B", "Electrical System", 50000, "In Use"),
		("Distribution Panel C", "Electrical System", 50000, "In Use"),
		("Metering System", "Electrical System", 60000, "In Use"),
		("Protection Relay System", "Electrical System", 70000, "In Use")
	]

	for elec_name, cat, amount, stat in electrical_items:
		asset_id = create_asset(elec_name, cat, location, electrical, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {elec_name} ({asset_id}) under {electrical}")

	# Generator System (Root)
	generator = create_asset("Backup Generator System", "Generator System", location, status="In Use", purchase_amount=350000)
	assets_created += 1
	print(f"  Created root asset: Backup Generator System ({generator})")

	# Generator components
	gen_items = [
		("Diesel Generator 500KVA", "Generator System", 250000, "In Use"),
		("Automatic Transfer Switch", "Electrical System", 60000, "In Use"),
		("Fuel Tank System", "Generator System", 40000, "In Use")
	]

	for gen_name, cat, amount, stat in gen_items:
		asset_id = create_asset(gen_name, cat, location, generator, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {gen_name} ({asset_id}) under {generator}")

	# Security System
	security = create_asset("Substation Security System", "Security System", location, status="In Use", purchase_amount=150000)
	assets_created += 1
	print(f"  Created root asset: Substation Security System ({security})")

	security_items = [
		("Perimeter CCTV System", "Security System", 60000, "In Use"),
		("Access Gate Control", "Access Control System", 40000, "In Use"),
		("Intrusion Detection", "Security System", 30000, "In Use")
	]

	for sec_name, cat, amount, stat in security_items:
		asset_id = create_asset(sec_name, cat, location, security, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {sec_name} ({asset_id}) under {security}")

	return assets_created


def create_nakuru_branch_assets(location, categories):
	"""Create assets for Branch Office Nakuru (15-20 assets)"""
	assets_created = 0

	# HVAC System (Root)
	hvac = create_asset("Branch HVAC System", "HVAC System", location, status="In Use", purchase_amount=200000)
	assets_created += 1
	print(f"  Created root asset: Branch HVAC System ({hvac})")

	# HVAC components
	hvac_items = [
		("Central Air Conditioning Unit", "HVAC System", 120000, "In Use"),
		("Ventilation System", "HVAC System", 50000, "In Use"),
		("Thermostat Control System", "HVAC System", 30000, "Under Maintenance")
	]

	for hvac_name, cat, amount, stat in hvac_items:
		asset_id = create_asset(hvac_name, cat, location, hvac, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {hvac_name} ({asset_id}) under {hvac}")

	# Office IT Equipment (Root)
	office_it = create_asset("Office IT Equipment", "IT Equipment", location, status="In Use", purchase_amount=180000)
	assets_created += 1
	print(f"  Created root asset: Office IT Equipment ({office_it})")

	# IT equipment
	it_items = [
		("File Server", "IT Equipment", 80000, "In Use"),
		("Network Switch", "Network Equipment", 40000, "In Use"),
		("WiFi Access Points", "Network Equipment", 30000, "In Use"),
		("UPS System", "Electrical System", 30000, "Available")
	]

	for it_name, cat, amount, stat in it_items:
		asset_id = create_asset(it_name, cat, location, office_it, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {it_name} ({asset_id}) under {office_it}")

	# Security System (Root)
	security = create_asset("Branch Security System", "Security System", location, status="In Use", purchase_amount=120000)
	assets_created += 1
	print(f"  Created root asset: Branch Security System ({security})")

	# Security components
	security_items = [
		("CCTV Camera System", "Security System", 50000, "In Use"),
		("Door Access Control", "Access Control System", 40000, "In Use"),
		("Alarm System", "Security System", 30000, "In Use")
	]

	for sec_name, cat, amount, stat in security_items:
		asset_id = create_asset(sec_name, cat, location, security, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {sec_name} ({asset_id}) under {security}")

	# Fire Safety System (Root)
	fire = create_asset("Fire Safety System", "Fire Safety System", location, status="In Use", purchase_amount=100000)
	assets_created += 1
	print(f"  Created root asset: Fire Safety System ({fire})")

	# Fire safety components
	fire_items = [
		("Fire Alarm Panel", "Fire Safety System", 40000, "In Use"),
		("Smoke Detectors", "Fire Safety System", 30000, "In Use"),
		("Fire Extinguisher System", "Fire Safety System", 30000, "Available")
	]

	for fire_name, cat, amount, stat in fire_items:
		asset_id = create_asset(fire_name, cat, location, fire, stat, amount)
		assets_created += 1
		print(f"  Created child asset: {fire_name} ({asset_id}) under {fire}")

	return assets_created

