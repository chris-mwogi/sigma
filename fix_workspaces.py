#!/usr/bin/env python3
"""
Fix workspace JSON files by removing null link_type and link_to values
from Card Break type links.
"""

import json
import os
from pathlib import Path

def fix_workspace_file(filepath):
    """Fix a single workspace JSON file."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Handle both single workspace object and array of workspaces
    workspaces = data if isinstance(data, list) else [data]
    
    fixed = False
    for workspace in workspaces:
        if 'links' not in workspace:
            continue
            
        for link in workspace['links']:
            # Fix Card Break type links with null values
            if link.get('type') == 'Card Break':
                # Remove link_type and link_to if they're null
                if 'link_type' in link and link['link_type'] is None:
                    del link['link_type']
                    fixed = True
                    print(f"  - Removed null link_type from '{link.get('label', 'Unknown')}'")
                
                if 'link_to' in link and link['link_to'] is None:
                    del link['link_to']
                    fixed = True
                    print(f"  - Removed null link_to from '{link.get('label', 'Unknown')}'")
    
    if fixed:
        # Write back with proper formatting
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=1)
        print(f"  ✓ Fixed: {filepath}")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    """Find and fix all workspace JSON files in the sigma app."""
    sigma_dir = Path(__file__).parent / 'sigma'
    
    # Find all workspace JSON files
    workspace_files = []
    
    # Check fixtures directory
    fixtures_dir = sigma_dir / 'fixtures'
    if fixtures_dir.exists():
        workspace_files.extend(fixtures_dir.glob('workspace_*.json'))
    
    # Check all module workspace directories
    for module_dir in sigma_dir.iterdir():
        if module_dir.is_dir() and module_dir.name.startswith('sigma_'):
            workspace_dir = module_dir / 'workspace'
            if workspace_dir.exists():
                workspace_files.extend(workspace_dir.rglob('*.json'))
    
    print(f"\nFound {len(workspace_files)} workspace files to check\n")
    print("=" * 80)
    
    fixed_count = 0
    for filepath in workspace_files:
        if fix_workspace_file(filepath):
            fixed_count += 1
        print()
    
    print("=" * 80)
    print(f"\nSummary: Fixed {fixed_count} out of {len(workspace_files)} workspace files")

if __name__ == '__main__':
    main()

