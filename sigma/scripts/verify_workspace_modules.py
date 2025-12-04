import frappe
import json


def execute():
    """
    Verify all workspace modules are properly created and assigned.
    """
    
    results = {
        'workspaces': [],
        'modules_status': {}
    }
    
    # Get all workspaces and their current modules
    workspaces = frappe.db.sql("SELECT name, module FROM `tabWorkspace` ORDER BY name", as_dict=True)
    
    for ws in workspaces:
        results['workspaces'].append({
            'workspace': ws['name'],
            'module': ws['module']
        })
    
    # Get all Sigma-related module defs
    modules = frappe.db.sql("SELECT name FROM `tabModule Def` WHERE name LIKE 'Sigma%' ORDER BY name", as_dict=True)
    
    for mod in modules:
        results['modules_status'][mod['name']] = 'exists'
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
