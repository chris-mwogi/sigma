import frappe
import json


def execute():
    """
    Register new sigma_* modules in the database and assign workspaces to them.
    """
    
    results = {
        'created_modules': [],
        'assigned_workspaces': [],
        'errors': []
    }
    
    # Modules to create and their workspace assignments
    modules_to_create = [
        {
            'name': 'Sigma CRM',
            'workspace': 'CRM'
        },
        {
            'name': 'Sigma Helpdesk',
            'workspace': 'Helpdesk'
        },
        {
            'name': 'Sigma Projects',
            'workspace': 'Projects'
        },
        {
            'name': 'Sigma Quality',
            'workspace': 'Quality'
        },
        {
            'name': 'Sigma Support',
            'workspace': 'Support'
        },
        {
            'name': 'Sigma Telephony',
            'workspace': 'Telephony'
        }
    ]
    
    # Create modules
    for module_info in modules_to_create:
        try:
            module_name = module_info['name']
            workspace_name = module_info['workspace']
            
            # Check if module already exists
            if frappe.db.exists('Module Def', module_name):
                results['created_modules'].append({
                    'name': module_name,
                    'status': 'already_exists'
                })
            else:
                # Create new Module Def
                module_doc = frappe.new_doc('Module Def')
                module_doc.module_name = module_name
                module_doc.app_name = 'sigma'
                module_doc.category = 'Modules'
                module_doc.insert(ignore_permissions=True)
                
                results['created_modules'].append({
                    'name': module_name,
                    'status': 'created'
                })
            
            # Assign workspace to module
            if frappe.db.exists('Workspace', workspace_name):
                frappe.db.set_value('Workspace', workspace_name, 'module', module_name)
                results['assigned_workspaces'].append({
                    'workspace': workspace_name,
                    'module': module_name,
                    'status': 'assigned'
                })
            else:
                results['errors'].append({
                    'workspace': workspace_name,
                    'error': 'Workspace not found'
                })
        
        except Exception as e:
            results['errors'].append({
                'module': module_info['name'],
                'error': str(e)
            })
    
    frappe.db.commit()
    
    results['summary'] = f"Created/verified {len(results['created_modules'])} modules. Assigned {len(results['assigned_workspaces'])} workspaces. {len(results['errors'])} errors."
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
