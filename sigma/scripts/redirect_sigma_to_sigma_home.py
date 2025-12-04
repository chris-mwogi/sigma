import frappe
import json
import os
import shutil


def execute():
    """
    1. Redirect all remaining Sigma module assignments to sigma_home
    2. Delete the Sigma Module Def from database
    3. Remove sigma module directories (except sigma_home)
    """
    
    results = {
        'redirected_workspaces': [],
        'redirected_other_docs': [],
        'deleted_sigma_module_def': False,
        'deleted_directories': [],
        'errors': []
    }
    
    try:
        # Step 1: Find and redirect all workspaces with module = 'Sigma'
        sigma_workspaces = frappe.db.sql(
            "SELECT name, module FROM `tabWorkspace` WHERE module = 'Sigma' OR module LIKE 'Sigma%'",
            as_dict=True
        )
        
        for ws in sigma_workspaces:
            try:
                frappe.db.set_value('Workspace', ws['name'], 'module', 'sigma_home')
                results['redirected_workspaces'].append({
                    'name': ws['name'],
                    'from_module': ws['module'],
                    'to_module': 'sigma_home'
                })
            except Exception as e:
                results['errors'].append({
                    'type': 'workspace_redirect',
                    'name': ws['name'],
                    'error': str(e)
                })
        
        # Step 2: Find and redirect any other items with Sigma module assignment
        # Check Dashboard, Report, and other module-aware doctypes
        try:
            other_docs = frappe.db.sql(
                "SELECT name FROM `tabDashboard` WHERE module LIKE 'Sigma%' OR module = 'Sigma' LIMIT 100",
                as_dict=True
            )
            for doc in other_docs:
                try:
                    frappe.db.set_value('Dashboard', doc['name'], 'module', 'sigma_home')
                    results['redirected_other_docs'].append({
                        'doctype': 'Dashboard',
                        'name': doc['name'],
                        'to_module': 'sigma_home'
                    })
                except Exception as e:
                    results['errors'].append({
                        'type': 'dashboard_redirect',
                        'name': doc['name'],
                        'error': str(e)
                    })
        except Exception as e:
            pass  # Dashboard might not exist, continue
        
        # Step 3: Delete Sigma Module Def from database (and all related Sigma* module defs)
        sigma_module_names = frappe.db.sql(
            "SELECT name FROM `tabModule Def` WHERE name LIKE 'Sigma%'",
            as_dict=True
        )
        
        for module_doc in sigma_module_names:
            try:
                frappe.delete_doc('Module Def', module_doc['name'], force=True, ignore_permissions=True)
                results['deleted_sigma_module_def'] = True
            except Exception as e:
                results['errors'].append({
                    'type': 'module_def_deletion',
                    'module': module_doc['name'],
                    'error': str(e)
                })
        
        # Step 4: Delete sigma module directories (keep sigma_home)
        sigma_base_path = frappe.get_app_path('sigma', 'sigma')
        directories_to_delete = [
            'sigma',  # The old sigma/ directory (different from sigma/sigma_home)
            'sigma_access_control',
            'sigma_asset_integrations',
            'sigma_case_management',
            'sigma_erpnext_integrations',
            'sigma_guard_monitoring',
            'sigma_risk_assessment',
            'sigma_vehicle_management',
            'sigma_visitor_management'
        ]
        
        for dir_name in directories_to_delete:
            dir_path = os.path.join(sigma_base_path, dir_name)
            if os.path.exists(dir_path):
                try:
                    if dir_name == 'sigma':
                        # Special case: only delete if it doesn't contain sigma_home
                        # First, check what's in it
                        if os.path.isdir(dir_path):
                            contents = os.listdir(dir_path)
                            if contents == ['sigma_home'] or (len(contents) == 1 and 'sigma_home' in contents):
                                # Only sigma_home inside, safe to delete parent
                                shutil.rmtree(dir_path)
                                results['deleted_directories'].append(dir_name)
                            else:
                                # Has other content, preserve
                                results['errors'].append({
                                    'type': 'directory_skip',
                                    'path': dir_path,
                                    'reason': f'Contains other content: {contents}'
                                })
                    else:
                        shutil.rmtree(dir_path)
                        results['deleted_directories'].append(dir_name)
                except Exception as e:
                    results['errors'].append({
                        'type': 'directory_deletion',
                        'path': dir_path,
                        'error': str(e)
                    })
        
        frappe.db.commit()
    
    except Exception as e:
        results['errors'].append({
            'type': 'general',
            'error': str(e)
        })
    
    return results


if __name__ == '__main__':
    result = execute()
    print(json.dumps(result, indent=2))
