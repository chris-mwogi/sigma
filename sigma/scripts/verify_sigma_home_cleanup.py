import frappe
import json


def execute():
    """
    Verify sigma_home cleanup and workspace status.
    """
    
    results = {
        'sigma_home_workspace': {},
        'home_workspace': {},
        'workspace_count': 0,
        'errors': []
    }
    
    try:
        # Check Sigma Home workspace
        if frappe.db.exists('Workspace', 'Sigma Home'):
            ws = frappe.get_doc('Workspace', 'Sigma Home')
            results['sigma_home_workspace'] = {
                'name': ws.name,
                'module': ws.module,
                'content_length': len(ws.content or ''),
                'status': 'exists'
            }
        else:
            results['errors'].append('Sigma Home workspace not found in database')
        
        # Check Home workspace
        if frappe.db.exists('Workspace', 'Home'):
            ws = frappe.get_doc('Workspace', 'Home')
            results['home_workspace'] = {
                'name': ws.name,
                'module': ws.module,
                'content_length': len(ws.content or ''),
                'status': 'exists'
            }
        else:
            results['errors'].append('Home workspace not found in database')
        
        # Count sigma_home module workspaces
        workspaces = frappe.db.sql(
            "SELECT name, module FROM `tabWorkspace` WHERE module = 'sigma_home' ORDER BY name",
            as_dict=True
        )
        results['workspace_count'] = len(workspaces)
        results['workspaces_in_sigma_home'] = [ws['name'] for ws in workspaces]
        
    except Exception as e:
        results['errors'].append(str(e))
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
