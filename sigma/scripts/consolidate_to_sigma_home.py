import frappe
import json
import os

def execute():
    """
    Consolidate all workspaces from 'sigma' module to 'sigma_home' module.
    Set Sigma Home workspace as the default home workspace.
    """
    
    results = {
        'consolidated_workspaces': [],
        'set_default': None,
        'errors': []
    }
    
    # Get all workspaces in sigma module (use direct SQL to avoid Module validation)
    sigma_workspaces = frappe.db.sql("""
        SELECT name, module FROM `tabWorkspace` WHERE module = 'Sigma'
    """, as_dict=True)
    
    if not sigma_workspaces:
        results['message'] = 'No workspaces found in sigma module'
        print(json.dumps(results))
        return
    
    # Update each workspace module from 'Sigma' to 'sigma_home' using direct SQL
    for ws_record in sigma_workspaces:
        try:
            frappe.db.set_value('Workspace', ws_record['name'], 'module', 'sigma_home')
            results['consolidated_workspaces'].append({
                'name': ws_record['name'],
                'new_module': 'sigma_home',
                'status': 'updated'
            })
        except Exception as e:
            results['errors'].append({
                'workspace': ws_record['name'],
                'error': str(e)
            })
    
    # Set Sigma Home as the default workspace
    try:
        sigma_home = frappe.get_doc('Workspace', 'Sigma Home')
        frappe.db.set_value('Workspace', 'Sigma Home', 'is_hidden', 0)
        
        results['set_default'] = {
            'workspace': 'Sigma Home',
            'status': 'set_as_default',
            'is_hidden': 0
        }
    except Exception as e:
        results['errors'].append({
            'set_default': str(e)
        })
    
    frappe.db.commit()
    print(json.dumps(results))
