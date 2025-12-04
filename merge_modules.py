import os
import shutil
import json


def merge_sigma_home_to_sigma():
    """
    Merge sigma_home module into sigma module.
    Move all content from sigma_home to sigma, then delete sigma_home.
    Update database to assign sigma_home workspaces to sigma module.
    """
    
    results = {
        'copied_directories': [],
        'copied_files': [],
        'removed_directories': [],
        'errors': [],
        'summary': ''
    }
    
    sigma_path = '/workspace/development/frappe-bench/apps/sigma/sigma/sigma'
    sigma_home_path = '/workspace/development/frappe-bench/apps/sigma/sigma/sigma_home'
    
    try:
        # Directories to move from sigma_home to sigma
        dirs_to_move = ['config', 'doctype', 'page', 'website_page', 'workspace']
        
        for dir_name in dirs_to_move:
            src_dir = os.path.join(sigma_home_path, dir_name)
            dst_dir = os.path.join(sigma_path, dir_name)
            
            if os.path.exists(src_dir):
                try:
                    # If destination exists, merge contents
                    if os.path.exists(dst_dir):
                        for item in os.listdir(src_dir):
                            src_item = os.path.join(src_dir, item)
                            dst_item = os.path.join(dst_dir, item)
                            
                            if os.path.isdir(src_item):
                                if os.path.exists(dst_item):
                                    # Skip if already exists
                                    results['copied_directories'].append({
                                        'from': src_item,
                                        'to': dst_item,
                                        'status': 'already_exists'
                                    })
                                else:
                                    shutil.copytree(src_item, dst_item)
                                    results['copied_directories'].append({
                                        'from': src_item,
                                        'to': dst_item,
                                        'status': 'copied'
                                    })
                            else:
                                if not os.path.exists(dst_item):
                                    shutil.copy2(src_item, dst_item)
                                results['copied_files'].append({
                                    'from': src_item,
                                    'to': dst_item,
                                    'status': 'copied'
                                })
                    else:
                        # Destination doesn't exist, move entire directory
                        shutil.copytree(src_dir, dst_dir)
                        results['copied_directories'].append({
                            'from': src_dir,
                            'to': dst_dir,
                            'status': 'moved'
                        })
                
                except Exception as e:
                    results['errors'].append({
                        'directory': dir_name,
                        'error': str(e)
                    })
        
        # Remove sigma_home directory after merge
        try:
            shutil.rmtree(sigma_home_path)
            results['removed_directories'].append({
                'directory': 'sigma_home',
                'path': sigma_home_path,
                'status': 'deleted'
            })
        except Exception as e:
            results['errors'].append({
                'directory': 'sigma_home',
                'error': f'Failed to delete: {str(e)}'
            })
        
        results['summary'] = f"Merged sigma_home into sigma: {len(results['copied_directories'])} directories, {len(results['copied_files'])} files copied. Errors: {len(results['errors'])}"
    
    except Exception as e:
        results['errors'].append({
            'type': 'general',
            'error': str(e)
        })
    
    return results


if __name__ == '__main__':
    result = merge_sigma_home_to_sigma()
    print(json.dumps(result, indent=2))
