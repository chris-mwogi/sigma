import frappe
import json
import os

def execute():
    # Check if Sigma Home already exists
    if frappe.db.exists('Workspace', 'Sigma Home'):
        print(json.dumps({'status': 'already_exists', 'workspace': 'Sigma Home'}))
        return
    
    # Load backup content
    backup_path = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'Sigma_Home_content.json')
    if not os.path.exists(backup_path):
        print(json.dumps({'status': 'backup_not_found', 'path': backup_path}))
        return
    
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Create Sigma Home workspace document
    try:
        ws = frappe.get_doc({
            'doctype': 'Workspace',
            'name': 'Sigma Home',
            'label': 'Sigma Home',
            'title': 'Sigma Home',
            'module': 'Sigma',
            'content': json.dumps(content),
            'public': 1,
            'is_default': 0
        })
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        print(json.dumps({'status': 'created', 'workspace': 'Sigma Home', 'content_blocks': len(content)}))
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
