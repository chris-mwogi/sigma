import frappe
import json
import os
import re

PRIORITY = ['DocType', 'Report', 'Dashboard', 'Page']


def find_fuzzy(name):
    tokens = re.split(r'\W+', name)
    tokens = [t for t in tokens if t]
    if not tokens:
        return None
    pattern = '%' + '%'.join(tokens) + '%'
    # search by priority
    for doctype in PRIORITY:
        table = {'DocType': 'tabDocType', 'Report': 'tabReport', 'Dashboard': 'tabDashboard', 'Page': 'tabPage'}[doctype]
        res = frappe.db.sql(f"select name from `{table}` where name like %s limit 1", (pattern,))
        if res:
            return {'type': doctype, 'name': res[0][0]}
    return None


def apply_to_workspace(ws_name, unresolved, block_type, suggestion):
    ws = frappe.get_doc('Workspace', ws_name)
    content_raw = ws.content or ''
    if not content_raw:
        return False, 'empty'
    try:
        content = json.loads(content_raw)
    except Exception as e:
        return False, f'invalid_json:{e}'
    applied = False
    changes = []
    for i, block in enumerate(content):
        if block.get('type') != block_type:
            continue
        data = block.get('data') or {}
        candidates = []
        for k in ('unresolved_shortcut_name','unresolved_link_name','shortcut_name','name','link_to'):
            if data.get(k):
                candidates.append(data.get(k))
        if unresolved not in candidates:
            # sometimes block may have been normalized; try matching label
            if data.get('label') != unresolved:
                continue
        # apply suggestion
        t = suggestion['type']
        n = suggestion['name']
        data['type'] = t
        data['link_to'] = n
        data['name'] = n
        if not data.get('label'):
            data['label'] = unresolved
        for k in ('unresolved_shortcut_name','unresolved_link_name','shortcut_name'):
            if k in data:
                del data[k]
        block['data'] = data
        content[i] = block
        applied = True
        changes.append({'index': i, 'from': unresolved, 'to': {'type': t, 'name': n}})
    if applied:
        backup_dir = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'fuzzy_apply')
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{ws_name.replace(' ','_')}.json.before")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content_raw)
        ws.content = json.dumps(content)
        ws.save()
        with open(backup_file + '.after', 'w', encoding='utf-8') as f:
            f.write(ws.content or '')
        return True, changes
    return False, 'no_match'


def execute():
    mapping_path = frappe.get_app_path('sigma', 'scripts', 'unresolved_mappings.json')
    if not os.path.exists(mapping_path):
        print(json.dumps({'error':'mapping_missing','path':mapping_path}))
        return
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    applied = []
    skipped = []
    for entry in mapping:
        ws = entry.get('workspace')
        unresolved = entry.get('unresolved_name')
        block_type = entry.get('block_type')
        # try to find candidate via fuzzy search
        sugg = find_fuzzy(unresolved)
        if not sugg:
            skipped.append({'workspace': ws, 'unresolved': unresolved, 'reason': 'no_fuzzy_match'})
            continue
        ok, info = apply_to_workspace(ws, unresolved, block_type, sugg)
        if ok:
            applied.append({'workspace': ws, 'unresolved': unresolved, 'applied_to': info, 'suggestion': sugg})
        else:
            skipped.append({'workspace': ws, 'unresolved': unresolved, 'reason': info, 'suggestion': sugg})
    print(json.dumps({'applied': applied, 'skipped': skipped}))
