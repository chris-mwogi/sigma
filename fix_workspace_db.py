#!/usr/bin/env python3
"""
Fix workspace records in the database by removing null link_type and link_to values.
This script should be run via bench console.
"""

import frappe

def fix_workspace_links():
    """Fix all workspace link records with null values."""
    
    print("\n" + "=" * 80)
    print("Fixing Workspace Links in Database")
    print("=" * 80 + "\n")
    
    # Get all workspace links
    links = frappe.get_all(
        "Workspace Link",
        fields=["name", "parent", "label", "type", "link_type", "link_to"],
        filters={"type": "Card Break"}
    )
    
    print(f"Found {len(links)} Card Break type links\n")
    
    fixed_count = 0
    for link in links:
        needs_fix = False
        updates = {}
        
        # Check if link_type or link_to is null
        if link.get("link_type") is not None:
            updates["link_type"] = None
            needs_fix = True
            print(f"  - Workspace: {link['parent']}")
            print(f"    Link: {link['label']}")
            print(f"    Clearing link_type: {link['link_type']} -> None")
        
        if link.get("link_to") is not None:
            updates["link_to"] = None
            needs_fix = True
            if not updates.get("link_type"):
                print(f"  - Workspace: {link['parent']}")
                print(f"    Link: {link['label']}")
            print(f"    Clearing link_to: {link['link_to']} -> None")
        
        if needs_fix:
            # Update the link
            frappe.db.set_value("Workspace Link", link["name"], updates)
            fixed_count += 1
            print(f"    ✓ Fixed\n")
    
    if fixed_count > 0:
        frappe.db.commit()
        print("=" * 80)
        print(f"✓ Fixed {fixed_count} workspace links")
        print("=" * 80 + "\n")
        print("Please clear cache and reload the page:")
        print("  bench --site sigma.localhost clear-cache")
    else:
        print("=" * 80)
        print("No workspace links needed fixing")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    # This script should be run via bench console
    print("This script should be run via bench console:")
    print("  bench --site sigma.localhost console")
    print("  >>> exec(open('apps/sigma/fix_workspace_db.py').read())")
    print("  >>> fix_workspace_links()")

