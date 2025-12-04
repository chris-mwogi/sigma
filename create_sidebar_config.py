import os
import json


def create_desktop_config():
    """
    Create desktop.py configuration files for all workspace modules
    to make workspaces appear in the sidebar.
    """
    
    results = {
        'created_files': [],
        'created_directories': [],
        'errors': []
    }
    
    base_path = '/workspace/development/frappe-bench/apps/sigma/sigma'
    
    # Workspace modules with their configurations
    modules_config = [
        {
            'module_dir': 'sigma_crm',
            'module_name': 'Sigma CRM',
            'workspace_name': 'CRM',
            'icon': 'briefcase',
            'color': '#FF6B6B'
        },
        {
            'module_dir': 'sigma_helpdesk',
            'module_name': 'Sigma Helpdesk',
            'workspace_name': 'Helpdesk',
            'icon': 'life-ring',
            'color': '#4ECDC4'
        },
        {
            'module_dir': 'sigma_projects',
            'module_name': 'Sigma Projects',
            'workspace_name': 'Projects',
            'icon': 'tasks',
            'color': '#45B7D1'
        },
        {
            'module_dir': 'sigma_quality',
            'module_name': 'Sigma Quality',
            'workspace_name': 'Quality',
            'icon': 'check-circle',
            'color': '#96CEB4'
        },
        {
            'module_dir': 'sigma_support',
            'module_name': 'Sigma Support',
            'workspace_name': 'Support',
            'icon': 'support',
            'color': '#FFEAA7'
        },
        {
            'module_dir': 'sigma_telephony',
            'module_name': 'Sigma Telephony',
            'workspace_name': 'Telephony',
            'icon': 'phone',
            'color': '#DDA0DD'
        }
    ]
    
    for config in modules_config:
        try:
            module_path = os.path.join(base_path, config['module_dir'])
            config_dir = os.path.join(module_path, 'config')
            
            # Create config directory if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                results['created_directories'].append({
                    'directory': config['module_dir'] + '/config',
                    'path': config_dir
                })
            
            # Create __init__.py in config
            init_file = os.path.join(config_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('')
            
            # Create desktop.py
            desktop_file = os.path.join(config_dir, 'desktop.py')
            desktop_content = f'''from frappe import _

def get_data():
    return [
        {{
            "module_name": "{config['module_name']}",
            "color": "{config['color']}",
            "icon": "{config['icon']}",
            "type": "module",
            "label": _("📊 {config['workspace_name']}")
        }}
    ]
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            results['created_files'].append({
                'file': desktop_file,
                'module': config['module_dir'],
                'status': 'created'
            })
        
        except Exception as e:
            results['errors'].append({
                'module': config['module_dir'],
                'error': str(e)
            })
    
    return results


if __name__ == '__main__':
    result = create_desktop_config()
    print(json.dumps(result, indent=2))
