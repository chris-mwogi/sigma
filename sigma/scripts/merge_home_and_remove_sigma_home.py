import frappe
import json

def execute():
    # Ensure both exist
    try:
        sigma_home = frappe.get_doc('Workspace', 'Sigma Home')
    except Exception as e:
        print(json.dumps({'error':'Sigma Home not found','msg':str(e)}))
        return
    try:
        home = frappe.get_doc('Workspace', 'Home')
    except Exception as e:
        print(json.dumps({'error':'Home not found','msg':str(e)}))
        return

    # Backup both contents to files in site public files (so accessible)
    try:
        import os
        site = frappe.local.site
        backup_dir = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups')
        os.makedirs(backup_dir, exist_ok=True)
        with open(os.path.join(backup_dir, 'Home_content.json'), 'w', encoding='utf-8') as f:
            f.write(home.content or '')
        with open(os.path.join(backup_dir, 'Sigma_Home_content.json'), 'w', encoding='utf-8') as f:
            f.write(sigma_home.content or '')
        print(json.dumps({'backup_dir': backup_dir}))
    except Exception as e:
        print(json.dumps({'backup_error': str(e)}))

    # Strategy: prefer to preserve Home.title/name, but use Sigma Home content if it's larger
    try:
        if (sigma_home.content or '') and (len(sigma_home.content or '') > len(home.content or '')):
            home.content = sigma_home.content
            print(json.dumps({'action':'replaced_home_content_with_sigma_home'}))
        else:
            print(json.dumps({'action':'kept_home_content'}))
        # copy some flags
        home.public = sigma_home.public
        home.for_user = sigma_home.for_user
        home.parent_page = sigma_home.parent_page
        home.is_default = sigma_home.is_default or home.is_default
        home.save()
        print(json.dumps({'saved_home': home.name}))
    except Exception as e:
        print(json.dumps({'save_error': str(e)}))

    # Delete Sigma Home
    try:
        frappe.delete_doc('Workspace', 'Sigma Home', force=True)
        print(json.dumps({'deleted': 'Sigma Home'}))
    except Exception as e:
        print(json.dumps({'delete_error': str(e)}))
