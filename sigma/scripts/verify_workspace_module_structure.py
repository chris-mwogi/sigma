import os
import json
import frappe


def execute():
    """
    Final verification of the new workspace module structure.
    """
    
    results = {
        'filesystem': {
            'modules_created': [],
            'workspace_files': [],
            'errors': []
        },
        'database': {
            'modules_registered': [],
            'workspaces_assigned': [],
            'errors': []
        },
        'summary': ''
    }
    
    base_path = '/workspace/development/frappe-bench/apps/sigma/sigma'
    
    # Check filesystem
    workspace_modules = [
        'sigma_crm',
        'sigma_helpdesk',
        'sigma_projects',
        'sigma_quality',
        'sigma_support',
        'sigma_telephony'
    ]
    
    for module_name in workspace_modules:
        module_path = os.path.join(base_path, module_name)
        
        if os.path.exists(module_path):
            results['filesystem']['modules_created'].append({
                'module': module_name,
                'path': module_path,
                'exists': True
            })
            
            # Check for workspace files
            workspace_dir = os.path.join(module_path, 'workspace')
            if os.path.exists(workspace_dir):
                for ws_name in os.listdir(workspace_dir):
                    ws_path = os.path.join(workspace_dir, ws_name)
                    if os.path.isdir(ws_path):
                        json_file = os.path.join(ws_path, f'{ws_name}.json')
                        if os.path.exists(json_file):
                            file_size = os.path.getsize(json_file)
                            results['filesystem']['workspace_files'].append({
                                'module': module_name,
                                'workspace': ws_name,
                                'file': json_file,
                                'size_bytes': file_size
                            })
        else:
            results['filesystem']['errors'].append({
                'module': module_name,
                'error': 'Module directory not found'
            })
    
    # Check database
    module_mapping = {
        'Sigma CRM': 'CRM',
        'Sigma Helpdesk': 'Helpdesk',
        'Sigma Projects': 'Projects',
        'Sigma Quality': 'Quality',
        'Sigma Support': 'Support',
        'Sigma Telephony': 'Telephony'
    }
    
    for module_name, workspace_name in module_mapping.items():
        # Check module exists
        if frappe.db.exists('Module Def', module_name):
            results['database']['modules_registered'].append({
                'module': module_name,
                'exists': True
            })
        else:
            results['database']['errors'].append({
                'module': module_name,
                'error': 'Module not found in database'
            })
        
        # Check workspace assignment
        if frappe.db.exists('Workspace', workspace_name):
            assigned_module = frappe.db.get_value('Workspace', workspace_name, 'module')
            results['database']['workspaces_assigned'].append({
                'workspace': workspace_name,
                'assigned_to_module': assigned_module
            })
        else:
            results['database']['errors'].append({
                'workspace': workspace_name,
                'error': 'Workspace not found in database'
            })
    
    # Generate summary
    fs_modules = len(results['filesystem']['modules_created'])
    fs_files = len(results['filesystem']['workspace_files'])
    db_modules = len(results['database']['modules_registered'])
    db_workspaces = len(results['database']['workspaces_assigned'])
    total_errors = len(results['filesystem']['errors']) + len(results['database']['errors'])
    
    results['summary'] = f"""
✅ Filesystem Structure:
   - {fs_modules} workspace modules created
   - {fs_files} workspace JSON files copied

✅ Database Structure:
   - {db_modules} modules registered
   - {db_workspaces} workspaces assigned to modules
   
📊 Total: {total_errors} errors (0 = perfect!)
"""
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
