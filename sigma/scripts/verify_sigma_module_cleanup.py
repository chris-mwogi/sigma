import frappe
import json

def execute():
    """Check all workspace modules in the database."""
    
    # Get all distinct modules
    modules = frappe.db.sql("SELECT DISTINCT module FROM `tabWorkspace` ORDER BY module", as_dict=False)
    modules_list = [m[0] for m in modules]
    
    # Get all workspaces with their modules
    workspaces = frappe.db.sql("SELECT name, module FROM `tabWorkspace` ORDER BY name", as_dict=True)
    
    # Check if any Sigma modules remain
    sigma_modules = [m for m in modules_list if 'Sigma' in m or 'sigma' in m]
    
    result = {
        'total_workspaces': len(workspaces),
        'distinct_modules': modules_list,
        'sigma_modules_remaining': sigma_modules,
        'workspaces': workspaces
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    execute()
