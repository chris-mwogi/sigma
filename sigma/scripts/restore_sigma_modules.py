import frappe
import json


def execute():
    """
    Restore all Sigma Module Def entries in the database.
    """
    
    results = {
        'created_modules': [],
        'errors': [],
        'summary': ''
    }
    
    # List of all sigma modules to restore with their metadata
    modules_to_restore = [
        {
            'name': 'Sigma Access Control',
            'module_name': 'Sigma Access Control',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Asset Integrations',
            'module_name': 'Sigma Asset Integrations',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Case Management',
            'module_name': 'Sigma Case Management',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma ERP Next Integrations',
            'module_name': 'Sigma ERP Next Integrations',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Guard Monitoring',
            'module_name': 'Sigma Guard Monitoring',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma',
            'module_name': 'Sigma',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Risk Assessment',
            'module_name': 'Sigma Risk Assessment',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Vehicle Management',
            'module_name': 'Sigma Vehicle Management',
            'app_name': 'sigma',
            'category': 'Modules'
        },
        {
            'name': 'Sigma Visitor Management',
            'module_name': 'Sigma Visitor Management',
            'app_name': 'sigma',
            'category': 'Modules'
        }
    ]
    
    for module_info in modules_to_restore:
        try:
            # Check if module already exists
            if frappe.db.exists('Module Def', module_info['name']):
                results['created_modules'].append({
                    'name': module_info['name'],
                    'status': 'already_exists'
                })
                continue
            
            # Create new Module Def
            module_doc = frappe.new_doc('Module Def')
            module_doc.module_name = module_info['module_name']
            module_doc.app_name = module_info['app_name']
            module_doc.category = module_info['category']
            module_doc.insert(ignore_permissions=True)
            
            results['created_modules'].append({
                'name': module_info['name'],
                'status': 'created'
            })
            
        except Exception as e:
            results['errors'].append({
                'module': module_info['name'],
                'error': str(e)
            })
    
    frappe.db.commit()
    
    created_count = len([m for m in results['created_modules'] if m.get('status') == 'created'])
    existing_count = len([m for m in results['created_modules'] if m.get('status') == 'already_exists'])
    
    results['summary'] = f"Restored {created_count} modules. {existing_count} modules already existed. {len(results['errors'])} errors."
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    execute()
