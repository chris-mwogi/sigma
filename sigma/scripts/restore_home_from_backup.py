import frappe
import json
import os

def execute():
    try:
        home = frappe.get_doc('Workspace', 'Home')
    except Exception as e:
        print(json.dumps({'error':'Home not found','msg':str(e)}))
        return
    try:
        backup_path = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'Sigma_Home_content.json')
        if not os.path.exists(backup_path):
            print(json.dumps({'error':'backup_missing', 'path': backup_path}))
            return
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        home.content = content
        # avoid assigning unknown attributes
        home.save()
        print(json.dumps({'restored_from': backup_path, 'saved_home': 'Home'}))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
