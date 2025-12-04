import frappe
import os
import json


def execute():
    """
    Verify the sigma and sigma_home module merge.
    """
    
    results = {
        'filesystem': {
            'sigma_exists': False,
            'sigma_home_exists': False,
            'sigma_contents': [],
            'workspace_files': []
        },
        'database': {
            'sigma_module_exists': False,
            'sigma_home_module_exists': False,
            'workspaces_in_sigma': [],
            'workspaces_in_sigma_home': []
        },
        'summary': '',
        'errors': []
    }
    
    base_path = '/workspace/development/frappe-bench/apps/sigma/sigma'
    
    # Check filesystem
    sigma_path = os.path.join(base_path, 'sigma')
    sigma_home_path = os.path.join(base_path, 'sigma_home')
    
    if os.path.exists(sigma_path):
        results['filesystem']['sigma_exists'] = True
        results['filesystem']['sigma_contents'] = os.listdir(sigma_path)
        
        # Check for workspace files
        workspace_dir = os.path.join(sigma_path, 'workspace')
        if os.path.exists(workspace_dir):
            for item in os.listdir(workspace_dir):
                item_path = os.path.join(workspace_dir, item)
                if os.path.isdir(item_path):
                    json_file = os.path.join(item_path, f'{item}.json')
                    if os.path.exists(json_file):
                        results['filesystem']['workspace_files'].append(item)
    
    if os.path.exists(sigma_home_path):
        results['filesystem']['sigma_home_exists'] = True
    
    # Check database
    try:
        if frappe.db.exists('Module Def', 'Sigma'):
            results['database']['sigma_module_exists'] = True
        
        if frappe.db.exists('Module Def', 'sigma_home'):
            results['database']['sigma_home_module_exists'] = True
        
        # Get workspaces in Sigma module
        sigma_ws = frappe.db.sql(
            "SELECT name FROM `tabWorkspace` WHERE module = 'Sigma' ORDER BY name",
            as_dict=False
        )
        results['database']['workspaces_in_sigma'] = [ws[0] for ws in sigma_ws]
        
        # Get workspaces in sigma_home module
        sigma_home_ws = frappe.db.sql(
            "SELECT name FROM `tabWorkspace` WHERE module = 'sigma_home' ORDER BY name",
            as_dict=False
        )
        results['database']['workspaces_in_sigma_home'] = [ws[0] for ws in sigma_home_ws]
    
    except Exception as e:
        results['errors'].append(str(e))
    
    # Generate summary
    if not results['filesystem']['sigma_home_exists'] and \
       results['database']['sigma_module_exists'] and \
       not results['database']['sigma_home_module_exists'] and \
       len(results['database']['workspaces_in_sigma']) > 0:
        results['summary'] = "✅ MERGE SUCCESSFUL: sigma_home fully merged into sigma"
    else:
        results['summary'] = "⚠️ Merge status needs review"
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
