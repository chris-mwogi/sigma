import frappe
import json

def execute():
    """Register sigma_home module if not already registered."""
    
    # Check if sigma_home module exists
    if frappe.db.exists('Module', 'sigma_home'):
        result = {'status': 'already_exists', 'module': 'sigma_home'}
        print(json.dumps(result))
        return
    
    # Create sigma_home module
    try:
        mod = frappe.new_doc('Module')
        mod.name = 'sigma_home'
        mod.module_name = 'sigma_home'
        mod.app_name = 'sigma'
        mod.insert(ignore_permissions=True)
        frappe.db.commit()
        result = {'status': 'created', 'module': 'sigma_home'}
        print(json.dumps(result))
    except Exception as e:
        result = {'status': 'error', 'module': 'sigma_home', 'error': str(e)}
        print(json.dumps(result))
