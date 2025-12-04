#!/usr/bin/env python3
"""
Rename and populate Buying and Selling workspaces for asset acquisition and disposal
"""
import frappe

def rename_and_populate_buying_workspace():
    """Rename Buying to Acquisition (Buying) and populate with content"""
    print("\n" + "=" * 70)
    print("RENAMING AND POPULATING BUYING WORKSPACE")
    print("=" * 70)

    # Get the existing Buying workspace
    if not frappe.db.exists('Workspace', 'Buying'):
        print("❌ Buying workspace does not exist")
        return

    old_name = 'Buying'
    new_name = 'Acquisition (Buying)'

    print(f"\nRenaming: {old_name} → {new_name}")

    # Rename the workspace using Frappe's rename_doc method
    frappe.rename_doc('Workspace', old_name, new_name)

    # Now get the renamed workspace
    ws = frappe.get_doc('Workspace', new_name)

    # Update the title
    ws.title = new_name

    # Clear existing content
    ws.shortcuts = []
    ws.links = []

    # Add shortcuts for acquisition/buying
    shortcuts_data = [
        {'label': 'New Purchase Order', 'link_to': 'Purchase Order', 'icon': 'octicon octicon-plus'},
        {'label': 'New Purchase Invoice', 'link_to': 'Purchase Invoice', 'icon': 'octicon octicon-plus'},
        {'label': 'New Item', 'link_to': 'Item', 'icon': 'octicon octicon-plus'},
        {'label': 'New Supplier', 'link_to': 'Supplier', 'icon': 'octicon octicon-plus'},
    ]

    for shortcut in shortcuts_data:
        ws.append('shortcuts', {
            'label': shortcut['label'],
            'link_to': shortcut['link_to'],
            'icon': shortcut['icon']
        })

    # Add links for acquisition/buying
    links_data = [
        {'label': 'Purchase Orders', 'link_to': 'Purchase Order'},
        {'label': 'Purchase Invoices', 'link_to': 'Purchase Invoice'},
        {'label': 'Items', 'link_to': 'Item'},
        {'label': 'Suppliers', 'link_to': 'Supplier'},
        {'label': 'Assets', 'link_to': 'Asset'},
        {'label': 'Purchase Receipts', 'link_to': 'Purchase Receipt'},
    ]

    for link in links_data:
        ws.append('links', {
            'label': link['label'],
            'link_to': link['link_to']
        })

    # Save the workspace
    ws.save(ignore_permissions=True)

    print(f"✅ Workspace renamed to: {new_name}")
    print(f"   - Shortcuts: {len(ws.shortcuts)}")
    print(f"   - Links: {len(ws.links)}")


def rename_and_populate_selling_workspace():
    """Rename Selling to Disposal (Selling) and populate with content"""
    print("\n" + "=" * 70)
    print("RENAMING AND POPULATING SELLING WORKSPACE")
    print("=" * 70)

    # Get the existing Selling workspace
    if not frappe.db.exists('Workspace', 'Selling'):
        print("❌ Selling workspace does not exist")
        return

    old_name = 'Selling'
    new_name = 'Disposal (Selling)'

    print(f"\nRenaming: {old_name} → {new_name}")

    # Rename the workspace using Frappe's rename_doc method
    frappe.rename_doc('Workspace', old_name, new_name)

    # Now get the renamed workspace
    ws = frappe.get_doc('Workspace', new_name)

    # Update the title
    ws.title = new_name

    # Clear existing content
    ws.shortcuts = []
    ws.links = []

    # Add shortcuts for disposal/selling
    shortcuts_data = [
        {'label': 'New Sales Order', 'link_to': 'Sales Order', 'icon': 'octicon octicon-plus'},
        {'label': 'New Sales Invoice', 'link_to': 'Sales Invoice', 'icon': 'octicon octicon-plus'},
        {'label': 'New Customer', 'link_to': 'Customer', 'icon': 'octicon octicon-plus'},
        {'label': 'New Item', 'link_to': 'Item', 'icon': 'octicon octicon-plus'},
    ]

    for shortcut in shortcuts_data:
        ws.append('shortcuts', {
            'label': shortcut['label'],
            'link_to': shortcut['link_to'],
            'icon': shortcut['icon']
        })

    # Add links for disposal/selling
    links_data = [
        {'label': 'Sales Orders', 'link_to': 'Sales Order'},
        {'label': 'Sales Invoices', 'link_to': 'Sales Invoice'},
        {'label': 'Customers', 'link_to': 'Customer'},
        {'label': 'Items', 'link_to': 'Item'},
        {'label': 'Delivery Notes', 'link_to': 'Delivery Note'},
        {'label': 'Asset Disposals', 'link_to': 'Asset'},
    ]

    for link in links_data:
        ws.append('links', {
            'label': link['label'],
            'link_to': link['link_to']
        })

    # Save the workspace
    ws.save(ignore_permissions=True)

    print(f"✅ Workspace renamed to: {new_name}")
    print(f"   - Shortcuts: {len(ws.shortcuts)}")
    print(f"   - Links: {len(ws.links)}")


def main():
    """Main function to rename and populate both workspaces"""
    print("\n" + "=" * 70)
    print("BUYING AND SELLING WORKSPACES RENAME AND POPULATE SCRIPT")
    print("=" * 70)
    
    try:
        rename_and_populate_buying_workspace()
        rename_and_populate_selling_workspace()
        
        print("\n" + "=" * 70)
        print("✅ ALL WORKSPACES RENAMED AND POPULATED SUCCESSFULLY")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

