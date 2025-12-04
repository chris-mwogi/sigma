import frappe
import json


def execute():
    """
    Restore original workspace module assignments from workspace data.
    This maps workspaces back to their original sigma modules.
    """
    
    results = {
        'restored_workspaces': [],
        'errors': [],
        'summary': ''
    }
    
    # Mapping of workspaces to their original modules
    workspace_module_mapping = {
        'Home': 'sigma_home',
        'Sigma Home': 'sigma_home',
        'CRM': 'sigma_home',
        'Support': 'sigma_home',
        'Helpdesk': 'sigma_home',
        'Projects': 'sigma_home',
        'Quality': 'sigma_home',
        'Telephony': 'sigma_home',
        'Stock': 'Sigma Asset Integrations',
        'Settings': 'Sigma Asset Integrations',
        'Disposal (Selling)': 'Sigma Asset Integrations',
        'Acquisition (Buying)': 'Sigma Asset Integrations',
        'Asset Management': 'Sigma Asset Integrations',
        'Access Control': 'Sigma Access Control',
        'Case Management': 'Sigma Case Management',
        'Guard Monitoring': 'Sigma Guard Monitoring',
        'Visitor Management': 'Sigma Visitor Management',
        'Vehicle Management': 'Sigma Vehicle Management',
        'Risk Assessment': 'Sigma Risk Assessment'
    }
    
    for workspace_name, module_name in workspace_module_mapping.items():
        try:
            if frappe.db.exists('Workspace', workspace_name):
                frappe.db.set_value('Workspace', workspace_name, 'module', module_name)
                results['restored_workspaces'].append({
                    'workspace': workspace_name,
                    'module': module_name,
                    'status': 'restored'
                })
            else:
                results['errors'].append({
                    'workspace': workspace_name,
                    'error': 'Workspace not found'
                })
        except Exception as e:
            results['errors'].append({
                'workspace': workspace_name,
                'error': str(e)
            })
    
    frappe.db.commit()
    
    results['summary'] = f"Restored {len(results['restored_workspaces'])} workspaces. {len(results['errors'])} errors."
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
