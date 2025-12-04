import frappe
import json
import os


def execute():
    """
    Remove unresolved opaque ID shortcuts (7u... pattern) from all workspaces using direct DB updates.
    Apply specific mappings to Projects workspace.
    """
    
    opaque_ids = [
        # Projects
        '7ubp9090u4', '7ubiaat731', '7ubirknjpd',
        # Quality
        '7uarp1ge0k', '7uajovag60', '7uai5fuudb',
        # Support
        '7ua4a3gf07', '7ua2qtrrnc', '7ua77hv8lc',
        # CRM
        '7u928qkm3j', '7u9vgslpu9', '7u9h9l70ms', '7u9haubfl5',
        # Helpdesk
        '7u8dc4c39n', '7u8hv62ncb', '7u929jak0g', '7u9pha0q2n',
        # Telephony
        '7u8iqfabhi', '7u8im4rplh', '7u8prb0svm'
    ]
    
    results = {
        'removed_opaque_ids': [],
        'applied_mappings': [],
        'errors': []
    }
    
    # Get all workspaces directly
    ws_list = frappe.db.sql("SELECT name, content FROM `tabWorkspace`", as_dict=True)
    
    for ws_record in ws_list:
        ws_name = ws_record['name']
        content_raw = ws_record.get('content') or ''
        
        if not content_raw:
            continue
        
        try:
            content = json.loads(content_raw)
            modified = False
            
            # Remove opaque ID shortcuts
            new_content = []
            for block in content:
                if block.get('type') == 'shortcut':
                    data = block.get('data') or {}
                    unresolved = data.get('unresolved_shortcut_name') or data.get('shortcut_name')
                    if unresolved in opaque_ids:
                        results['removed_opaque_ids'].append({
                            'workspace': ws_name,
                            'removed': unresolved
                        })
                        modified = True
                        continue  # Skip this block (remove it)
                
                new_content.append(block)
            
            # Apply specific mappings for Projects
            if ws_name == 'Projects':
                for i, block in enumerate(new_content):
                    if block.get('type') == 'shortcut':
                        data = block.get('data') or {}
                        unresolved = data.get('unresolved_shortcut_name')
                        
                        if unresolved == 'Project Billing Summary':
                            new_content[i]['data'] = {
                                'type': 'Report',
                                'link_to': 'Project Summary',
                                'name': 'Project Summary',
                                'label': 'Project Billing Summary',
                                'col': data.get('col', 3)
                            }
                            results['applied_mappings'].append({
                                'workspace': ws_name,
                                'from': 'Project Billing Summary',
                                'to': {'type': 'Report', 'name': 'Project Summary'}
                            })
                            modified = True
            
            # Update DB using direct SQL
            if modified:
                new_content_json = json.dumps(new_content)
                frappe.db.set_value('Workspace', ws_name, 'content', new_content_json)
                
                # Write JSON file to disk
                try:
                    ws_folder = ws_name.lower().replace(' ', '_')
                    file_path = frappe.get_app_path('sigma', 'sigma', 'sigma_home', 'workspace', 
                                                    ws_folder, f"{ws_folder}.json")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({'content': new_content}, f, indent=2)
                except Exception as e:
                    results['errors'].append({
                        'workspace': ws_name,
                        'file_write_error': str(e)
                    })
        
        except Exception as e:
            results['errors'].append({
                'workspace': ws_name,
                'error': str(e)
            })
    
    frappe.db.commit()
    print(json.dumps(results))
