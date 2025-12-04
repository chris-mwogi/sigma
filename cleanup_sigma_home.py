import os
import shutil
import json


def cleanup_sigma_home():
    """
    Clean up sigma_home by removing workspace directories that now have their own modules.
    Keep only: home, sigma_home
    Remove: crm, helpdesk, projects, quality, support, telephony
    """
    
    results = {
        'removed_directories': [],
        'kept_directories': [],
        'errors': []
    }
    
    workspace_path = '/workspace/development/frappe-bench/apps/sigma/sigma/sigma_home/workspace'
    
    # Directories to remove (they now have their own modules)
    to_remove = ['crm', 'helpdesk', 'projects', 'quality', 'support', 'telephony']
    
    # Directories to keep
    to_keep = ['home', 'sigma_home']
    
    try:
        # Remove duplicate workspace directories
        for dir_name in to_remove:
            dir_path = os.path.join(workspace_path, dir_name)
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    results['removed_directories'].append({
                        'directory': dir_name,
                        'path': dir_path,
                        'status': 'removed'
                    })
                except Exception as e:
                    results['errors'].append({
                        'directory': dir_name,
                        'error': str(e)
                    })
            else:
                results['removed_directories'].append({
                    'directory': dir_name,
                    'status': 'not_found'
                })
        
        # Verify kept directories
        for dir_name in to_keep:
            dir_path = os.path.join(workspace_path, dir_name)
            if os.path.exists(dir_path):
                results['kept_directories'].append({
                    'directory': dir_name,
                    'path': dir_path,
                    'status': 'preserved'
                })
            else:
                results['errors'].append({
                    'directory': dir_name,
                    'error': 'Directory not found - should be preserved!'
                })
    
    except Exception as e:
        results['errors'].append({
            'type': 'general',
            'error': str(e)
        })
    
    return results


if __name__ == '__main__':
    result = cleanup_sigma_home()
    print(json.dumps(result, indent=2))
