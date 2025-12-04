#!/usr/bin/env python3
"""
Clear shortcuts and links tables from workspaces to force rendering of content field.

This script clears the shortcuts and links child tables from workspaces that have
a populated content field. This ensures that the frontend renders the content field
using Editor.js instead of rendering the shortcuts and links tables.
"""

import frappe
import json


def main():
    print("\n" + "=" * 70)
    print("CLEARING WORKSPACE SHORTCUTS AND LINKS TABLES")
    print("=" * 70)

    workspaces_to_fix = [
        'Sigma',
        'Risk Assessment',
        'Assets & Inventory',
        'Acquisition (Buying)',
        'Disposal (Selling)'
    ]

    for ws_name in workspaces_to_fix:
        print(f"\nProcessing: {ws_name}")
        print("-" * 70)

        if not frappe.db.exists('Workspace', ws_name):
            print(f"❌ Workspace does not exist")
            continue

        ws = frappe.get_doc('Workspace', ws_name)

        # Check if content field is populated
        if not ws.content:
            print(f"❌ Content field is empty, skipping")
            continue

        # Parse content to verify it's valid JSON
        try:
            content = json.loads(ws.content)
            print(f"✅ Content field is valid JSON with {len(content)} items")
        except Exception as e:
            print(f"❌ Content field is not valid JSON: {e}")
            continue

        # Clear shortcuts table
        shortcuts_count = len(ws.shortcuts)
        if shortcuts_count > 0:
            ws.shortcuts = []
            print(f"✅ Cleared {shortcuts_count} shortcuts")

        # Clear links table
        links_count = len(ws.links)
        if links_count > 0:
            ws.links = []
            print(f"✅ Cleared {links_count} links")

        # Save the workspace
        try:
            ws.save()
            print(f"✅ Workspace saved successfully")
        except Exception as e:
            print(f"❌ Error saving workspace: {e}")
            continue

    print("\n" + "=" * 70)
    print("✅ CLEARING COMPLETE")
    print("=" * 70)

    # Clear cache
    print("\nClearing cache...")
    frappe.cache.clear()
    print("✅ Cache cleared")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

