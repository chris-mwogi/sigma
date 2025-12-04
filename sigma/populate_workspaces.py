#!/usr/bin/env python3
"""
Populate Sigma workspaces with content, shortcuts, links, and cards
"""
import frappe
import json

def populate_sigma_home_workspace():
    """Populate Sigma workspace with shortcuts and links"""
    print("\n" + "=" * 70)
    print("POPULATING SIGMA WORKSPACE")
    print("=" * 70)

    ws = frappe.get_doc('Workspace', 'Sigma')

    # Clear existing content
    ws.shortcuts = []
    ws.links = []

    # Add shortcuts
    shortcuts_data = [
        {'label': 'New Case', 'link_to': 'Case', 'icon': 'octicon octicon-plus'},
        {'label': 'New Incident', 'link_to': 'Incident Report', 'icon': 'octicon octicon-plus'},
        {'label': 'New Access Event', 'link_to': 'Access Event', 'icon': 'octicon octicon-plus'},
        {'label': 'New Guard Shift', 'link_to': 'Guard Shift', 'icon': 'octicon octicon-plus'},
    ]

    for shortcut in shortcuts_data:
        ws.append('shortcuts', {
            'label': shortcut['label'],
            'link_to': shortcut['link_to'],
            'icon': shortcut['icon']
        })

    # Add links
    links_data = [
        {'label': 'Cases', 'link_to': 'Case'},
        {'label': 'Incident Reports', 'link_to': 'Incident Report'},
        {'label': 'Access Events', 'link_to': 'Access Event'},
        {'label': 'Guard Shifts', 'link_to': 'Guard Shift'},
        {'label': 'Assets', 'link_to': 'Asset'},
        {'label': 'Risk Assessments', 'link_to': 'Risk Assessment'},
    ]

    for link in links_data:
        ws.append('links', {
            'label': link['label'],
            'link_to': link['link_to']
        })

    ws.save(ignore_permissions=True)
    print(f"✅ Sigma workspace populated")
    print(f"   - Shortcuts: {len(ws.shortcuts)}")
    print(f"   - Links: {len(ws.links)}")


def populate_risk_assessment_workspace():
    """Populate Risk Assessment workspace with content"""
    print("\n" + "=" * 70)
    print("POPULATING RISK ASSESSMENT WORKSPACE")
    print("=" * 70)

    ws = frappe.get_doc('Workspace', 'Risk Assessment')

    # Clear existing content
    ws.shortcuts = []
    ws.links = []

    # Add shortcuts
    shortcuts_data = [
        {'label': 'New Risk Assessment', 'link_to': 'Risk Assessment', 'icon': 'octicon octicon-plus'},
        {'label': 'New Risk Mitigation', 'link_to': 'Risk Mitigation Action', 'icon': 'octicon octicon-plus'},
    ]

    for shortcut in shortcuts_data:
        ws.append('shortcuts', {
            'label': shortcut['label'],
            'link_to': shortcut['link_to'],
            'icon': shortcut['icon']
        })

    # Add links
    links_data = [
        {'label': 'Risk Assessments', 'link_to': 'Risk Assessment'},
        {'label': 'Risk Mitigation Actions', 'link_to': 'Risk Mitigation Action'},
    ]

    for link in links_data:
        ws.append('links', {
            'label': link['label'],
            'link_to': link['link_to']
        })

    ws.save(ignore_permissions=True)
    print(f"✅ Risk Assessment workspace populated")
    print(f"   - Shortcuts: {len(ws.shortcuts)}")
    print(f"   - Links: {len(ws.links)}")


def populate_assets_inventory_workspace():
    """Populate Assets & Inventory workspace with content"""
    print("\n" + "=" * 70)
    print("POPULATING ASSETS & INVENTORY WORKSPACE")
    print("=" * 70)

    if not frappe.db.exists('Workspace', 'Assets & Inventory'):
        print("⚠️ Assets & Inventory workspace does not exist")
        return

    ws = frappe.get_doc('Workspace', 'Assets & Inventory')

    # Clear existing content
    ws.shortcuts = []
    ws.links = []

    # Add shortcuts
    shortcuts_data = [
        {'label': 'New Item', 'link_to': 'Item', 'icon': 'octicon octicon-plus'},
        {'label': 'New Asset', 'link_to': 'Asset', 'icon': 'octicon octicon-plus'},
        {'label': 'New Purchase Invoice', 'link_to': 'Purchase Invoice', 'icon': 'octicon octicon-plus'},
        {'label': 'New Sales Invoice', 'link_to': 'Sales Invoice', 'icon': 'octicon octicon-plus'},
    ]

    for shortcut in shortcuts_data:
        ws.append('shortcuts', {
            'label': shortcut['label'],
            'link_to': shortcut['link_to'],
            'icon': shortcut['icon']
        })

    # Add links
    links_data = [
        {'label': 'Items', 'link_to': 'Item'},
        {'label': 'Assets', 'link_to': 'Asset'},
        {'label': 'Purchase Invoices', 'link_to': 'Purchase Invoice'},
        {'label': 'Sales Invoices', 'link_to': 'Sales Invoice'},
        {'label': 'Suppliers', 'link_to': 'Supplier'},
        {'label': 'Customers', 'link_to': 'Customer'},
    ]

    for link in links_data:
        ws.append('links', {
            'label': link['label'],
            'link_to': link['link_to']
        })

    ws.save(ignore_permissions=True)
    print(f"✅ Assets & Inventory workspace populated")
    print(f"   - Shortcuts: {len(ws.shortcuts)}")
    print(f"   - Links: {len(ws.links)}")


def main():
    """Main function to populate all workspaces"""
    print("\n" + "=" * 70)
    print("SIGMA WORKSPACE POPULATION SCRIPT")
    print("=" * 70)
    
    try:
        populate_sigma_home_workspace()
        populate_risk_assessment_workspace()
        populate_assets_inventory_workspace()
        
        print("\n" + "=" * 70)
        print("✅ ALL WORKSPACES POPULATED SUCCESSFULLY")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

