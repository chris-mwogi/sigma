import os
import shutil
import json
import frappe


def execute():
    """
    Final cleanup: Delete all sigma-prefixed module directories (except sigma_home).
    """
    
    results = {
        'deleted_directories': [],
        'errors': [],
        'summary': ''
    }
    
    try:
        # Get the correct path - avoid double sigma
        sigma_base_path = os.path.dirname(frappe.get_app_path('sigma'))
        # Now we're at /workspace/development/frappe-bench/apps/sigma
        # Need to go to sigma_home's parent
        sigma_base_path = os.path.join(sigma_base_path, 'sigma')
        
        # List of sigma-prefixed directories to delete
        directories_to_delete = [
            'sigma_access_control',
            'sigma_asset_integrations',
            'sigma_case_management',
            'sigma_erpnext_integrations',
            'sigma_guard_monitoring',
            'sigma_risk_assessment',
            'sigma_vehicle_management',
            'sigma_visitor_management'
        ]
        
        deleted_count = 0
        for dir_name in directories_to_delete:
            dir_path = os.path.join(sigma_base_path, dir_name)
            
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    results['deleted_directories'].append({
                        'directory': dir_name,
                        'path': dir_path,
                        'status': 'deleted'
                    })
                    deleted_count += 1
                except Exception as e:
                    results['errors'].append({
                        'directory': dir_name,
                        'path': dir_path,
                        'error': str(e)
                    })
            else:
                results['deleted_directories'].append({
                    'directory': dir_name,
                    'path': dir_path,
                    'status': 'not_found'
                })
        
        results['summary'] = f"Successfully deleted {deleted_count} sigma module directories. sigma_home module preserved."
        
    except Exception as e:
        results['errors'].append({
            'type': 'general',
            'error': str(e)
        })
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
