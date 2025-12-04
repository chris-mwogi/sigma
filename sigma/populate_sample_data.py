#!/usr/bin/env python3
"""
Script to populate Sigma app with sample asset acquisition and disposal data
Run with: bench --site prismod.localhost execute populate_sample_data.main
"""
import frappe
from datetime import datetime, timedelta

def main():
    """Main function to populate sample data"""
    print("=" * 60)
    print("Populating Sigma App with Sample Asset Data")
    print("=" * 60)

    company = "Kenya Power and Lighting Company PLC"

    # Create sample items first
    print("\n0. Creating sample items...")
    items = [
        'Laptop Dell XPS 15',
        'Security Camera System',
        'Office Desk',
        'Server Rack',
        'Network Switch',
    ]

    for item_name in items:
        if not frappe.db.exists('Item', item_name):
            item = frappe.new_doc('Item')
            item.item_code = item_name
            item.item_name = item_name
            item.item_group = 'All Item Groups'
            item.stock_uom = 'Nos'
            item.insert(ignore_permissions=True)
            print(f"✅ Created item: {item_name}")
        else:
            print(f"⏭️  Item already exists: {item_name}")

    # Create sample suppliers
    print("\n1. Creating sample suppliers...")
    suppliers = [
        {'name': 'Tech Solutions Ltd', 'supplier_name': 'Tech Solutions Ltd'},
        {'name': 'Security Systems Inc', 'supplier_name': 'Security Systems Inc'},
        {'name': 'Office Equipment Co', 'supplier_name': 'Office Equipment Co'},
    ]

    for supplier_data in suppliers:
        if not frappe.db.exists('Supplier', supplier_data['name']):
            supplier = frappe.new_doc('Supplier')
            supplier.supplier_name = supplier_data['supplier_name']
            supplier.supplier_type = 'Company'
            supplier.insert(ignore_permissions=True)
            print(f"✅ Created supplier: {supplier_data['name']}")
        else:
            print(f"⏭️  Supplier already exists: {supplier_data['name']}")

    # Create sample customers
    print("\n2. Creating sample customers...")
    customers = [
        {'name': 'Buyer Corp', 'customer_name': 'Buyer Corp'},
        {'name': 'Asset Resellers Ltd', 'customer_name': 'Asset Resellers Ltd'},
        {'name': 'Tech Recyclers', 'customer_name': 'Tech Recyclers'},
    ]

    for customer_data in customers:
        if not frappe.db.exists('Customer', customer_data['name']):
            customer = frappe.new_doc('Customer')
            customer.customer_name = customer_data['customer_name']
            customer.customer_type = 'Company'
            customer.insert(ignore_permissions=True)
            print(f"✅ Created customer: {customer_data['name']}")
        else:
            print(f"⏭️  Customer already exists: {customer_data['name']}")

    # Create sample purchase invoices
    print("\n3. Creating sample purchase invoices (asset acquisitions)...")
    base_date = datetime.now() - timedelta(days=180)

    purchases = [
        {'item': 'Laptop Dell XPS 15', 'qty': 5, 'rate': 1500, 'supplier': 'Tech Solutions Ltd'},
        {'item': 'Security Camera System', 'qty': 10, 'rate': 800, 'supplier': 'Security Systems Inc'},
        {'item': 'Office Desk', 'qty': 20, 'rate': 300, 'supplier': 'Office Equipment Co'},
        {'item': 'Server Rack', 'qty': 2, 'rate': 5000, 'supplier': 'Tech Solutions Ltd'},
        {'item': 'Network Switch', 'qty': 3, 'rate': 2000, 'supplier': 'Tech Solutions Ltd'},
    ]

    for idx, purchase_data in enumerate(purchases):
        pi_name = f"PI-ASSET-{idx+1:03d}"
        if not frappe.db.exists('Purchase Invoice', pi_name):
            pi = frappe.new_doc('Purchase Invoice')
            pi.name = pi_name
            pi.supplier = purchase_data['supplier']
            pi.posting_date = (base_date + timedelta(days=idx*30)).date()
            pi.company = company

            pi.append('items', {
                'item_code': purchase_data['item'],
                'item_name': purchase_data['item'],
                'qty': purchase_data['qty'],
                'rate': purchase_data['rate'],
                'amount': purchase_data['qty'] * purchase_data['rate'],
            })

            pi.insert(ignore_permissions=True)
            print(f"✅ Created: {pi_name} - {purchase_data['item']} ({purchase_data['qty']} units @ {purchase_data['rate']})")
        else:
            print(f"⏭️  Already exists: {pi_name}")

    # Create sample sales invoices
    print("\n4. Creating sample sales invoices (asset disposals)...")
    base_date = datetime.now() - timedelta(days=90)

    sales = [
        {'item': 'Laptop Dell XPS 15', 'qty': 2, 'rate': 1000, 'customer': 'Buyer Corp'},
        {'item': 'Security Camera System', 'qty': 3, 'rate': 500, 'customer': 'Asset Resellers Ltd'},
        {'item': 'Office Desk', 'qty': 5, 'rate': 150, 'customer': 'Tech Recyclers'},
        {'item': 'Network Switch', 'qty': 1, 'rate': 1200, 'customer': 'Buyer Corp'},
    ]

    for idx, sale_data in enumerate(sales):
        si_name = f"SI-ASSET-{idx+1:03d}"
        if not frappe.db.exists('Sales Invoice', si_name):
            si = frappe.new_doc('Sales Invoice')
            si.name = si_name
            si.customer = sale_data['customer']
            si.posting_date = (base_date + timedelta(days=idx*20)).date()
            si.company = company

            si.append('items', {
                'item_code': sale_data['item'],
                'item_name': sale_data['item'],
                'qty': sale_data['qty'],
                'rate': sale_data['rate'],
                'amount': sale_data['qty'] * sale_data['rate'],
            })

            si.insert(ignore_permissions=True)
            print(f"✅ Created: {si_name} - {sale_data['item']} ({sale_data['qty']} units @ {sale_data['rate']})")
        else:
            print(f"⏭️  Already exists: {si_name}")

    print("\n" + "=" * 60)
    print("✅ Sample data population completed successfully!")
    print("=" * 60)

