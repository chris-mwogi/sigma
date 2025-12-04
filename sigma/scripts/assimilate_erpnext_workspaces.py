import frappe
import json
import os

MAPPINGS = [
    # (erpnext_file, sigma_workspace_name, sigma_file_path)
    (
        frappe.get_app_path('erpnext', 'crm', 'workspace', 'crm', 'crm.json'),
        'CRM',
        frappe.get_app_path('sigma', 'sigma', 'sigma', 'workspace', 'crm', 'crm.json')
    ),
    (
        frappe.get_app_path('erpnext', 'support', 'workspace', 'support', 'support.json'),
        'Support',
        frappe.get_app_path('sigma', 'sigma', 'sigma', 'workspace', 'support', 'support.json')
    ),
    (
        frappe.get_app_path('erpnext', 'projects', 'workspace', 'projects', 'projects.json'),
        'Projects',
        frappe.get_app_path('sigma', 'sigma', 'sigma', 'workspace', 'projects', 'projects.json')
    ),
    (
        frappe.get_app_path('erpnext', 'quality_management', 'workspace', 'quality', 'quality.json'),
        'Quality',
        frappe.get_app_path('sigma', 'sigma', 'sigma', 'workspace', 'quality', 'quality.json')
    ),
]


def ensure_dir(path):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)


def backup_workspace(ws_name):
    try:
        ws = frappe.get_doc('Workspace', ws_name)
        site = frappe.local.site
        backup_dir = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'assimilate')
        os.makedirs(backup_dir, exist_ok=True)
        with open(os.path.join(backup_dir, f"{ws_name.replace(' ','_')}.json.before"), 'w', encoding='utf-8') as f:
            f.write(ws.content or '')
        return True, backup_dir
    except Exception as e:
        return False, str(e)


def apply_mapping(erp_file, ws_name, sigma_file):
    if not os.path.exists(erp_file):
        return {'workspace': ws_name, 'status': 'erp_file_missing', 'file': erp_file}
    with open(erp_file, 'r', encoding='utf-8') as f:
        erp_content = f.read()
    # validate JSON and extract content
    try:
        erp_obj = json.loads(erp_content)
    except Exception as e:
        return {'workspace': ws_name, 'status': 'erp_json_invalid', 'error': str(e)}

    # ERPNext workspace files are objects; the actual UI blocks are often in erp_obj['content']
    # which can itself be a JSON string representing a list. We want to set Workspace.content
    # to that list (serialized) so the DB sees the expected structure.
    new_ws_content = None
    if isinstance(erp_obj, dict) and 'content' in erp_obj:
        candidate = erp_obj.get('content')
        if isinstance(candidate, str):
            # content stored as JSON string in ERPNext files
            new_ws_content = candidate
        else:
            # content is a list/object; serialize to string
            new_ws_content = json.dumps(candidate)
    else:
        # fallback: if the ERP file is already the content list
        new_ws_content = json.dumps(erp_obj)

    ok, info = backup_workspace(ws_name)
    if not ok:
        return {'workspace': ws_name, 'status': 'backup_failed', 'error': info}

    # write sigma file (save the full ERPNext JSON object so the file mirrors ERPNext)
    ensure_dir(sigma_file)
    with open(sigma_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(erp_obj, indent=2))

    # update DB
    try:
        ws = frappe.get_doc('Workspace', ws_name)
        if new_ws_content is None:
            return {'workspace': ws_name, 'status': 'no_content_in_erp_file'}
        ws.content = new_ws_content
        ws.save()
    except Exception as e:
        return {'workspace': ws_name, 'status': 'db_update_failed', 'error': str(e)}

    return {'workspace': ws_name, 'status': 'updated', 'sigma_file': sigma_file}


def execute():
    results = []
    for erp_file, ws_name, sigma_file in MAPPINGS:
        res = apply_mapping(erp_file, ws_name, sigma_file)
        results.append(res)
    print(json.dumps(results))
