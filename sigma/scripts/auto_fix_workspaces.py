import frappe
import json
import os
import re

PREFIXES = ['New ', 'List ', 'All ', 'Recent ', 'View '] 

# simple singularization: remove trailing s if present (very naive)
def singularize(name):
    if name.endswith('ies'):
        return name[:-3] + 'y'
    if name.endswith('s') and not name.endswith('ss'):
        return name[:-1]
    return name


def candidates(name):
    name = name.strip()
    cands = [name]
    cands.append(name.title())
    cands.append(name.capitalize())
    for p in PREFIXES:
        if name.startswith(p):
            cands.append(name[len(p):])
            cands.append(name[len(p):].title())
    # singularize last token
    tokens = name.split()
    if tokens:
        last = tokens[-1]
        s = singularize(last)
        if s != last:
            tokens2 = tokens[:-1] + [s]
            cands.append(' '.join(tokens2))
            cands.append(' '.join(tokens2).title())
    # dedupe candidates preserving order
    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def find_existing(name):
    """Return tuple (found_type, found_name) or (None, None)"""
    # Try direct checks on candidate transforms
    for c in candidates(name):
        # check DocType first
        if frappe.db.exists('DocType', c):
            return ('DocType', c)
        if frappe.db.exists('Report', c):
            return ('Report', c)
        if frappe.db.exists('Dashboard', c):
            return ('Dashboard', c)
        if frappe.db.exists('Page', c):
            return ('Page', c)
    # If still not found, try partial match: find a DocType containing tokens
    tokens = re.split(r'\W+', name)
    tokens = [t for t in tokens if t]
    if tokens:
        pattern = '%' + '%'.join(tokens) + '%'
        res = frappe.db.sql("""select name from `tabDocType` where name like %s limit 1""", (pattern,))
        if res:
            return ('DocType', res[0][0])
        res = frappe.db.sql("""select name from `tabReport` where name like %s limit 1""", (pattern,))
        if res:
            return ('Report', res[0][0])
        res = frappe.db.sql("""select name from `tabDashboard` where name like %s limit 1""", (pattern,))
        if res:
            return ('Dashboard', res[0][0])
    return (None, None)


def normalize_shortcut_block(block):
    data = block.get('data') or {}
    changed = False
    notes = []
    # If proper link already present, nothing to do
    if data.get('link_to') or data.get('name'):
        return changed, notes
    # Some fixtures use 'shortcut_name'
    shortcut_name = data.get('shortcut_name')
    if not shortcut_name:
        return changed, notes
    # Try to resolve
    found_type, found_name = find_existing(shortcut_name)
    if found_type:
        # apply
        data['type'] = found_type
        data['link_to'] = found_name
        data['name'] = found_name
        # set label if absent
        if not data.get('label'):
            data['label'] = shortcut_name
        # remove legacy key to avoid confusion
        if 'shortcut_name' in data:
            del data['shortcut_name']
        block['data'] = data
        changed = True
        notes.append({'note': 'resolved_shortcut', 'from': shortcut_name, 'to': {'type': found_type, 'name': found_name}})
    else:
        # leave but annotate unresolved
        data['unresolved_shortcut_name'] = shortcut_name
        if 'shortcut_name' in data:
            del data['shortcut_name']
        block['data'] = data
        notes.append({'note': 'unresolved_shortcut', 'name': shortcut_name})
        changed = True
    return changed, notes


def normalize_link_block(block):
    data = block.get('data') or {}
    changed = False
    notes = []
    if data.get('link_to') or data.get('name'):
        # check existence: if type present but missing target, try to resolve
        name = data.get('link_to') or data.get('name')
        t = data.get('type')
        if name and t:
            exists = frappe.db.exists(t, name)
            if not exists:
                # try to find alternate
                found_type, found_name = find_existing(name)
                if found_type:
                    data['type'] = found_type
                    data['link_to'] = found_name
                    data['name'] = found_name
                    block['data'] = data
                    changed = True
                    notes.append({'note': 'fixed_broken_link', 'from': {'type': t, 'name': name}, 'to': {'type': found_type, 'name': found_name}})
        return changed, notes
    # else no link_to/name present
    shortcut_name = data.get('shortcut_name') or data.get('name')
    if not shortcut_name:
        return changed, notes
    found_type, found_name = find_existing(shortcut_name)
    if found_type:
        data['type'] = found_type
        data['link_to'] = found_name
        data['name'] = found_name
        if 'shortcut_name' in data:
            del data['shortcut_name']
        if not data.get('label'):
            data['label'] = shortcut_name
        block['data'] = data
        changed = True
        notes.append({'note': 'resolved_link', 'from': shortcut_name, 'to': {'type': found_type, 'name': found_name}})
    else:
        data['unresolved_link_name'] = shortcut_name
        if 'shortcut_name' in data:
            del data['shortcut_name']
        block['data'] = data
        changed = True
        notes.append({'note': 'unresolved_link', 'name': shortcut_name})
    return changed, notes


def execute():
    # backup dir
    site = frappe.local.site
    backup_dir = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'auto_fix')
    os.makedirs(backup_dir, exist_ok=True)

    workspaces = frappe.get_all('Workspace', filters={"module": ["like", "%Sigma%"]}, fields=['name','content'])
    report = {'processed': 0, 'modified': []}
    for w in workspaces:
        name = w.get('name')
        content_raw = w.get('content') or ''
        report['processed'] += 1
        # backup
        backup_file = os.path.join(backup_dir, f"{name.replace(' ','_')}.json")
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content_raw)
        except Exception as e:
            frappe.log_error(message=f"Failed to backup workspace {name}: {e}")
        if not content_raw:
            continue
        try:
            content = json.loads(content_raw)
        except Exception as e:
            # invalid json; skip
            continue
        changed_any = False
        workspace_notes = []
        for i, block in enumerate(content):
            btype = block.get('type')
            if btype == 'shortcut':
                changed, notes = normalize_shortcut_block(block)
                if changed:
                    content[i] = block
                    changed_any = True
                    workspace_notes.extend(notes)
            elif btype == 'link':
                changed, notes = normalize_link_block(block)
                if changed:
                    content[i] = block
                    changed_any = True
                    workspace_notes.extend(notes)
            # cards left unchanged
        if changed_any:
            # write back
            try:
                ws = frappe.get_doc('Workspace', name)
                ws.content = json.dumps(content)
                ws.save()
                report['modified'].append({'workspace': name, 'notes': workspace_notes})
            except Exception as e:
                frappe.log_error(message=f"Failed to save workspace {name}: {e}")
    print(json.dumps(report))
