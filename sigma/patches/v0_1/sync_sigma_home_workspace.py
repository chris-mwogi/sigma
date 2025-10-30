"""
Patch: Sync Sigma Home Workspace from fixture file
Description: Ensures the Sigma Home workspace is properly synced with all links and shortcuts
"""

import frappe
import json
import os


def execute():
    """Execute the patch to sync Sigma Home workspace"""

    print("\n" + "="*70)
    print("SYNCING SIGMA HOME WORKSPACE FROM FIXTURE FILE")
    print("="*70)

    # Path to the fixture file
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "../../fixtures/workspace_sigma_home.json"
    )

    # Resolve the absolute path
    fixture_path = os.path.abspath(fixture_path)

    print(f"\nFixture File: {fixture_path}")
    print(f"File exists: {os.path.exists(fixture_path)}")

    if not os.path.exists(fixture_path):
        print("❌ Fixture file not found, skipping patch")
        return

    # Read the fixture file
    with open(fixture_path, 'r') as f:
        fixture_data = json.load(f)

    if not isinstance(fixture_data, list) or len(fixture_data) == 0:
        print("❌ Invalid fixture file format")
        return

    workspace_data = fixture_data[0]

    print(f"\nLoading workspace from fixture...")
    print(f"  Name: {workspace_data.get('name')}")
    print(f"  Title: {workspace_data.get('title')}")
    print(f"  Links: {len(workspace_data.get('links', []))}")
    print(f"  Shortcuts: {len(workspace_data.get('shortcuts', []))}")

    # Check current state
    try:
        current_ws = frappe.get_doc("Workspace", "Sigma Home")
        current_links = len(current_ws.links)
        print(f"\nCurrent workspace state:")
        print(f"  Links in database: {current_links}")

        if current_links == 18:
            print(f"  ✅ Workspace already properly synced, skipping")
            return
    except:
        pass

    # Delete the existing workspace
    print(f"\nDeleting existing workspace from database...")
    try:
        frappe.delete_doc("Workspace", "Sigma Home")
        frappe.db.commit()
        print("✅ Workspace deleted")
    except Exception as e:
        print(f"⚠️  Could not delete: {e}")

    # Create new workspace from fixture
    print(f"\nCreating workspace from fixture...")
    try:
        workspace = frappe.get_doc(workspace_data)
        workspace.insert()
        frappe.db.commit()
        print("✅ Workspace created from fixture")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    # Verify
    print(f"\n" + "="*70)
    print("VERIFICATION")
    print("="*70)

    workspace = frappe.get_doc("Workspace", "Sigma Home")
    print(f"\n✅ Sigma Home workspace synced")
    print(f"   Total Links: {len(workspace.links)}")
    print(f"   Total Shortcuts: {len(workspace.shortcuts)}")

    if len(workspace.links) == 18 and len(workspace.shortcuts) == 6:
        print(f"\n✅ SUCCESS: Workspace properly synced")
    else:
        print(f"\n⚠️  Expected 18 links and 6 shortcuts")

