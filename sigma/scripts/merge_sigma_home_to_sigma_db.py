import frappe
import json


def execute():
    """
    Update database after merging sigma_home to sigma:
    1. Delete Sigma Home module def
    2. Reassign Home and Sigma Home workspaces to Sigma module
    """
    
    results = {
        'deleted_modules': [],
        'reassigned_workspaces': [],
        'errors': []
    }
    
    try:
        # Delete sigma_home module definition
        if frappe.db.exists('Module Def', 'sigma_home'):
            try:
                frappe.delete_doc('Module Def', 'sigma_home', force=True, ignore_permissions=True)
                results['deleted_modules'].append({
                    'module': 'sigma_home',
                    'status': 'deleted'
                })
            except Exception as e:
                results['errors'].append({
                    'module': 'sigma_home',
                    'error': str(e)
                })
        
        # Reassign workspaces from sigma_home to Sigma
        workspaces_to_reassign = ['Home', 'Sigma Home']
        
        for ws_name in workspaces_to_reassign:
            try:
                if frappe.db.exists('Workspace', ws_name):
                    frappe.db.set_value('Workspace', ws_name, 'module', 'Sigma')
                    results['reassigned_workspaces'].append({
                        'workspace': ws_name,
                        'from_module': 'sigma_home',
                        'to_module': 'Sigma',
                        'status': 'reassigned'
                    })
                else:
                    results['errors'].append({
                        'workspace': ws_name,
                        'error': 'Workspace not found'
                    })
            except Exception as e:
                results['errors'].append({
                    'workspace': ws_name,
                    'error': str(e)
                })
        
        frappe.db.commit()
        
        results['summary'] = f"Deleted {len(results['deleted_modules'])} modules. Reassigned {len(results['reassigned_workspaces'])} workspaces. Errors: {len(results['errors'])}"
    
    except Exception as e:
        results['errors'].append({
            'type': 'general',
            'error': str(e)
        })
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
