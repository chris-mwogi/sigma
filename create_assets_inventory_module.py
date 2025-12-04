#!/usr/bin/env python3
"""
Restore the Assets & Inventory module with its 6 workspaces.
- Assets & Inventory
- Asset Management  
- Stock
- Settings
- Acquisition (Buying)
- Disposal (Selling)
"""

import os
import json
import shutil
from pathlib import Path

# Base paths
SIGMA_BASE = Path("/workspace/development/frappe-bench/apps/sigma/sigma")
BACKUP_DIR = Path("/workspace/development/frappe-bench/sites/prismod.localhost/public/files/workspace_backups/auto_fix")

# Module details
MODULE_NAME = "sigma_assets_inventory"
MODULE_DIR = SIGMA_BASE / MODULE_NAME

# Workspaces to restore
WORKSPACES = [
    "Assets_&_Inventory",
    "Asset_Management",
    "Stock",
    "Settings",
    "Acquisition_(Buying)",
    "Disposal_(Selling)"
]

print("=" * 60)
print("RESTORING ASSETS & INVENTORY MODULE")
print("=" * 60)

# Step 1: Create module directory structure
print("\n[1] Creating module directory structure...")
try:
    (MODULE_DIR / "config").mkdir(parents=True, exist_ok=True)
    (MODULE_DIR / "workspace").mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {MODULE_DIR}")
except Exception as e:
    print(f"✗ Error creating directories: {e}")
    exit(1)

# Step 2: Create __init__.py
print("[2] Creating __init__.py files...")
try:
    (MODULE_DIR / "__init__.py").write_text("")
    (MODULE_DIR / "config" / "__init__.py").write_text("")
    print("✓ Created __init__.py files")
except Exception as e:
    print(f"✗ Error creating __init__.py: {e}")
    exit(1)

# Step 3: Create module.txt
print("[3] Creating module.txt...")
try:
    (MODULE_DIR / "module.txt").write_text("Sigma Assets & Inventory")
    print("✓ Created module.txt")
except Exception as e:
    print(f"✗ Error creating module.txt: {e}")
    exit(1)

# Step 4: Create module.json
print("[4] Creating module.json...")
module_json = {
    "app_name": "sigma",
    "app_title": "Sigma",
    "app_publisher": "Frappe",
    "app_description": "Sigma Assets & Inventory Management",
    "app_icon": "octicon octicon-briefcase",
    "app_color": "#3498db",
    "app_order": 5,
    "hide_in_desk": True
}
try:
    (MODULE_DIR / "module.json").write_text(json.dumps(module_json, indent=2))
    print("✓ Created module.json")
except Exception as e:
    print(f"✗ Error creating module.json: {e}")
    exit(1)

# Step 5: Copy workspace files
print("[5] Copying workspace files from backups...")
workspace_map = {}
for workspace_name in WORKSPACES:
    backup_file = BACKUP_DIR / f"{workspace_name}.json"
    if not backup_file.exists():
        print(f"  ⚠ Warning: Backup not found for {workspace_name}")
        continue
    
    # Create workspace directory
    workspace_dir = MODULE_DIR / "workspace" / workspace_name.lower()
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy JSON file
    dest_file = workspace_dir / f"{workspace_name.lower()}.json"
    shutil.copy(backup_file, dest_file)
    
    # Convert name to proper format for database (e.g., "Assets_&_Inventory" -> "Assets & Inventory")
    display_name = workspace_name.replace("_", " ")
    workspace_map[display_name] = workspace_name.lower()
    
    print(f"  ✓ Copied {workspace_name} → {dest_file.name}")

# Step 6: Create desktop.py with sidebar configuration
print("[6] Creating config/desktop.py for sidebar...")
desktop_py = '''from frappe import _

def get_data():
    return [
        {
            "module_name": "Sigma Assets & Inventory",
            "color": "#E8A87C",
            "icon": "boxes",
            "type": "module",
            "label": _("📊 Assets & Inventory")
        }
    ]
'''
try:
    (MODULE_DIR / "config" / "desktop.py").write_text(desktop_py)
    print("✓ Created config/desktop.py")
except Exception as e:
    print(f"✗ Error creating desktop.py: {e}")
    exit(1)

# Step 7: Summary
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"\n✓ Module created: {MODULE_DIR}")
print(f"✓ Workspaces restored: {len(workspace_map)}")
for display_name, internal_name in workspace_map.items():
    print(f"  - {display_name}")

print(f"\n✓ Sidebar icon: boxes (📦)")
print(f"✓ Sidebar label: 📊 Assets & Inventory")
print(f"✓ Sidebar color: #E8A87C (tan/brown)")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Add 'Sigma Assets & Inventory' to sigma/modules.txt")
print("2. Run: bench --site prismod.localhost migrate")
print("3. Refresh browser to see new workspace module in sidebar")
print("=" * 60)
